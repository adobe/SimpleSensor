"""
CamCollectionPoint
Events with face demographic data when a new face is detected and becomes the focal object.
Tracks faces as they move, sending only one event per fresh detection.
Sends reset event when no faces are detected for some time set in config.
"""
from . import moduleConfigLoader as configLoader
from simplesensor.shared.message import Message
from simplesensor.shared.moduleProcess import ModuleProcess
from .azureImagePredictor import AzureImagePredictor
from simplesensor.shared.threadsafeLogger import ThreadsafeLogger
from .multiTracker import MultiTracker
from distutils.version import LooseVersion, StrictVersion
from .version import __version__
# from multiprocessing import Process
from .idsWrapper import IdsWrapper
from datetime import datetime
from threading import Thread
from PIL import Image
import base64
import time
import sys
import cv2
import io
import os

class CollectionPoint(ModuleProcess):

    def __init__(self, baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue):
        """ Initialize new CamCollectionPoint instance.
        Setup queues, variables, configs, predictionEngines, constants and loggers.
        """

        # ModuleProcess.__init__(self, baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue)
        super().__init__(baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue)

        if not self.check_opencv_version("3.", cv2):
            print("OpenCV version {0} is not supported. Use 3.x for best results.".format(self.get_opencv_version()))

        # Queues
        self.outQueue = pOutBoundQueue #messages from this thread to the main process
        self.inQueue= pInBoundQueue
        self.loggingQueue = loggingQueue

        # Variables
        self.video = None
        self.needsReset = False
        self.needsResetMux = False
        self.alive = False

        # Configs
        self.moduleConfig = configLoader.load(self.loggingQueue, __name__) #Get the config for this module
        self.config = baseConfig

        # Prediction engine
        self.imagePredictionEngine = AzureImagePredictor(moduleConfig=self.moduleConfig, loggingQueue=loggingQueue)

        # Constants
        self._useIdsCamera = self.moduleConfig['UseIdsCamera']
        self._minFaceWidth = self.moduleConfig['MinFaceWidth']
        self._minFaceHeight = self.moduleConfig['MinFaceHeight']
        self._minNearestNeighbors = self.moduleConfig['MinNearestNeighbors']
        self._maximumPeople = self.moduleConfig['MaximumPeople']
        self._facePixelBuffer = self.moduleConfig['FacePixelBuffer']
        self._collectionThreshold = self.moduleConfig['CollectionThreshold']
        self._showVideoStream = self.moduleConfig['ShowVideoStream']
        self._sendBlobs = self.moduleConfig['SendBlobs']
        self._blobWidth = self.moduleConfig['BlobWidth']
        self._blobHeight = self.moduleConfig['BlobHeight']
        self._captureWidth = self.moduleConfig['CaptureWidth']
        self._captureHeight = self.moduleConfig['CaptureHeight']
        self._bitsPerPixel = self.moduleConfig['BitsPerPixel']
        self._resetEventTimer = self.moduleConfig['ResetEventTimer']
        self._collectionPointType = self.moduleConfig['CollectionPointType']
        self._collectionPointId = self.moduleConfig['CollectionPointId']

        # Logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

    def run(self):
        """ Main thread method, run when the thread's start() function is called.
        Controls flow of detected faces and the MultiTracker. 
        Determines when to send 'reset' events to clients and when to send 'found' events. 
        This function contains various comments along the way to help understand the flow.
        You can use this flow, extend it, or build your own.
        """
        if self.check_ss_version():
            #cant run with wrong version so we return early
            return False
        
        self.alive = True

        # Monitor inbound queue on own thread
        self.listen()

        self.initialize_camera()

        # Load the OpenCV Haar classifier to detect faces
        curdir = os.path.dirname(__file__)
        cascadePath = os.path.join(curdir, 'classifiers','haarcascades','haarcascade_frontalface_default.xml')
        faceCascade = cv2.CascadeClassifier(cascadePath)

        self.mmTracker = MultiTracker("KCF", self.moduleConfig, self.loggingQueue)

        # Setup timer for FPS calculations
        start = time.time()
        frameCounter = 1
        fps = 0

        # Start timer for collection events
        self.collectionStart = time.time()

        ok, frame = self.video.read()
        if not ok:
            self.logger.error('Cannot read video file')
            self.shutdown()

        while self.alive:
            ok, frame = self.video.read()
            if not ok:
                self.logger.error('Error while reading frame')
                break

            # Image alts
            if self._useIdsCamera:
                grayFrame = frame.copy()
                outputImage = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                outputImage = frame.copy()
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect faces
            faces = faceCascade.detectMultiScale(
                grayFrame,
                scaleFactor = 1.1,
                minNeighbors = self._minNearestNeighbors,
                minSize = (self._minFaceWidth, self._minFaceHeight)
            )

            # If no faces in frame, clear tracker and start reset timer
            if len(faces) == 0 or self.mmTracker.length() > self._maximumPeople:
                self.mmTracker.clear()
                self.start_reset()

            # If there are trackers, update
            if self.mmTracker.length() > 0:
                ok, bboxes, failed = self.mmTracker.update(outputImage)
                if failed:
                    self.logger.error('Update trackers failed on: %s' % ''.join(str(s) for s in failed))

            for (x, y, w, h) in faces:
                # If faces are detected, engagement exists, do not reset
                self.needsReset = False

                # Optionally add buffer to face, can improve tracking/classification accuracy
                if self._facePixelBuffer > 0:
                    (x, y, w, h) = self.apply_face_buffer(x, y, w, h, self._facePixelBuffer, outputImage.shape)

                # Get region of interest
                roi_gray = grayFrame[y:y+h, x:x+w]
                roi_color = outputImage[y:y+h, x:x+w]

                # If the tracker is valid and doesn't already exist, add it
                if self.valid_tracker(x, y, w, h):
                    self.logger.info('Adding tracker')
                    ok = self.mmTracker.add(bbox={'x':x,'y':y,'w':w,'h':h}, frame=outputImage)

                # Draw box around face
                if self._showVideoStream:
                    cv2.rectangle(outputImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # If the time since last collection is more than the set threshold
            if not self.needsReset or (time.time() - self.collectionStart > self._collectionThreshold):
                # Check if the focal face has changed
                check, face = self.mmTracker.check_focus()
                if check:
                    predictions = self.get_predictions(grayFrame, face)
                    if predictions:
                        self.send_message(topic="update",
                                        data={
                                            'detectedTime': datetime.now().isoformat('T'),
                                            'predictions': predictions
                                        })
                    
            frameCounter += 1
            elapsed = time.time() - start
            fps = frameCounter/max(abs(elapsed),0.0001)
            if frameCounter > sys.maxsize:
                start = time.time()
                frameCounter = 1

            if self._showVideoStream:
                cv2.putText(outputImage, "%s FPS" % fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.imshow("Faces found", outputImage)
                cv2.waitKey(1)

            if self._sendBlobs and frameCounter%6==0:
                self.send_message(topic="blob", 
                                data={
                                    'imageArr': cv2.resize(outputImage, (self._blobWidth, self._blobHeight)) , 
                                    'time': datetime.now().isoformat('T')
                                })
                # self.putCPMessage(data = {
                #                     'imageArr': cv2.resize(outputImage, (self._blobWidth, self._blobHeight)) , 
                #                     'time': datetime.now().isoformat('T')
                #                     }, 
                #                   type="blob")

    def check_ss_version(self):
        #check for min version met
        self.logger.info('Module version %s' %(__version__))
        if LooseVersion(self.config['ss_version']) < LooseVersion(self.moduleConfig['MinSimpleSensorVersion']):
            self.logger.error('This module requires a min SimpleSensor %s version.  This instance is running version %s' %(self.moduleConfig['MinSimpleSensorVersion'],self.config['ss_version']))
            return False
        return True

    def get_predictions(self, grayFrame, face):
        """ Send face to predictionEngine as JPEG.
        Return predictions array or false if no face is found. 
        """

        faceArr = grayFrame[int(face[1]):int(face[1]+face[3]), int(face[0]):int(face[0]+face[2])]
        img = Image.fromarray(faceArr)
        buff = io.BytesIO()
        img.save(buff, format="JPEG")

        predictions = self.imagePredictionEngine.get_prediction(buff.getvalue())
        if 'error' in predictions:
            return False
        return predictions
    
    def valid_tracker(self, x, y, w, h):
        """ Check if the coordinates are a newly detected face or already present in MultiTracker.
        Only accepts new tracker candidates every _collectionThreshold seconds.
        Return true if the object in those coordinates should be tracked.
        """
        if not self.needsReset or (time.time() - self.collectionStart > self._collectionThreshold):
            if (self.mmTracker.length() == 0 or not self.mmTracker.contains(bbox={'x':x, 'y':y, 'w':w, 'h':h})):
                return True
        return False

    def start_reset(self):
        """Start a timer from reset event.
        If timer completes and the reset event should still be sent, send it.
        """
        if self.needsResetMux:
            self.needsReset = True
            self.needsResetMux = False
            self.resetStart = time.time()

        if self.needsReset:
            if (time.time() - self.resetStart) > 10: # 10 seconds after last face detected
                self.send_message(data=None, type="reset")
                self.needsReset = False

    def apply_face_buffer(self, x, y, w, h, b, shape):
        x = x-b if x-b >= 0 else 0
        y = y-b if y-b >= 0 else 0
        w = w+b if w+b <= shape[1] else shape[1]
        h = h+b if h+b <= shape[0] else shape[0]
        return (x, y, w, h)

    def initialize_camera(self):
        # Using IDS camera
        if self._useIdsCamera:
            self.logger.info ("Using IDS Camera")
            self.wrapper = IdsWrapper(self.loggingQueue, self.moduleConfig)
            if not( self.wrapper.isOpened()):
                self.wrapper.open()
            self.wrapper.set('py_width', self._captureWidth)
            self.wrapper.set('py_height', self._captureHeight)
            self.wrapper.set('py_bitspixel', self._bitsPerPixel)

            # Convert values to ctypes, prep memory locations
            self.wrapper.set_c_types()

            self.wrapper.allocate_image_memory()
            self.wrapper.set_image_memory()
            self.wrapper.begin_capture()
            self.wrapper.init_image_data()

            # Start video update thread
            self.video = self.wrapper.start()

        # Not using IDS camera
        else:
            # open first webcam available
            self.video = cv2.VideoCapture(0)
            if not( self.video.isOpened()):
                self.video.open()

            #set the resolution from config
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self._captureWidth)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self._captureHeight)

    def processQueue(self):
        self.logger.info("Starting to watch collection point inbound message queue")
        while self.alive:
            if (self.inQueue.empty() == False):
                self.logger.info("Queue size is %s" % self.inQueue.qsize())
                try:
                    message = self.inQueue.get(block=False,timeout=1)
                    if message is not None:
                        if message == "SHUTDOWN":
                            self.logger.info("SHUTDOWN command handled on %s" % __name__)
                            self.shutdown()
                        else:
                            self.handleMessage(message)
                except Exception as e:
                    self.logger.error("Unable to read queue, error: %s " %e)
                    self.shutdown()
                self.logger.info("Queue size is %s after" % self.inQueue.qsize())
            else:
                time.sleep(.25)

    def handle_message(self, message):
        if message._topic == 'open-stream':
            self._sendBlobs = True
        elif message._topic == 'close-stream':
            self._sendBlobs = False

    def send_message(self, topic, data=None):
        message = self.build_message(topic, data)
        self.put_message(message)

    def build_message(self, topic, data):
        if topic == "reset":
            # Send reset message
            self.logger.info('Sending reset message')
            msg = Message(
                topic='reset',
                sender_id=self._collectionPointId,
                sender_type=self._collectionPointType,
                extended_data=None,
                recipients='communication_modules'
            )
            return msg

        elif topic == "update":
            # Reset collection start and now needs needs reset
            collectionStart = time.time()
            self.needsResetMux = True

            self.logger.info('Sending found message')
            msg = Message(
                topic='face',
                sender_id=self._collectionPointId,
                sender_type=self._collectionPointType,
                extended_data=data['predictions'],
                recipients='communication_modules',
                timestamp=data['detectedTime'],
            )
            return msg

        elif topic == "blob":
            # Get numpy array as bytes
            img = Image.fromarray(data['imageArr'])
            buff = io.BytesIO()
            img.save(buff, format="JPEG")
            s = base64.b64encode(buff.getvalue()).decode("utf-8")

            eventExtraData = {}
            eventExtraData['imageData'] = s
            eventExtraData['dataType'] = 'image/jpeg'

            msg = Message(
                topic='blob',
                sender_id=self._collectionPointId,
                sender_type=self._collectionPointType,
                extended_data=eventExtraData,
                recipients='communication_modules'
            )
            return msg
       
    # def putCPMessage(self, data, type):
    #     if type == "reset":
    #         # Send reset message
    #         self.logger.info('Sending reset message')
    #         msg = CollectionPointEvent(
    #             self._collectionPointId,
    #             self._collectionPointType,
    #             'Reset mBox',
    #             None)
    #         self.outQueue.put(msg)

    #     elif type == "update":
    #         # Reset collection start and now needs needs reset
    #         collectionStart = time.time()
    #         self.needsResetMux = True

    #         self.logger.info('Sending found message')
    #         msg = CollectionPointEvent(
    #             self._collectionPointId,
    #             self._collectionPointType,
    #             'Found face',
    #             data['predictions']
    #         )
    #         self.outQueue.put(msg)

    #     elif type == "blob":
    #         # Get numpy array as bytes
    #         img = Image.fromarray(data['imageArr'])
    #         buff = io.BytesIO()
    #         img.save(buff, format="JPEG")
    #         s = base64.b64encode(buff.getvalue()).decode("utf-8")

    #         eventExtraData = {}
    #         eventExtraData['imageData'] = s
    #         eventExtraData['dataType'] = 'image/jpeg'

    #         # Send found message 
    #         # self.logger.info('Sending blob message')
    #         msg = CollectionPointEvent(
    #             self._collectionPointId,
    #             self._collectionPointType,
    #             'blob',
    #             eventExtraData,
    #             False
    #         )
    #         self.outQueue.put(msg)

    def shutdown(self):
        self.alive = False
        self.logger.info("Shutting down")
        if self._useIdsCamera and self.wrapper.is_open():
            self.wrapper.exit()
        cv2.destroyAllWindows()
        self.threadProcessQueue.join()
        time.sleep(1)
        self.exit = True

    #Custom methods for demo
    def get_opencv_version(self):
        import cv2 as lib
        return lib.__version__

    def check_opencv_version(self,major, lib=None):
        # if the supplied library is None, import OpenCV
        if lib is None:
            import cv2 as lib

        # return whether or not the current OpenCV version matches the
        # major version number
        return lib.__version__.startswith(major)

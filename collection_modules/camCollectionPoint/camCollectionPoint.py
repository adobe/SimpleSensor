import cv2
from collectionPointEvent import CollectionPointEvent
import time
from datetime import datetime
import sys
import numpy as np
from idsWrapper import IdsWrapper
from threadsafeLogger import ThreadsafeLogger
from threading import Thread
from multiprocessing import Process
import io, base64
import os
from PIL import Image
from multiTracker import MultiTracker
import camConfigLoader
from azureImagePrediction import AzureImagePrediction

class CamCollectionPoint(Process):

    def __init__(self, baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue):
        """ Initialize new CamCollectionPoint instance.
        Setup queues, variables, configs, predictionEngines, constants and loggers.
        """

        super(CamCollectionPoint, self).__init__()

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
        self.alive = True

        # Configs
        self.moduleConfig = camConfigLoader.load(self.loggingQueue) #Get the config for this module
        self.config = baseConfig

        # Prediction engine
        self.imagePredictionEngine = AzureImagePrediction(moduleConfig=self.moduleConfig, loggingQueue=loggingQueue)

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

        self._collectionPointType = self.config['CollectionPointType']
        self._collectionPointId = self.config['CollectionPointId']

        # Logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

    def run(self):
        """ Main thread method, run when the thread's start() function is called.
        Controls flow of detected faces and the MultiTracker. 
        Determines when to send 'reset' events to clients and when to send 'found' events. 
        This function contains various comments along the way to help understand the flow.
        You can use this flow, extend it, or build your own.
        """

        # Monitor inbound queue on own thread
        self.threadProcessQueue = Thread(target=self.processQueue)
        self.threadProcessQueue.setDaemon(True)
        self.threadProcessQueue.start()

        self.initializeCamera()

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
                self.startReset()

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
                    (x, y, w, h) = self.applyFaceBuffer(x, y, w, h, self._facePixelBuffer, outputImage.shape)

                # Get region of interest
                roi_gray = grayFrame[y:y+h, x:x+w]
                roi_color = outputImage[y:y+h, x:x+w]

                # If the tracker is valid and doesn't already exist, add it
                if self.validTracker(x, y, w, h):
                    self.logger.info('Adding tracker')
                    ok = self.mmTracker.add(bbox={'x':x,'y':y,'w':w,'h':h}, frame=outputImage)

                # Draw box around face
                if self._showVideoStream:
                    cv2.rectangle(outputImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # If the time since last collection is more than the set threshold
            if not self.needsReset or (time.time() - self.collectionStart > self._collectionThreshold):
                # Check if the focal face has changed
                check, face = self.mmTracker.checkFocus()
                if check:
                    predictions = self.getPredictions(grayFrame, face)
                    if predictions:
                        self.putCPMessage(data = {
                            'detectedTime': datetime.now().isoformat('T'),
                            'predictions': predictions
                            }, 
                            type="update")
                    
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
                self.putCPMessage(data = {
                                    'imageArr': cv2.resize(outputImage, (self._blobWidth, self._blobHeight)) , 
                                    'time': datetime.now().isoformat('T')
                                    }, 
                                  type="blob")

    def getPredictions(self, grayFrame, face):
        """ Send face to predictionEngine as JPEG.
        Return predictions array or false if no face is found. 
        """

        faceArr = grayFrame[int(face[1]):int(face[1]+face[3]), int(face[0]):int(face[0]+face[2])]
        img = Image.fromarray(faceArr)
        buff = io.BytesIO()
        img.save(buff, format="JPEG")

        try:
            predictions = self.imagePredictionEngine.getPrediction(buff.getvalue())
        except Exception as e:
            predictions = False

        return predictions
    
    def validTracker(self, x, y, w, h):
        """ Check if the coordinates are a newly detected face or already present in MultiTracker.
        Only accepts new tracker candidates every _collectionThreshold seconds.
        Return true if the object in those coordinates should be tracked.
        """
        if not self.needsReset or (time.time() - self.collectionStart > self._collectionThreshold):
            if (self.mmTracker.length() == 0 or not self.mmTracker.contains(bbox={'x':x, 'y':y, 'w':w, 'h':h})):
                return True
        return False

    def startReset(self):
        """Start a timer from reset event.
        If timer completes and the reset event should still be sent, send it.
        """
        if self.needsResetMux:
            self.needsReset = True
            self.needsResetMux = False
            self.resetStart = time.time()

        if self.needsReset:
            if (time.time() - self.resetStart) > 10: # 10 seconds after last face detected
                self.putCPMessage(data=None, type="reset")
                self.needsReset = False

    def applyFaceBuffer(self, x, y, w, h, b, shape):
        x = x-b if x-b >= 0 else 0
        y = y-b if y-b >= 0 else 0
        w = w+b if w+b <= shape[1] else shape[1]
        h = h+b if h+b <= shape[0] else shape[0]
        return (x, y, w, h)

    def initializeCamera(self):
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
            self.wrapper.setCTypes()

            self.wrapper.allocateImageMemory()
            self.wrapper.setImageMemory()
            self.wrapper.beginCapture()
            self.wrapper.initImageData()

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

    def handleMessage(self, message):
        if message._topic == 'open-stream':
            self._sendBlobs = True
        elif message._topic == 'close-stream':
            self._sendBlobs = False
       
    def putCPMessage(self, data, type):
        if type == "reset":
            # Send reset message
            self.logger.info('Sending reset message')
            msg = CollectionPointEvent(
                self._collectionPointId,
                self._collectionPointType,
                'Reset mBox',
                None)
            self.outQueue.put(msg)

        elif type == "update":
            # Reset collection start and now needs needs reset
            collectionStart = time.time()
            self.needsResetMux = True

            self.logger.info('Sending found message')
            msg = CollectionPointEvent(
                self._collectionPointId,
                self._collectionPointType,
                'Found face',
                data['predictions']
            )
            self.outQueue.put(msg)

        elif type == "blob":
            # Get numpy array as bytes
            img = Image.fromarray(data['imageArr'])
            buff = io.BytesIO()
            img.save(buff, format="JPEG")
            s = base64.b64encode(buff.getvalue()).decode("utf-8")

            eventExtraData = {}
            eventExtraData['imageData'] = s
            eventExtraData['dataType'] = 'image/jpeg'

            # Send found message 
            # self.logger.info('Sending blob message')
            msg = CollectionPointEvent(
                self._collectionPointId,
                self._collectionPointType,
                'blob',
                eventExtraData,
                False
            )
            self.outQueue.put(msg)

    def shutdown(self):
        self.alive = False
        self.logger.info("Shutting down")
        # self.outQueue.put("SHUTDOWN")
        if self._useIdsCamera and self.wrapper.isOpened():
            self.wrapper.exit()
        cv2.destroyAllWindows()
        # self.threadProcessQueue.join()
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

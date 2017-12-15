"""
Custom sensor logic
author: DaViD bEnGe
date: 6/9/2017

"""
import cv2
from collectionPointEvent import CollectionPointEvent
import time
import sys
import logging
from threadsafeLogger import ThreadsafeLogger
from threading import Thread

class CollectionPoint(Thread):
    """ Sample class to show basic structure of collecting data and passing it to communication channels """

    def __init__(self,baseConfig,pOutBoundEventQueue, pInBoundEventQueue, loggingQueue):
        # Standard initialization that most collection points would do
        super(CollectionPoint, self).__init__()
        self.alive = True
        self.config = baseConfig
        self.outBoundEventQueue = pOutBoundEventQueue
        self.inBoundEventQueue = pInBoundEventQueue
        self.logger = ThreadsafeLogger(loggingQueue,__name__)

        # Initialize collection point specific variables
        self.video = None

        # Set constants from config
        self._collectionPointId = self.config['CollectionPointId']
        self._collectionPointType = self.config['CollectionPointType']
        self._testMode = self.config['TestMode']


        if not self.check_opencv_version("3.",cv2):
            self.logger.critical("open CV is the wrong version {0}.  We require version 3.x".format(self.get_opencv_version()))

    def run(self):
        """ Sample run function for a collection point class.
        Starting point for when the thread is start()'d from main.py
        Extend this to create your own, or understand how to perform specific actions.
        """

        # Start a thread to monitor the inbound queue
        self.threadProcessQueue = Thread(target=self.processQueue)
        self.threadProcessQueue.setDaemon(True)
        self.threadProcessQueue.start()

        # Load the OpenCV classifier to detect faces
        faceCascade = cv2.CascadeClassifier('./classifiers/haarcascades/haarcascade_frontalface_default.xml')

        tracker = cv2.Tracker_create("KCF")

        # Get first camera connected
        video = cv2.VideoCapture(0)
        if not video.isOpened():
            video.open()
        
        # Set resolution of capture
        video.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ok, frame = video.read()
        if not ok:
            self.logger.error('Cannot read video file')
            self.shutdown()

        while self.alive:
            # Read a new frame
            ok, frame = video.read()
            if not ok:
                self.logger.error('Cannot read video file')
                break

            # Convert to grayscale
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Copy the frame to allow manipulation
            outputImage = frame.copy()

            # Detect faces
            faces = faceCascade.detectMultiScale(
                grayFrame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(5, 5)
            )

            self.logger.info("Found " + str(len(faces)) + " faces")

            # Draw a rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(outputImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if self._testMode:
                if len(faces) > 0:
                    msg = CollectionPointEvent(self._collectionPointId,self._collectionPointType,('Found {0} faces'.format(len(faces))))
                    self.outBoundEventQueue.put(msg)

            # Display the image
            cv2.imshow("Faces found", outputImage)

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27: #esc key
                self.shutdown()
                break

        video.release()

    def shutdown(self):
        self.logger.info("Shutting down collection point")
        cv2.destroyAllWindows()
        self.threadProcessQueue.join()
        self.alive = False
        time.sleep(1)
        self.exit = True

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



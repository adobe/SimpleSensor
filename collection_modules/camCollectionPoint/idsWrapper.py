"""
IDS camera DLL wrapper
author: MaX EdeLL
date: 13/37/2017
"""

from ctypes import *
from platform import architecture
import numpy as np
from idsConsts import *
from threadsafeLogger import ThreadsafeLogger
from threading import Thread
import time

class IdsWrapper(object):
    def __init__(self, loggingQueue, moduleConfig):
        """ Create a new IdsWrapper instance. 
        IdsWrapper uses the Windows IDS DLL, wraps C calls in Python.
        Tested using the IDS XS 2.0 USB camera
        """

        self.config = moduleConfig
        self.isOpen = False
        self.width = 0
        self.height = 0
        self.bitspixels = 0
        self.py_width = 0
        self.py_height = 0
        self.py_bitspixel = 0
        self.cam = None
        self.pcImgMem = c_char_p() #create placeholder for image memory
        self.pid=c_int()

        # Setup logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)
        
        # Load the correct dll
        try:
            if architecture()[0] == '64bit':
                self.logger.info('Using IDS camera with 64-bit architecture')
                self.uEyeDll = cdll.LoadLibrary("C:/Windows/System32/uEye_api_64.dll")
            else:
                self.logger.info('Using IDS camera with 32-bit architecture')
                self.uEyeDll = cdll.LoadLibrary("C:/Windows/System32/uEye_api.dll")
        except Exception as e:
            self.logger.error('Failed to load IDS DLL: %s . Are you sure you are using an IDS camera?'%e)

    def isOpened(self):
        """ Return camera open status"""
        return self.isOpen
    
    def set(self, key, value):
        """ Set the py_width, py_height or py_bitspixel properties """
        if key == 'py_width':
            self.py_width = value
        elif key == 'py_height':
            self.py_height = value
        else:
            self.py_bitspixel = value
    
    def allocateImageMemory(self):
        """ Wrapped call to allocate image memory """
        ret=self.uEyeDll.is_AllocImageMem(self.cam, self.width, self.height, self.bitspixel, byref(self.pcImgMem), byref(self.pid))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully allocated image memory")
        else:
            self.logger.error('Memory allocation failed, no camera with value ' + str(self.cam.value) + ' | Error code: ' + str(ret))
            return

    def setImageMemory(self):
        """ Wrapped call to set image memory """
        ret = self.uEyeDll.is_SetImageMem(self.cam, self.pcImgMem, self.pid)
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set image memory")
        else:
            self.logger.error("Failed to set image memory; error code: " + str(ret))
            return

    def beginCapture(self):
        """ Wrapped call to begin capture """
        ret = self.uEyeDll.is_CaptureVideo (self.cam, c_long(IS_DONT_WAIT))  
        if ret == IS_SUCCESS:
            self.logger.info("Successfully began video capture")
        else:
            self.logger.error("Failed to begin video capture; error code: " + str(ret))
            return

    def initImageData(self):
        """ Initialize the ImageData numpy array """
        self.ImageData = np.ones((self.py_height,self.py_width),dtype=np.uint8)

    def setCTypes(self):
        """ Set C Types for width, height, and bitspixel properties"""
        self.width = c_int(self.py_width)
        self.height = c_int(self.py_height) 
        self.bitspixel = c_int(self.py_bitspixel)

    def start(self):
        """ Start capturing frames on another thread as a daemon """
        self.updateThread = Thread(target=self.update)
        self.updateThread.setDaemon(True)
        self.updateThread.start()
        return self

    def initializeCamera(self):
        """ Wrapped call to initialize camera """
        ret = self.uEyeDll.is_InitCamera(byref(self.cam), self.hWnd)
        if ret == IS_SUCCESS:
            self.logger.info("Successfully initialized camera")
        else:
            self.logger.error("Failed to initialize camera; error code: " + str(ret))
            return

    def enableAutoExit(self):
        """ Wrapped call to allow allocated memory to be dropped on exit. """
        ret = self.uEyeDll.is_EnableAutoExit (self.cam, c_uint(1))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully enabled auto exit")
        else:
            self.logger.error("Failed to enable auto exit; error code: " + str(ret))
            return

    def setDisplayMode(self):
        """ Wrapped call to set display mode to DIB """
        ret = self.uEyeDll.is_SetDisplayMode (self.cam, c_int(IS_SET_DM_DIB))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set camera to DIB mode")
        else:
            self.logger.error("Failed to set camera mode; error code: " + str(ret))
            return

    def setColorMode(self):
        """ Wrapped call to set camera color capture mode """
        ret = self.uEyeDll.is_SetColorMode(self.cam, c_int(IS_CM_SENSOR_RAW8))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set color mode")
        else:
            self.logger.error("Failed to set color mode; error code: " + str(ret))
            return
    
    def setCompressionFactor(self):
        """ Wrapped call to set image compression factor.
        Required for long USB lengths when bandwidth is constrained, lowers quality.
        """
        ret = self.uEyeDll.is_DeviceFeature(self.cam, IS_DEVICE_FEATURE_CMD_SET_JPEG_COMPRESSION, byref(c_int(self.config['CompressionFactor'])), c_uint(INT_BYTE_SIZE));
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set compression factor to: " + str(self.config['CompressionFactor']))
        else:
            self.logger.error("Failed to set compression factor; error code: " + str(ret))
            return

    def setPixelClock(self):
        """ Wrapped call to set pixel clock.
        Required for long USB lengths when bandwidth is constrained
        Lowers frame rate and increases motion blur. 
        """
        ret = self.uEyeDll.is_PixelClock(self.cam, IS_PIXELCLOCK_CMD_SET, byref(c_uint(self.config['PixelClock'])), c_uint(INT_BYTE_SIZE));
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set pixel clock to: " + str(self.config['PixelClock']))
        else:
            self.logger.error("Failed to set pixel clock; error code: " + str(ret))
            return

    def setTrigger(self):
        """ Wrapped call to set trigger type to software trigger. """
        ret = self.uEyeDll.is_SetExternalTrigger(self.cam, c_uint(IS_SET_TRIGGER_SOFTWARE))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set software trigger")
        else:
            self.logger.error("Failed to set software trigger; error code: " + str(ret))
            return

    def setImageProfile(self):
        """ Wrapped call to set image format.
        Sets resolution of the capture to UXGA. More modes available in idsConsts.py.
        """
        ret = self.uEyeDll.is_ImageFormat(self.cam, c_uint(IMGFRMT_CMD_SET_FORMAT), byref(c_int(UXGA)), c_uint(INT_BYTE_SIZE))
        if ret == IS_SUCCESS:
            self.logger.info("Successfully set camera image profile")
        else:
            self.logger.error("Failed to set camera image profile; error code: " + str(ret))
            return

    def open(self):
        """ Open connection to IDS camera, set various modes. """
        self.cam = c_uint32(0)
        self.hWnd = c_voidp()
        
        self.initializeCamera()
        self.enableAutoExit()
        self.setDisplayMode()
        self.setColorMode()
        self.setCompressionFactor()
        self.setPixelClock()
        self.setTrigger()
        self.setImageProfile()

        # Declare video open
        self.isOpen = True

        self.logger.info('Successfully opened camera')
    
    def update(self):
        """ Loop to update frames and copy to ImageData variable. """
        while True:
            if not self.isOpen:
                return
            self.uEyeDll.is_CopyImageMem (self.cam, self.pcImgMem, self.pid, self.ImageData.ctypes.data_as(c_char_p))
    
    def read(self):
        """ Read frame currently available in ImageData variable. """
        try:
            return True, self.ImageData
        except Exception as e:
            self.logger.error('Error getting image data: %r'% e)
            return False, None


    def exit(self):
        """ Close camera down, release memory. """
        self.uEyeDll.is_ExitCamera(self.cam)
        self.isOpen = False
        self.logger.info('Closing wrapper and camera')
        return
            
#################
 #  Copyright 2018 Adobe Systems Incorporated
 #
 #  Licensed under the Apache License, Version 2.0 (the "License");
 #  you may not use this file except in compliance with the License.
 #  You may obtain a copy of the License at
 #
 #      http://www.apache.org/licenses/LICENSE-2.0
 #
 #  Unless required by applicable law or agreed to in writing, software
 #  distributed under the License is distributed on an "AS IS" BASIS,
 #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 #  See the License for the specific language governing permissions and
 #  limitations under the License.
 #
 #  not my circus, not my monkeys
 #
 #  Created by: David bEnGe at some time in 2016
 #  Entry point for the BTLE sensors used in the Adobe SJ CEC entry experiance
 #  its basically a reverse BTLE scanner where the area scans to see what tags are in the space.  Each visitor to our CEC gets a badge with 
 #  a small btle beacon that transmits a uuid. 
 #
#################

import ConfigParser
import os.path
import sys
import logging
import logging.config
import pprint
import json
import time
sys.path.append('./btle')
sys.path.append('./libs')
sys.path.append('./btle/device/bluegiga')
sys.path.append('./btle/device/iogear')
from eventManager import EventManager
from threading import Thread
from Queue import Queue
from btle.device.bluegiga.btleThread import BlueGigaBtleCollectionPointThread
#from btle.device.iogear.btleThread import IoGearBtleCollectionPointThread
from registeredClientRegistry import *
from repeatedTimer import RepeatedTimer
from threadsafeLogger import ThreadsafeLogger
from threading import Thread
import configLoader

class BtleCollectionPoint(Thread):

    def __init__(self, baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue):
        """ Initialize new CamCollectionPoint instance.
        Setup queues, variables, configs, constants and loggers.
        """
        super(BtleCollectionPoint, self).__init__()

         # Queues
        self.outQueue = pOutBoundQueue #messages from this thread to the main process
        self.inQueue= pInBoundQueue
        self.loggingQueue = loggingQueue
        self.queueBLE = Queue()

        # Configs
        self.moduleConfig = configLoader.load(self.loggingQueue) #Get the config for this module
        self.config = baseConfig

        # Logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

        # Variables
        self.registeredClientRegistry = RegisteredClientRegistry(self.moduleConfig)
        self.eventManager = EventManager(self.moduleConfig,pOutBoundQueue,self.registeredClientRegistry)
        self.alive = True
        self.btleThread = None
        self.BLEThread = None
        self.repeatTimerSweepClients = None

        ###Pausing Startup to wait for things to start after a system restart
        self.logger.info("Pausing execution 15 seconds waiting for other system services to start")
        time.sleep(15)
        self.logger.info("Done with our nap.  Time to start looking for clients")

        #########  setup global client registry start #########
        self.registeredClientRegistry = RegisteredClientRegistry(self.moduleConfig)
        #########  setup global client registry end #########

        self.btleThread = BlueGigaBtleCollectionPointThread(self.queueBLE,self.moduleConfig)
        self.BLEThread = Thread(target=self.btleThread.bleDetect, args=(__name__,10))
        self.BLEThread.daemon = True
        self.BLEThread.start()

        #Setup repeat task to run the sweep every X interval
        self.repeatTimerSweepClients = RepeatedTimer((self.moduleConfig['AbandonedClientCleanupIntervalInMilliseconds']/1000), self.registeredClientRegistry.sweepOldClients)

        #read the queue
        try:
            while True:
                if (self.queueBLE.empty() == False):
                    result = self.queueBLE.get(False)
                    self.handleBtleClientEvents(result)
        except KeyboardInterrupt:
            self.logger.info("attempting to close threads.")
            self.repeatTimerSweepClients.stop()
            self.btleThread.stop()
            self.logger.info("threads successfully closed")

    #handle btle reads
    def handleBtleClientEvents(self,dectectedClients):
        #logger.debug("doing handleBtleClientEvents")
        for client in dectectedClients:
            self.logger.debug("--- Found client ---")
            self.logger.debug(vars(client))
            self.logger.debug("--- Found client end ---")
            self.eventManager.registerDetectedClient(client)

    def shutdown(self):
        self.logger.info("Shutting down btle collection point")
        self.threadProcessQueue.join()
        self.alive = False
        time.sleep(1)
        self.exit = True

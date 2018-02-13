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
 #  Entry point for the BTLE sensors used in the Adobe SJ CEC entry experience
 #  its basically a reverse BTLE scanner where the area scans to see what tags are in the space.  Each visitor to our CEC gets a badge with 
 #  a small btle beacon that transmits a uuid. 
 #
#################

__author__ = "David Benge"
__license__ = "Apache License, Version 2.0"
__version__ = "2018-02-08"
__email__ = "dbenge@adobe.com"

import sys
import json
import time
import multiprocessing as mp
sys.path.append('./collection_modules/btleCollectionPoint/btle')
sys.path.append('./collection_modules/btleCollectionPoint/libs')
sys.path.append('./collection_modules/btleCollectionPoint/btle/device/bluegiga')
sys.path.append('./collection_modules/btleCollectionPoint/btle/device/iogear')
from eventManager import EventManager
from btle.device.bluegiga.btleThread import BlueGigaBtleCollectionPointThread
# import registeredClientRegistry
from registeredClientRegistry import RegisteredClientRegistry
from repeatedTimer import RepeatedTimer
from threading import Thread
from threadsafeLogger import ThreadsafeLogger
import btleConfigLoader as configLoader

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
        self.queueBLE = mp.Queue()
        # Configs
        self.moduleConfig = configLoader.load(self.loggingQueue) #Get the config for this module
        self.config = baseConfig

        # Logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)
        # Variables
        self.registeredClientRegistry = RegisteredClientRegistry(self.moduleConfig, self.loggingQueue)
        self.eventManager = EventManager(self.moduleConfig, pOutBoundQueue, self.registeredClientRegistry, self.loggingQueue)
        self.alive = True
        self.btleThread = None
        self.BLEThread = None
        self.repeatTimerSweepClients = None

    # main start method
    def run(self):
        ###Pausing Startup to wait for things to start after a system restart
        self.logger.info("Pausing execution 15 seconds waiting for other system services to start")
        time.sleep(15)
        self.logger.info("Done with our nap.  Time to start looking for clients")

        #########  setup global client registry start #########
        # self.registeredClientRegistry = RegisteredClientRegistry(self.moduleConfig, self.loggingQueue)
        #########  setup global client registry end #########

        self.btleThread = BlueGigaBtleCollectionPointThread(self.queueBLE, self.moduleConfig, self.loggingQueue)
        self.BLEThread = Thread(target=self.btleThread.bleDetect, args=(__name__,10))
        self.BLEThread.daemon = True
        self.BLEThread.start()

        #Setup repeat task to run the sweep every X interval
        self.repeatTimerSweepClients = RepeatedTimer((self.moduleConfig['AbandonedClientCleanupIntervalInMilliseconds']/1000), self.registeredClientRegistry.sweepOldClients)

        # Process queue from main thread for shutdown messages
        self.threadProcessQueue = Thread(target=self.processQueue)
        self.threadProcessQueue.setDaemon(True)
        self.threadProcessQueue.start()
        #read the queue
        try:
            while self.alive:
                if (self.queueBLE.empty() == False):
                    result = self.queueBLE.get(False)
                    self.__handleBtleClientEvents(result)
        except KeyboardInterrupt:
            self.logger.info("Attempting to close threads.")
            self.repeatTimerSweepClients.stop()
            self.btleThread.stop()
            self.logger.info("Threads successfully closed")

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
                            self.sendOutMessage(message)
                except Exception as e:
                    self.logger.error("Unable to read queue, error: %s " %e)
                    self.shutdown()
                self.logger.info("Queue size is %s after" % self.inQueue.qsize())
            else:
                time.sleep(.25)

    #handle btle reads
    def __handleBtleClientEvents(self,dectectedClients):
        #logger.debug("doing handleBtleClientEvents")
        for client in dectectedClients:
            self.logger.debug("--- Found client ---")
            self.logger.debug(vars(client))
            self.logger.debug("--- Found client end ---")
            self.eventManager.registerDetectedClient(client)

    def shutdown(self):
        self.logger.info("Shutting down")
        # self.threadProcessQueue.join()
        self.alive = False
        time.sleep(1)
        self.exit = True

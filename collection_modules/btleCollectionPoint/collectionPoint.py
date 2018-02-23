import sys
import json
import time
import multiprocessing as mp
sys.path.append('./collection_modules/btleCollectionPoint/libs')
sys.path.append('./collection_modules/btleCollectionPoint/devices/bluegiga')
from eventManager import EventManager
from devices.bluegiga.btleThread import BlueGigaBtleCollectionPointThread
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
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

         # Queues
        self.outQueue = pOutBoundQueue # Messages from this thread to the main process
        self.inQueue = pInBoundQueue
        self.queueBLE = mp.Queue()

        # Configs
        self.moduleConfig = configLoader.load(self.loggingQueue)
        self.config = baseConfig

        # Variables and objects
        self.registeredClientRegistry = RegisteredClientRegistry(self.moduleConfig, self.loggingQueue)
        self.eventManager = EventManager(self.moduleConfig, pOutBoundQueue, self.registeredClientRegistry, self.loggingQueue)
        self.alive = True
        self.btleThread = None
        self.BLEThread = None
        self.repeatTimerSweepClients = None

        # Constants
        self._cleanupInterval = self.moduleConfig['AbandonedClientCleanupInterval']

    def run(self):
        ###Pausing Startup to wait for things to start after a system restart
        self.logger.info("Pausing execution 15 seconds waiting for other system services to start")
        time.sleep(15)
        self.logger.info("Done with our nap.  Time to start looking for clients")

        self.btleThread = BlueGigaBtleCollectionPointThread(self.queueBLE, self.moduleConfig, self.loggingQueue)
        self.BLEThread = Thread(target=self.btleThread.bleDetect, args=(__name__,10))
        self.BLEThread.daemon = True
        self.BLEThread.start()

        # Setup repeat task to run the sweep every X interval
        self.repeatTimerSweepClients = RepeatedTimer((self._cleanupInterval/1000), self.registeredClientRegistry.sweepOldClients)

        # Process queue from main thread for shutdown messages
        self.threadProcessQueue = Thread(target=self.processQueue)
        self.threadProcessQueue.setDaemon(True)
        self.threadProcessQueue.start()

        #read the queue
        while self.alive:
            if not self.queueBLE.empty():
                result = self.queueBLE.get(block=False, timeout=1)
                self.__handleBtleClientEvents(result)

    def processQueue(self):
        self.logger.info("Starting to watch collection point inbound message queue")
        while self.alive:
            if not self.inQueue.empty():
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

    def __handleBtleClientEvents(self, detectedClients):
        for client in detectedClients:
            self.logger.debug("--- Found client ---")
            self.logger.debug(vars(client))
            self.logger.debug("--- Found client end ---")
            self.eventManager.registerDetectedClient(client)

    def handleMessage(self, msg):
        # Handle incoming messages, eg. from other collection points
        return

    def shutdown(self):
        self.logger.info("Shutting down")
        self.repeatTimerSweepClients.stop()
        self.btleThread.stop()
        self.alive = False
        time.sleep(1)
        self.exit = True

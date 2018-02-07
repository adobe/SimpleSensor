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

        # Variables
        self.video = None
        self.needsReset = False
        self.needsResetMux = False
        self.alive = True

        # Configs
        self.moduleConfig = configLoader.load(self.loggingQueue) #Get the config for this module
        self.config = baseConfig

        # Prediction engine
        self.imagePredictionEngine = AzureImagePrediction(moduleConfig=self.moduleConfig, loggingQueue=loggingQueue)

        # Constants
        self._useIdsCamera = self.moduleConfig['UseIdsCamera']

        try:
            with open("/collectionPoint.conf") as f:
                configParser.readfp(f)
        except IOError: 
            configParser.read(os.path.join(os.path.dirname(__file__),"config/collectionPoint.conf"))

        # Logger
        self.logger = ThreadsafeLogger(loggingQueue, __name__)



    logger.info("Setup App config for collection point : %s" % configParser.get('CollectionPointConf','CollectionPointId'))
    # ZeroMq setup
    REQUEST_TIMEOUT = configParser.getint('zmq_conf','Request_timeout')
    logger.info("ZMQ request timeout: %s" % REQUEST_TIMEOUT)
    REQUEST_RETRIES = configParser.getint('zmq_conf','Request_retries')
    logger.info("ZMQ request retries: %s" % REQUEST_RETRIES)
    SERVER_ENDPOINT = configParser.get('zmq_conf','Server_endpoint')
    logger.info("ZMQ server endpoint: %s" % SERVER_ENDPOINT)

    #collection point config
    collectionPointConfig = {}
    GATEWAY_TYPE = configParser.get('CollectionPointConf','GatewayType')
    logger.info("gateway type is: %s" % GATEWAY_TYPE)
    collectionPointConfig['gatewayType'] = GATEWAY_TYPE

    COLLECTION_POINT_ID=configParser.get('CollectionPointConf','CollectionPointId')
    logger.info("Collection point id: %s" % COLLECTION_POINT_ID)
    collectionPointConfig['collectionPointId'] = COLLECTION_POINT_ID

    INTERFACE_TYPE = configParser.get('CollectionPointConf','InterfaceType')
    logger.info("Collection point interface type: %s" % INTERFACE_TYPE)
    collectionPointConfig['InterfaceType']=INTERFACE_TYPE

    PROXIMITY_EVENT_INTERVAL_IN_MILLISECONDS = configParser.getint('CollectionPointConf','ProximityEventIntervalInMilliseconds')
    logger.info("Proximity event interval in milliseconds: %i" % PROXIMITY_EVENT_INTERVAL_IN_MILLISECONDS)
    collectionPointConfig['proximityEventIntervalInMilliseconds']=PROXIMITY_EVENT_INTERVAL_IN_MILLISECONDS

    LEAVE_TIME_IN_MILLISECONDS = configParser.getint('CollectionPointConf','leaveTimeInMilliseconds')
    logger.info("leave time in milliseconds: %i" % LEAVE_TIME_IN_MILLISECONDS)
    collectionPointConfig['leaveTimeInMilliseconds']=LEAVE_TIME_IN_MILLISECONDS

    #TODO: run sweep on secondary thread that runs at this interval
    ABANDONED_CLIENT_CLEANUP_INTERVAL_IN_MILLISECONDS = configParser.getint('CollectionPointConf','AbandonedClientCleanupIntervalInMilliseconds')
    logger.info("AbandonedClientCleanupIntervalInMilliseconds: %i" % ABANDONED_CLIENT_CLEANUP_INTERVAL_IN_MILLISECONDS)
    collectionPointConfig['abandonedClientCleanupIntervalInMilliseconds']=ABANDONED_CLIENT_CLEANUP_INTERVAL_IN_MILLISECONDS

    ABANDONED_CLIENT_TIMEOUT_IN_MILLISECONDS = configParser.getint('CollectionPointConf','AbandonedClientTimeoutInMilliseconds')
    logger.info("AbandonedClientTimeoutInMilliseconds: %i" % ABANDONED_CLIENT_TIMEOUT_IN_MILLISECONDS)
    collectionPointConfig['abandonedClientTimeoutInMilliseconds']=ABANDONED_CLIENT_TIMEOUT_IN_MILLISECONDS

    BTLE_RSSI_CLIENT_IN_THRESHOLD = configParser.getint('CollectionPointConf','BtleRssiClientInThreshold')
    logger.info("BTLE client in threshold: %i" % BTLE_RSSI_CLIENT_IN_THRESHOLD)
    collectionPointConfig['btleRssiClientInThreshold']=BTLE_RSSI_CLIENT_IN_THRESHOLD

    BTLE_RSSI_CLIENT_IN_THRESHOLD_TYPE = configParser.get('CollectionPointConf','BtleRssiClientInThresholdType')
    logger.info("BTLE client in threshold type: %s" % BTLE_RSSI_CLIENT_IN_THRESHOLD_TYPE)
    collectionPointConfig['btleRssiClientInThresholdType'] = BTLE_RSSI_CLIENT_IN_THRESHOLD_TYPE

    BTLE_DEVICE_ID = configParser.get('CollectionPointConf','BtleDeviceId')
    logger.info("BTLE Device Id: %s" % BTLE_DEVICE_ID)
    collectionPointConfig['btleDeviceId'] = BTLE_DEVICE_ID

    try:
        BTLE_DEVICE_BAUD_RATE = configParser.getint('CollectionPointConf','BtleDeviceBaudRate')
    except:
        BTLE_DEVICE_BAUD_RATE = 38400
    logger.info("BTLE Device Baud Rate: %i" % BTLE_DEVICE_BAUD_RATE)
    collectionPointConfig['btleDeviceBaudRate'] = BTLE_DEVICE_BAUD_RATE

    BTLE_ADVERTISING_MAJOR = configParser.getint('CollectionPointConf','BtleAdvertisingMajor')
    logger.info("BTLE Major: %i" % BTLE_ADVERTISING_MAJOR)
    collectionPointConfig['btleAdvertisingMajor'] = BTLE_ADVERTISING_MAJOR

    BTLE_ADVERTISING_MINOR = configParser.getint('CollectionPointConf','BtleAdvertisingMinor')
    logger.info("BTLE Minor: %i" % BTLE_ADVERTISING_MINOR)
    collectionPointConfig['btleAdvertisingMinor'] = BTLE_ADVERTISING_MINOR

    BTLE_ANOMALY_RESET_LIMIT = configParser.getint('CollectionPointConf','BtleAnomalyResetLimit')
    logger.info("BTLE Anomaly reset limit: %i" % BTLE_ANOMALY_RESET_LIMIT)
    collectionPointConfig['btleAnomalyResetLimit'] = BTLE_ANOMALY_RESET_LIMIT

    BTLE_RSSI_NEEDED_SAMPLE_SIZE = configParser.getint('CollectionPointConf','BtleRssiNeededSampleSize')
    logger.info("BTLE rssi needed sample size: %i" % BTLE_RSSI_NEEDED_SAMPLE_SIZE)
    collectionPointConfig['btleRssiNeededSampleSize'] = BTLE_RSSI_NEEDED_SAMPLE_SIZE

    BTLE_RSSI_MAX_SAMPLE_SIZE = configParser.getint('CollectionPointConf','BtleRssiMaxSampleSize')
    logger.info("BTLE rssi max sample size: %i" % BTLE_RSSI_MAX_SAMPLE_SIZE)
    collectionPointConfig['btleRssiMaxSampleSize'] = BTLE_RSSI_MAX_SAMPLE_SIZE

    BTLE_RSSI_ERROR_VARIANCE = configParser.getfloat('CollectionPointConf','BtleRssiErrorVariance')
    logger.info("BTLE rssi error variance multiplier: %f" % BTLE_RSSI_ERROR_VARIANCE)
    collectionPointConfig['btleRssiErrorVariance'] = BTLE_RSSI_ERROR_VARIANCE

    try:
        BTLE_DEVICE_TX_POWER = configParser.getint('CollectionPointConf','BtleDeviceTxPower')
    except:
        BTLE_DEVICE_TX_POWER = 15
    logger.info("BTLE TX power: %i" % BTLE_DEVICE_TX_POWER)
    collectionPointConfig['btleDeviceTxPower'] = BTLE_DEVICE_TX_POWER

    try:
        BTLE_CLIENTOUT_COUNT_THRESHOLD = configParser.getint('CollectionPointConf','BtleClientOutCountThreshold')
    except:
        BTLE_CLIENTOUT_COUNT_THRESHOLD = 15
    logger.info("BTLE ClientOut Count Threshold: %i" % BTLE_CLIENTOUT_COUNT_THRESHOLD)
    collectionPointConfig['btleClientOutCountThreshold'] = BTLE_CLIENTOUT_COUNT_THRESHOLD

    # Used to send alerts when things are not working right
    try:
        SLACK_CHANNEL_WEBHOOK_URL = configParser.get('CollectionPointConf','SlackChannelWebhookUrl')
    except:
        SLACK_CHANNEL_WEBHOOK_URL = ""
    logger.info("Slack Webhook url: %s" % SLACK_CHANNEL_WEBHOOK_URL)
    collectionPointConfig['slackChannelWebhookUrl'] = SLACK_CHANNEL_WEBHOOK_URL

    ###Pausing Startup to wait for things to start after a system restart
    logger.info("Pausing execution 15 seconds waiting for other system services to start")
    time.sleep(15)
    logger.info("Done with our nap.  Time to start looking for clients")

    #########  setup global client registry start #########

    registeredClientRegistry = RegisteredClientRegistry(collectionPointConfig)

    #########  setup global client registry end #########

    #EventManager
    zmqOptions = {'zmqServerEndpoint':SERVER_ENDPOINT,'zmqRequestTimeout':REQUEST_TIMEOUT,'zmqRequestRetries':REQUEST_RETRIES}
    eventManager = EventManager(collectionPointConfig,zmqOptions,registeredClientRegistry)
    eventManager.start()

    #BTLE Config
    btleConfig={}
    btleConfig['deviceId'] = BTLE_DEVICE_ID
    btleConfig['major'] = BTLE_ADVERTISING_MAJOR
    btleConfig['minor'] = BTLE_ADVERTISING_MINOR
    btleConfig['btleDeviceBaudRate'] = BTLE_DEVICE_BAUD_RATE
    btleConfig['btleDeviceTxPower'] = BTLE_DEVICE_TX_POWER
    btleConfig['slackChannelWebhookUrl'] = SLACK_CHANNEL_WEBHOOK_URL

    #handle btle reads
    #pp = pprint.PrettyPrinter(indent=4)
    def handleBtleClientEvents(dectectedClients):
        #logger.debug("doing handleBtleClientEvents")
        for client in dectectedClients:
            logger.debug("--- Found client ---")
            logger.debug(vars(client))
            logger.debug("--- Found client end ---")
            eventManager.registerDetectedClient(client)

    queueBLE = Queue()
    btleThread = BlueGigaBtleCollectionPointThread(queueBLE,btleConfig)
    BLEThread = Thread(target=btleThread.bleDetect, args=(__name__,10))
    BLEThread.daemon = True
    BLEThread.start()

    #Setup repeat task to run the sweep every X interval
    repeatTimerSweepClients = RepeatedTimer((collectionPointConfig['abandonedClientCleanupIntervalInMilliseconds']/1000), registeredClientRegistry.sweepOldClients)

    #read the queue
    try:
        while True:
            if (queueBLE.empty() == False):
                result = queueBLE.get(False)
                handleBtleClientEvents(result)
    except KeyboardInterrupt:
        print "attempting to close threads."
        eventManager.stop()
        repeatTimerSweepClients.stop()
        btleThread.stop()
        print "threads successfully closed"

from detectedClient import DetectedClient
import os
import sys
import time
import math
import logging
import logging.config
from threadsafeLogger import ThreadsafeLogger

#TODO: clean up mess from our trials on the scan normalizing
class BtleRegisteredClient:
    #part of interface for Registered Client
    def __init__(self,detectedClient,collectionPointConfig,loggingQueue):
        # Logger
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)
            
        self.logger = logging.getLogger('btleRegisteredClient.BtleRegisteredClient')
        self.clientEventLogger = logging.getLogger('btleRegisteredClient.BtleEventTesting')
        self.clientEventSendLogger = logging.getLogger('eventSend')
        self.clientInRangeTrigerCount = 2
        self.lastTimeMessageClientInWasSentToController = -1
        self.lastTimeMessageClientOutWasSentToController = -1
        self.__countClientInRange=0
        self.__countClientOutOfRange=0
        self.timeInCollectionPointInMilliseconds = 0
        self.firstRegisteredTime = time.time()
        self.collectionPointConfig = collectionPointConfig
        self.__clientOutThresholdMin = int(self.collectionPointConfig['BtleRssiClientInThreshold'] + (self.collectionPointConfig['BtleRssiClientInThreshold'] * self.collectionPointConfig['BtleRssiErrorVariance']))
        self.handleNewDetectedClientEvent(detectedClient)  #standard shared methods when we see a detected client

    #part of interface for Registered Client
    def updateWithNewDectedClientData(self,detectedClient):
        self.timeInCollectionPointInMilliseconds = time.time() - self.firstRegisteredTime
        self.handleNewDetectedClientEvent(detectedClient)  #standard shared methods when we see a detected client

    #Common methods are handled here for updateWithNewDectedClientData and init
    def handleNewDetectedClientEvent(self,detectedClient):
        self.lastRegisteredTime = time.time()
        self.detectedClient = detectedClient
        self.txPower = detectedClient.extraData['tx']
        self.beaconId = detectedClient.extraData['udid']    #TODO HACK FIX
        self.incrementInternalClientEventCounts(detectedClient)

    def incrementInternalClientEventCounts(self,detectedClient):
        self.clientEventLogger.debug("==================================== EVENT COUNTS DATA START ====================================")
        self.clientEventLogger.debug("Counts before inCount %i : outCount %i" %(self.__countClientInRange,self.__countClientOutOfRange))

        #self.clientEventLogger.debug("rssi types")
        #self.clientEventLogger.debug("type of self.detectedClient.extraData['rssi'] = %s" %type(self.detectedClient.extraData['rssi']))
        #self.clientEventLogger.debug("type of self.detectedClient.extraData['rssi'] = %s" %type(self.detectedClient.extraData['rssi']))
        #self.clientEventLogger.debug("type of self.collectionPointConfig['btleRssiClientInThreshold'] = %s " %type(self.collectionPointConfig['btleRssiClientInThreshold']))
        #self.clientEventLogger.debug("type of self.__clientOutThresholdMin = %s " %type(self.__clientOutThresholdMin))

        if self.collectionPointConfig['gatewayType'] == 'proximity':
            #check threshold type
            if self.collectionPointConfig['btleRssiClientInThresholdType'] == 'rssi':
                #are they in or are they out of range --- increament internal count.  we use the count to normalize the events even more
                #self.logger.debug("rssi average %i  > btleRssi threshold %i: %s" %(self.getRssiAverage(),self.collectionPointConfig['btleRssiClientInThreshold'],self.getRssiAverage() > self.collectionPointConfig['btleRssiClientInThreshold']))
                self.clientEventLogger.debug("Registered Client Event")
                self.clientEventLogger.debug("UDID is %s " %self.getUdid())
                self.clientEventLogger.debug("Beacon ID is %s " %self.beaconId)
                self.clientEventLogger.debug("RSSI %i" %self.detectedClient.extraData['rssi'])
                self.clientEventLogger.debug("BTLE RSSI client in threshold %i" %self.collectionPointConfig['BtleRssiClientInThreshold'])
                self.clientEventLogger.debug("BTLE RSSI client out threshold %i" %self.__clientOutThresholdMin)

                if self.detectedClient.extraData['rssi'] >= self.collectionPointConfig['BtleRssiClientInThreshold']:
                    self.__countClientInRange = self.__countClientInRange + 1
                    self.__countClientOutOfRange = 0
                    self.clientEventLogger.debug("CLIENT IN RANGE>>>>>>>>>>>")

                else:
                    if self.detectedClient.extraData['rssi'] <= self.__clientOutThresholdMin:
                        self.__countClientOutOfRange = self.__countClientOutOfRange + 1
                        #self.__countClientInRange = 0
                        self.clientEventLogger.debug("CLIENT OUT OF RANGE<<<<<<<<<<<")

                    else:
                        self.clientEventLogger.debug("CLIENT IN BUFFER AREA==========")

        self.clientEventLogger.debug("Counts after inCount %i : outCount %i" %(self.__countClientInRange,self.__countClientOutOfRange))
        self.clientEventLogger.debug("==================================== EVENT COUNTS DATA END ====================================")
        self.clientEventLogger.debug("")

    #part of interface for Registered Client
    def shouldSendClientInEvent(self):
        if self.collectionPointConfig['gatewayType'] == 'proximity':
            #we compare on seconds so we need to adjust this to seconds
            proximityEventIntervalInSeconds = (self.collectionPointConfig['ProximityEventIntervalInMilliseconds']/1000)

            timeDiff = math.trunc(time.time() - self.lastTimeMessageClientInWasSentToController)
            self.logger.debug("shouldSendClientInEvent timeDiff %f > %s" %(timeDiff,proximityEventIntervalInSeconds) )

            if timeDiff > proximityEventIntervalInSeconds:
                if self.__countClientInRange > self.clientInRangeTrigerCount:
                    self.logClientEventSend("SHOULD ClientIN event to controller for")
                    self.zeroEventRangeCounters()
                    return True

        #TODO add in other types of gateway types

        return False

    #part of interface for Registered Client
    def shouldSendClientOutEvent(self):
        if self.collectionPointConfig['gatewayType'] == 'proximity':
            #we compare on seconds so we need to adjust this to seconds
            proximityEventIntervalInSeconds = (self.collectionPointConfig['ProximityEventIntervalInMilliseconds']/1000)

            #check the time to see if we need to send a message
            #have we ever sent an IN event? if not we dont need to send an out event
            if self.lastTimeMessageClientInWasSentToController > 0:
                #check timing on last event sent
                #self.logger.debug("shouldSendClientOutEvent lastTimeMessageClientOutWasSentToController=%f"%self.lastTimeMessageClientOutWasSentToController)
                timeDiff = time.time() - self.lastTimeMessageClientOutWasSentToController

                #have we sent a client out since the last client in?  if so we dont need to throw another
                if self.lastTimeMessageClientOutWasSentToController < self.lastTimeMessageClientInWasSentToController:
                    #do we have enought qualifying out events. we dont want to throw one too soon
                    if self.__countClientOutOfRange >= self.collectionPointConfig['BtleClientOutCountThreshold']:
                        self.logClientEventSend("SHOULD ClientOUT event to controller for")
                        self.zeroEventRangeCounters()
                        return True

                #lets check to see if we need to clean up the out count --- not sure this is the best idea
                else:
                    if self.__countClientOutOfRange > self.collectionPointConfig['BtleClientOutCountThreshold']:
                        self.clientEventLogger.debug("Client out count %i is past max.  Resetting." %self.__countClientOutOfRange)
                        self.__countClientOutOfRange = 0

            else:
                #lets check to see if we need to clean up the out count --- not sure this is the best idea
                if self.__countClientOutOfRange > self.collectionPointConfig['BtleClientOutCountThreshold']:
                    self.clientEventLogger.debug("Client out count %i is past max.  Resetting." %self.__countClientOutOfRange)
                    self.__countClientOutOfRange = 0

        #TODO add in other types of gateway types

        return False

    #part of interface for Registered Client
    def sweepShouldSendClientOutEvent(self):
        if self.collectionPointConfig['gatewayType'] == 'proximity':
            #has an out event already been sent? if so we dont need to throw another on sweep
            if self.lastTimeMessageClientOutWasSentToController > 0:
                #was there a in event sent after the last out?
                if self.lastTimeMessageClientInWasSentToController > self.lastTimeMessageClientOutWasSentToController:
                    self.logClientEventSend("Sweep case a is sending ClientOUT on")
                    self.zeroEventRangeCounters()
                    return True
                else:
                    return False
            else:
                self.logClientEventSend("Sweep case b is sending ClientOUT on")
                self.zeroEventRangeCounters()
                return True

        #TODO add in other types of gateway types

        return True

    #part of interface for Registered Client
    def getUdid(self):
        return self.detectedClient.extraData["beaconMac"]

    def getTxPower(self):
        return self.txPower

    #zero out the BTLE event counters
    def zeroEventRangeCounters(self):
        self.__countClientOutOfRange = 0
        self.__countClientInRange = 0

    def logClientEventSend(self,message):
        self.clientEventSendLogger.debug("")
        self.clientEventSendLogger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.clientEventSendLogger.debug("%%%%%%%%%%%%%%%%%% %s %%%%%%%%%%%%%%%%%%" %message)
        self.clientEventSendLogger.debug("UDID is %s " %self.getUdid())
        self.clientEventSendLogger.debug("Beacon ID is %s " %self.beaconId)
        self.clientEventSendLogger.debug("RSSI %i" %self.detectedClient.extraData['rssi'])
        self.clientEventSendLogger.debug("BTLE RSSI client in threshold %i" %self.collectionPointConfig['BtleRssiClientInThreshold'])
        self.clientEventSendLogger.debug("BTLE RSSI client out threshold %i" %self.__clientOutThresholdMin)
        self.clientEventSendLogger.debug("inCount %i : outCount %i" %(self.__countClientInRange,self.__countClientOutOfRange))
        self.clientEventSendLogger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.clientEventSendLogger.debug("")


    #part of interface for Registered Client
    def getExtenedDataForEvent(self):
        extraData = {}
        extraData['lastRegisteredTime'] = self.lastRegisteredTime
        extraData['firstRegisteredTime'] = self.firstRegisteredTime
        extraData['lastTimeMessageClientInWasSentToController'] = self.lastTimeMessageClientInWasSentToController
        extraData['lastTimeMessageClientOutWasSentToController'] = self.lastTimeMessageClientOutWasSentToController
        extraData['timeInCollectionPointInMilliseconds'] = self.timeInCollectionPointInMilliseconds
        extraData['rssi'] = self.detectedClient.extraData['rssi']
        extraData['averageRssi'] = self.detectedClient.extraData['rssi']
        extraData['txPower'] = self.getTxPower()
        #TODO INSTALL FIX
        extraData['beaconId'] = self.beaconId

        return extraData

    #part of interface for Registered Client
    def setClientInMessageSentToController(self):
        self.lastTimeMessageClientInWasSentToController = time.time()
        self.__countClientInRange = 0

    #part of interface for Registered Client
    def setClientOutMessageSentToController(self):
        self.lastTimeMessageClientOutWasSentToController = time.time()
        self.__countClientOutOfRange = 0

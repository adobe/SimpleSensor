from detectedClient import DetectedClient
import os
import sys
import time
import math
import logging
import logging.config
from threadsafeLogger import ThreadsafeLogger
from uidMap import UIDMap as UIDMap

class BtleRegisteredClient:
    def __init__(self, detectedClient, collectionPointConfig, loggingQueue):
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)
        
        # Counters and variables
        self.clientInRangeTrigerCount = 2
        self.prevClientInMsgTime = -1
        self.prevClientOutMsgTime = -1
        self.numClientInRange=0
        self.numClientOutRange=0
        self.timeInCollectionPointInMilliseconds = 0
        self.firstRegisteredTime = time.time()
        self.collectionPointConfig = collectionPointConfig
        try:
            self.uidMap = UIDMap()
        except Exception as e:
            print('cant instantiate uid map: %s '%e)
        # Constants
        self._rssiClientInThresh = self.collectionPointConfig['BtleRssiClientInThreshold']
        self._rssiErrorVar = self.collectionPointConfig['BtleRssiErrorVariance']
        self.__clientOutThresholdMin = int(self._rssiClientInThresh + (self._rssiClientInThresh * self._rssiErrorVar))

        # Initiate event when client is detected
        self.handleNewDetectedClientEvent(detectedClient)

    # part of interface for Registered Client
    def updateWithNewDetectedClientData(self, detectedClient):
        self.timeInCollectionPointInMilliseconds = time.time() - self.firstRegisteredTime
        self.handleNewDetectedClientEvent(detectedClient)  #standard shared methods when we see a detected client

    # Common methods are handled here for updateWithNewDetectedClientData and init
    def handleNewDetectedClientEvent(self, detectedClient):
        self.lastRegisteredTime = time.time()
        self.detectedClient = detectedClient
        self.txPower = detectedClient.extraData['tx']
        self.beaconId = detectedClient.extraData['udid']
        self.incrementInternalClientEventCounts(detectedClient)

    def incrementInternalClientEventCounts(self, detectedClient):
        if self.collectionPointConfig['GatewayType'] == 'proximity':
            if self.collectionPointConfig['BtleRssiClientInThresholdType'] == 'rssi':
                # Are they in or are they out of range 
                # Increment internal count, used to normalize events.
                if self.detectedClient.extraData['rssi'] >= self.collectionPointConfig['BtleRssiClientInThreshold']:
                    self.numClientInRange = self.numClientInRange + 1
                    self.numClientOutRange = 0
                    self.logger.debug("CLIENT IN RANGE>>>>>>>>>>>")

                elif self.detectedClient.extraData['rssi'] < self.__clientOutThresholdMin:
                        self.numClientOutRange = self.numClientOutRange + 1
                        #self.numClientInRange = 0
                        self.logger.debug("CLIENT OUT OF RANGE<<<<<<<<<<<")

    #part of interface for Registered Client
    def shouldSendClientInEvent(self):
        if self.collectionPointConfig['GatewayType'] == 'proximity':
            #e compare on seconds so we need to adjust this to seconds
            proximityEventIntervalInSeconds = (self.collectionPointConfig['ProximityEventInterval']/1000)

            timeDiff = math.trunc(time.time() - self.prevClientInMsgTime)
            # self.logger.debug("shouldSendClientInEvent timeDiff %f > %s" %(timeDiff,proximityEventIntervalInSeconds) )

            if timeDiff > proximityEventIntervalInSeconds:
                if self.numClientInRange > self.clientInRangeTrigerCount:
                    self.logClientEventSend("SHOULD ClientIN event to controller for")
                    self.zeroEventRangeCounters()
                    return True

        #TODO add in other types of gateway types

        return False

    #part of interface for Registered Client
    def shouldSendClientOutEvent(self):
        if self.collectionPointConfig['GatewayType'] == 'proximity':
            #we compare on seconds so we need to adjust this to seconds
            proximityEventIntervalInSeconds = (self.collectionPointConfig['ProximityEventInterval']/1000)

            #check the time to see if we need to send a message
            #have we ever sent an IN event? if not we dont need to send an out event
            if self.prevClientInMsgTime > 0:
                #check timing on last event sent
                #self.logger.debug("shouldSendClientOutEvent prevClientOutMsgTime=%f"%self.prevClientOutMsgTime)
                timeDiff = time.time() - self.prevClientOutMsgTime

                #have we sent a client out since the last client in?  if so we dont need to throw another
                if self.prevClientOutMsgTime < self.prevClientInMsgTime:
                    #do we have enought qualifying out events. we dont want to throw one too soon
                    if self.numClientOutRange >= self.collectionPointConfig['BtleClientOutCountThreshold']:
                        self.logClientEventSend("SHOULD ClientOUT event to controller for")
                        self.zeroEventRangeCounters()
                        return True

                #lets check to see if we need to clean up the out count --- not sure this is the best idea
                else:
                    if self.numClientOutRange > self.collectionPointConfig['BtleClientOutCountThreshold']:
                        # self.logger.debug("Client out count %i is past max.  Resetting." %self.numClientOutRange)
                        self.numClientOutRange = 0

            else:
                #lets check to see if we need to clean up the out count --- not sure this is the best idea
                if self.numClientOutRange > self.collectionPointConfig['BtleClientOutCountThreshold']:
                    # self.logger.debug("Client out count %i is past max.  Resetting." %self.numClientOutRange)
                    self.numClientOutRange = 0

        #TODO add in other types of gateway types

        return False

    #part of interface for Registered Client
    def sweepShouldSendClientOutEvent(self):
        if self.collectionPointConfig['GatewayType'] == 'proximity':
            #has an out event already been sent? if so we dont need to throw another on sweep
            if self.prevClientOutMsgTime > 0:
                #was there a in event sent after the last out?
                if self.prevClientInMsgTime > self.prevClientOutMsgTime:
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
        self.numClientOutRange = 0
        self.numClientInRange = 0

    def logClientEventSend(self,message):
        return
        # self.logger.debug("")
        # self.logger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # self.logger.debug("%%%%%%%%%%%%%%%%%% %s %%%%%%%%%%%%%%%%%%" %message)
        # self.logger.debug("UDID is %s " %self.getUdid())
        # self.logger.debug("Beacon ID is %s " %self.beaconId)
        # self.logger.debug("RSSI %i" %self.detectedClient.extraData['rssi'])
        # self.logger.debug("BTLE RSSI client in threshold %i" %self.collectionPointConfig['BtleRssiClientInThreshold'])
        # self.logger.debug("BTLE RSSI client out threshold %i" %self.__clientOutThresholdMin)
        # self.logger.debug("inCount %i : outCount %i" %(self.numClientInRange,self.numClientOutRange))
        # self.logger.debug("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # self.logger.debug("")


    #part of interface for Registered Client
    def getExtendedDataForEvent(self):
        extraData = {}
        extraData['lastRegisteredTime'] = self.lastRegisteredTime
        extraData['firstRegisteredTime'] = self.firstRegisteredTime
        extraData['prevClientInMsgTime'] = self.prevClientInMsgTime
        extraData['prevClientOutMsgTime'] = self.prevClientOutMsgTime
        extraData['timeInCollectionPointInMilliseconds'] = self.timeInCollectionPointInMilliseconds
        extraData['rssi'] = self.detectedClient.extraData['rssi']
        extraData['averageRssi'] = self.detectedClient.extraData['rssi']
        extraData['txPower'] = self.getTxPower()
        extraData['beaconId'] = self.beaconId
        extraData['beaconMac'] = self.detectedClient.extraData["beaconMac"]
        extraData['industry'] = self.uidMap.get(self.beaconId)

        return extraData

    #part of interface for Registered Client
    def setClientInMessageSentToController(self):
        self.prevClientInMsgTime = time.time()
        self.numClientInRange = 0

    #part of interface for Registered Client
    def setClientOutMessageSentToController(self):
        self.prevClientOutMsgTime = time.time()
        self.numClientOutRange = 0

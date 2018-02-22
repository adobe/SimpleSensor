import os
import os.path
import logging
import logging.config
import time
import json
import requests
import platform
from threading import Thread
from btleThreadCollectionPoint import BtleThreadCollectionPoint
from detectedClient import DetectedClient
from threadsafeLogger import ThreadsafeLogger

class BlueGigaBtleCollectionPointThread(Thread):

    def __init__(self, queue, btleConfig, loggingQueue, debugMode=False):
        Thread.__init__(self)
        # Logger
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)
        self.alive = True
        self.btleConfig = btleConfig
        self.queue = queue
        self.btleCollectionPoint = BtleThreadCollectionPoint(self.eventScanResponse,self.btleConfig,self.loggingQueue)

    def bleDetect(self,__name__,repeatcount=10):
        try:
            self.btleCollectionPoint.start()
        except Exception as e:
            self.logger.error("[btleThread] Unable to connect to BTLE device: %s"%e)
            self.sendFailureNotice("Unable to connect to BTLE device")
            quit()

        while self.alive:
            try:
                self.btleCollectionPoint.scan()
            except Exception as e:
                self.logger.error("[btleThread] Unable to scan BTLE device: %s"%e)
                self.sendFailureNotice("Unable to connect to BTLE device to perform a scan")
                quit()

            # don't burden the CPU
            time.sleep(0.01)

    # handler to print scan responses with a timestamp
    def eventScanResponse(self,sender,args):

        #check to make sure there is enough data to be a beacon
        if len(args["data"]) > 15:
            # self.logger.debug("=============================== eventScanResponse START ===============================")
            try:
                majorNumber = args["data"][26] | (args["data"][25] << 8)
                # self.logger.debug("majorNumber=%i"%majorNumber)
            except:
                majorNumber = 0

            try:
                minorNumber = args["data"][28] | (args["data"][27] << 8)
                # self.logger.debug("minorNumber=%i"%minorNumber)
            except:
                minorNumber = 0

            if self.btleConfig['BtleAdvertisingMajor'] == majorNumber and self.btleConfig['BtleAdvertisingMinor'] == minorNumber:
                self.logger.debug("self.btleConfig['BtleAdvertisingMinor'] == %i and self.btleConfig['BtleAdvertisingMinor'] == %i "%(majorNumber,minorNumber))
                self.logger.debug("yep, we care about this major and minor so lets create a detected client and pass it to the event manager")

                udid = "%s" % ''.join(['%02X' % b for b in args["data"][9:25]])
                self.logger.debug("UDID=%s"%udid)
                rssi = args["rssi"]
                self.logger.debug("rssi=%s"%rssi)

                beaconMac = "%s" % ''.join(['%02X' % b for b in args["sender"][::-1]])
                self.logger.debug("beaconMac=%s"%beaconMac)
                rawTxPower = args["data"][29]
                self.logger.debug("rawTxPower=%i"%rawTxPower)

                if rawTxPower <= 127:
                    txPower = rawTxPower
                else:
                    txPower = rawTxPower - 256
                self.logger.debug("txPower=%i"%txPower)

                arrayDetectedClients = [] #we send an array to the event queue, we used to process bacthes of responses

                #package it up for sending to the queue
                detectedClient = DetectedClient('btle',udid=udid,beaconMac=beaconMac,majorNumber=majorNumber,minorNumber=minorNumber,tx=txPower,rssi=rssi)
                arrayDetectedClients.append(detectedClient)

                #put it on the queue for the event manager to pick up
                self.queue.put(arrayDetectedClients)
                self.logger.debug("================================= eventScanResponse END =================================")

    def stop(self):
        self.alive = False

    def sendFailureNotice(self,msg):
        if len(self.btleConfig['SlackChannelWebhookUrl']) > 10:
            myMsg = 'Help I have fallen and can not get back up! \n %s. \nSent from %s'%(msg,platform.node())
            payload = {'text': myMsg}
            r = requests.post(self.btleConfig['SlackChannelWebhookUrl'], data = json.dumps(payload))

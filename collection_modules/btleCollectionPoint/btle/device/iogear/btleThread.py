import os
import os.path
import sys
from collectionPoint import BtleCollectionPoint
import bluetooth._bluetooth as bluez
import logging
import logging.config

class IoGearBtleCollectionPointThread(object):
    def __init__(self,source,queue,btleConfig,debugMode=False):
        # logging setup
        try:
            logging.config.fileConfig("/logging.conf")
        except:
            logging.config.fileConfig(os.path.join(os.path.dirname(__file__),"../../../config/logging.conf"))
        self.logger = logging.getLogger('btleThread.BtleThread')
        self.btleConfig = btleConfig
        self.btleCollectionPoint = BtleCollectionPoint(None,self.btleConfig)
        self.queue = queue

    def bleDetect(self,__name__,repeatcount=10):

        dev_id = self.btleConfig['deviceId']
        try:
            sock = bluez.hci_open_dev(dev_id)

        except:
            self.logger.error("error accessing bluetooth device...")
            sys.exit(1)

        self.btleCollectionPoint.hci_le_set_scan_parameters(sock)
        self.btleCollectionPoint.hci_enable_le_scan(sock)

        while True:
            returnedList = self.btleCollectionPoint.parse_events(sock, repeatcount)
            self.queue.put(returnedList)
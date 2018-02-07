__author__ = 'dbenge'

import time

class DetectedClient:
    def __init__(self,type,**kwargs):
        self.type=type
        if self.type == 'btle':
            self.udid=kwargs.get('udid','undefined')
            self.createTime = time.time()
            self.extraData = {}
            self.extraData['beaconMac'] = kwargs.get('beaconMac','undefined')
            self.extraData['majorNumber'] = kwargs.get('majorNumber',0)
            self.extraData['minorNumber'] = kwargs.get('minorNumber',0)
            self.extraData['udid'] = self.udid
            self.extraData['tx'] = kwargs.get('tx',0)
            self.extraData['rssi'] = kwargs.get('rssi',0)
        #we could add in over types here if needed
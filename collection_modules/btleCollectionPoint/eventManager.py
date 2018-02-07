import os.path
import logging
from Queue import Queue
from threading import Thread
from collectionPointEvent import CollectionPointEvent
from btle.btleRegisteredClient import BtleRegisteredClient
from zmqConnectionThread import ZmqConnectionThread


class EventManager(object):
    def __init__(self,collectionPointConfig,zmqConfig,registeredClientRegistry):
        try:
            logging.config.fileConfig("/logging.conf")
        except:
            logging.config.fileConfig(os.path.join(os.path.dirname(__file__),"config/logging.conf"))
        self.__stats_totalRemoveEvents = 0
        self.__stats_totalNewEvents = 0
        self.logger = logging.getLogger('eventManager.EventManager')
        self.logger.debug("in constructor")
        self.registeredClientRegistry = registeredClientRegistry
        self.registeredClientRegistry.eventRegisteredClientAdded += self.__newClientRegistered
        self.registeredClientRegistry.eventRegisteredClientRemoved += self.__removedRegisteredClient
        self.collectionPointConfig = collectionPointConfig
        self.messageQueue = Queue()
        self.zmqThread = ZmqConnectionThread(self.messageQueue,zmqConfig)

    def stop(self):
        self.zmqThread.stop()

    def start(self):
        self.zmqThread.start()
        zmqLiveThread = Thread(target=self.zmqThread.readMessages)
        zmqLiveThread.daemon = True
        zmqLiveThread.start()

    def registerDetectedClient(self,detectedClient):
        self.logger.debug("Registering detected client %s"%detectedClient.extraData["beaconMac"])
        eClient = self.registeredClientRegistry.getRegisteredClient(detectedClient.extraData["beaconMac"])

        #check for existing
        if eClient == None:
            #Newly found client
            if self.collectionPointConfig['InterfaceType'] == 'btle':
                rClient = BtleRegisteredClient(detectedClient,self.collectionPointConfig)
            self.logger.debug("client %s not found in the existing clients. NEW CLIENT! "%detectedClient.extraData["beaconMac"])

            if rClient.shouldSendClientInEvent():
                self.__sendEventToController(rClient,"clientIn")
            elif rClient.shouldSendClientOutEvent():
                self.logger.debug("########################################## SENDING CLIENT OUT eClient ##########################################")
                self.__sendEventToController(rClient,"clientOut")

            self.registeredClientRegistry.addNewRegisteredClient(rClient)

        else:
            eClient.updateWithNewDectedClientData(detectedClient)
            if eClient.shouldSendClientInEvent():
                #self.logger.debug("########################################## SENDING CLIENT IN ##########################################")
                self.__sendEventToController(eClient,"clientIn")
            elif eClient.shouldSendClientOutEvent():
                self.logger.debug("########################################## SENDING CLIENT OUT rClient ##########################################")
                self.__sendEventToController(eClient,"clientOut")

            self.registeredClientRegistry.updateRegisteredClient(eClient)

    def registerClients(self,detectedClients):
        for detectedClient in detectedClients:
            self.registerDetectedClient(detectedClient)

    def getEventAuditData(self):
        """Returns a dict with the total New and Remove events the engine has seen since startup"""
        return {'NewEvents': self.__stats_totalNewEvents, 'RemoveEvents': self.__stats_totalRemoveEvents}

    def __newClientRegistered(self,sender,registeredClient):
        self.logger.debug("######### NEW CLIENT REGISTERED %s #########"%registeredClient.detectedClient.extraData["beaconMac"])

        #we dont need to count for ever and eat up all the memory
        if self.__stats_totalNewEvents > 1000000:
            self.__stats_totalNewEvents = 0
        else:
            self.__stats_totalNewEvents += 1

    def __removedRegisteredClient(self,sender,registeredClient):
        self.logger.debug("######### REGISTERED REMOVED %s #########"%registeredClient.detectedClient.extraData["beaconMac"])
        if registeredClient.sweepShouldSendClientOutEvent():
            self.__sendEventToController(registeredClient,"clientOut")

        #we dont need to count for ever and eat up all the memory
        if self.__stats_totalRemoveEvents > 1000000:
            self.__stats_totalRemoveEvents = 0
        else:
            self.__stats_totalRemoveEvents  += 1

    def __sendEventToController(self,registeredClient,eventType):
        eventMessage = CollectionPointEvent(self.collectionPointConfig['collectionPointId'],registeredClient.lastRegisteredTime,registeredClient.detectedClient.extraData["beaconMac"],self.collectionPointConfig['gatewayType'],eventType,registeredClient.getExtenedDataForEvent())

        if eventType == 'clientIn':
            registeredClient.setClientInMessageSentToController()
        elif eventType == 'clientOut':
            registeredClient.setClientOutMessageSentToController()

        #update reg
        self.registeredClientRegistry.updateRegisteredClient(registeredClient)

        self.messageQueue.put(eventMessage)



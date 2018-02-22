import os
import os.path
import logging
import logging.config
from btleRegisteredClient import BtleRegisteredClient
import time
from threadsafeLogger import ThreadsafeLogger

class RegistryEvent(object):

    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return RegistryEventHandler(self, obj)

    def __set__(self, obj, value):
        pass


class RegistryEventHandler(object):

    def __init__(self, event, obj):

        self.event = event
        self.obj = obj

    def _getfunctionlist(self):

        """(internal use) """

        try:
            eventhandler = self.obj.__eventhandler__
        except AttributeError:
            eventhandler = self.obj.__eventhandler__ = {}
        return eventhandler.setdefault(self.event, [])

    def add(self, func):

        """Add new event handler function.

        Event handler function must be defined like func(sender, earg).
        You can add handler also by using '+=' operator.
        """

        self._getfunctionlist().append(func)
        return self

    def remove(self, func):

        """Remove existing event handler function.

        You can remove handler also by using '-=' operator.
        """

        self._getfunctionlist().remove(func)
        return self

    def fire(self, earg=None):

        """Fire event and call all handler functions

        You can call EventHandler object itself like e(earg) instead of
        e.fire(earg).
        """

        for func in self._getfunctionlist():
            func(self.obj, earg)

    __iadd__ = add
    __isub__ = remove
    __call__ = fire

class RegisteredClientRegistry(object):
    eventRegisteredClientRemoved = RegistryEvent()
    eventRegisteredClientAdded = RegistryEvent()
    eventRegisteredClientUpdated = RegistryEvent()
    eventSweepComplete = RegistryEvent()

    def __init__(self,collectionPointConfig,loggingQueue):
        # Logger
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

        self.rClients = {}  #registered clients
        self.collectionPointConfig = collectionPointConfig #collection point config

    def getRegisteredClient(self,udid):
        """Get an existing registered client by udid and if its found return it.  If no existing registered client is found return None."""
        try:
            eClient = self.rClients[udid]
        except KeyError:
            eClient = None

        return eClient

    def sweepOldClients(self):
        """look at the registry and look for expired inactive clients.  Returns a list of removed clients"""
        self.logger.debug("*** Sweeping clients existing count %s***"%len(self.rClients))

        clientsToBeRemoved=[] #list of clients to be cleaned up

        currentExpireTime = time.time() - (self.collectionPointConfig['AbandonedClientTimeout']/1000)

        for udid in self.rClients:
            regClient = self.rClients[udid]

            if regClient.lastRegisteredTime < currentExpireTime:
                clientsToBeRemoved.append(regClient)

        for client in clientsToBeRemoved:
            self.logger.debug("Client sweep removing udid %s"%client.getUdid())
            self.removeRegisteredClient(client)

        self.logger.debug("*** End of sweeping tags existing count %s***"%len(self.rClients))

        self.eventSweepComplete(clientsToBeRemoved)

        return clientsToBeRemoved

    def addNewRegisteredClient(self,registeredClient):
        self.logger.debug("in addNewRegisteredClient with %s"%registeredClient.getUdid())
        self.rClients[registeredClient.getUdid()] = registeredClient
        self.eventRegisteredClientAdded(registeredClient)#throw event

    def updateRegisteredClient(self,registeredClient):
        self.logger.debug("in updateRegisteredClient with %s"%registeredClient.getUdid())
        self.rClients[registeredClient.getUdid()] = registeredClient
        self.eventRegisteredClientUpdated(registeredClient)#throw event

    def removeRegisteredClient(self,registeredClient):
        self.logger.debug("in removeRegisteredClient with %s"%registeredClient.getUdid())
        self.rClients.pop(registeredClient.getUdid())
        self.eventRegisteredClientRemoved(registeredClient)#throw event
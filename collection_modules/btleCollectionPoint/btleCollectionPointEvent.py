class CollectionPointEvent():

    def __init__(self,collectionPointId,eventTime,clientId,gatewayType,event,extendedData):
        self.collectionPointId=collectionPointId
        self.eventTime=eventTime
        self.clientId=clientId
        self.gatewayType=gatewayType
        self.event=event
        self.extendedData=extendedData
        self._localOnly = False
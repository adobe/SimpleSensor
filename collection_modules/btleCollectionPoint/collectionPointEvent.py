class CollectionPointEvent():

    def __init__(self,collectionPointId,eventTime,clientId,gatewayType='inout',event='clientIn',extendedData={}):
        self.collectionPointId=collectionPointId
        self.eventTime=eventTime
        self.clientId=clientId
        self.gatewayType=gatewayType
        self.event=event
        self.extendedData=extendedData
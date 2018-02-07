import time

class RfidTag:
    startPosition = 0;

    #def __init__(self,readerResponse):
    def __init__(self,**kwargs):
        readerResponse = kwargs.get('readerResponse',"4416000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        self.uuid=''
        self.createTime = time.time()

        if readerResponse == "4416000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000":
            self.readerResponseSetToDefault = True;

        #print("self.createTime %s" %self.createTime)
        #print "in RfidTag readerResponse = %s" %readerResponse
        if len(readerResponse) < 40:
            raise Exception("reader response does not have enough data")

        #if they passed the whole reader response shift up 4
        if readerResponse.startswith("4416") or readerResponse.startswith("3212"):
            startPosition = 4

        rssiStart = self.startPosition+2
        rssiEnd = rssiStart + 2
        self.rssi = int(readerResponse[rssiStart:rssiEnd],16)
        #print("self.rssi %s" %self.rssi)
        frequencyStart = rssiEnd
        self.frequency = (readerResponse[frequencyStart:frequencyStart+2],readerResponse[frequencyStart+2:frequencyStart+4],readerResponse[frequencyStart+4:frequencyStart+6])
        #print("frequency")
        #print(self.frequency)
        epcLengthStart = self.startPosition + 10
        self.epcLength = int(readerResponse[epcLengthStart:epcLengthStart+2],16)
        #print("self.epcLength %s" %self.epcLength)
        tagUuidStart = self.startPosition + 16
        self.uuid=readerResponse[tagUuidStart:len(readerResponse)]
        #print("self.uuid %s" %self.uuid)



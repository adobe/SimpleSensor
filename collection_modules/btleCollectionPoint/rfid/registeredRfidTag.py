from rfidTag import RfidTag
import time

class RegisteredRfidTag:
    lastRegisteredTime = -1
    tag = None

    def __init__(self,rfidTag):
        self.lastRegisteredTime = time.time()
        self.tag = rfidTag

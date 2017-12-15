"""
Common event to send out about activity from this collection point
author: DaViD bEnGe
date: 6/9/2017

TODO: define this object better
"""
import datetime

class CollectionPointEvent():

    def __init__(self, cpid, cptype, topic, extendedData={}, localOnly=False):
        self._cpid=cpid
        self._cptype=cptype
        self._topic=topic
        self._eventTime='{0}'.format(datetime.datetime.utcnow())
        self._extendedData=extendedData
        self._localOnly=localOnly #this flag triggers the scope of broadcast, some events we dont want to send everywhere and just want to echo to local websocket

    @property
    def cpid(self):
        """Get the id for the collection point that generated the Collection Point Event"""
        return self._cpid

    @cpid.setter
    def cpid(self, value):
        """SetGet the id of the collection point that generated the Collection Point Event"""
        self._cpid = value

    @property
    def cptype(self):
        """Get the Collection Point type"""
        return self.cptype

    @cptype.setter
    def cptype(self, value):
        """Set the Collection Point type"""
        self.cptype = value

    @property
    def topic(self):
        """Get the event topic"""
        return self._topic

    @topic.setter
    def topic(self, value):
        """Set the event topic"""
        self._topic = value

    @property
    def eventTime(self):
        """Get the event creation time"""
        return self._eventTime

    @property
    def localOnly(self):
        """Get localOnly flag from event"""
        return self._localOnly

    @localOnly.setter
    def localOnly(self,value):
        """Set localOnly on event"""
        self._localOnly = value

    @property
    def extendedData(self):
        """Get extended data from event"""
        return self._extendedData

    @extendedData.setter
    def extendedData(self,value):
        """Set extended data from event"""
        self._extendedData = value

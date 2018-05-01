import json
import datetime

""" 
Class for messages between collection points.

"""

class CollectionPointMessage(object):

	def __init__(self, topic, sender, recipients=['all'], extendedData=None, localOnly=False, eventTime=datetime.datetime.utcnow()):
		self._topic = topic
		self._sender = sender
		self._recipients = recipients
		self._extendedData = extendedData
		self._localOnly = localOnly
		self._eventTime='{0}'.format(eventTime)

	def json(self):
		return json.dumps(self.__dict__)
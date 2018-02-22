import json

class SSMSG(object):
	""" 
	Class for messages between collection points.

	"""
	def __init__(self, topic, sender, recipients=['all'], extraData=None, localOnly=False):
		self._topic = topic
		self._sender = sender
		self._recipients = recipients
		self._extraData = extraData
		self._localOnly = localOnly

	def json(self):
		return json.dumps(self.__dict__)

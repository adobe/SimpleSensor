""" 
Message
Common message class for passing events/messages between collection points to 
change variables/workflows, and from collection points to communication 
channels to forward them along to external listeners."""

import datetime
import json
from simplesensor.version import __version__

class Message(object):
	
	def __init__(self, topic, sender_id, sender_type=None, extended_data={}, recipients=['communication_modules'], timestamp=datetime.datetime.now()):
		"""  
		topic (required): message type
		sender_id (required): id property of original sender
		sender_type (optional): type of sender, ie. collection point type, module name, hostname, etc
		extended_data (optional): payload to deliver to recipient(s)
		recipients (optional): module name, which module(s) the message will be delivered to, ie. `websocket_server`.
								use an array of strings to define multiple modules to send to.
								use 'all' to send to all available modules.
								use 'local_only' to send only to modules with `low_cost` prop set to True.
								use 'communication_modules' to send only to communication modules.
								use 'collection_modules' to send only to collection modules.
		"""
		super(Message, self).__init__()
		self.topic = topic
		self.sender_id = sender_id
		self.sender_type = sender_type
		self.extended_data = extended_data
		self.recipients = recipients
		self.ssvn = __version__
		self.timestamp='{0}'.format(timestamp)

	def stringify(self):
		""" Get JSON string dump of the message object. """
		try:
			return json.dumps(self.__dict__)
		except Exception as e:
			print('exception over here fella: ', e)

	def __str__(self):
		""" Allow 'pretty' printing of Message objects. """
		return json.dumps(self.__dict__)
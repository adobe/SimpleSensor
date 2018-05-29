""" 
Message
Common message class for passing events/messages between collection points to 
change variables/workflows, and from collection points to communication 
channels to forward them along to external listeners."""

import datetime
import json

class Message(object):
	
	def __init__(self, topic, sender_id, sender_type=None, extended_data={}, recipients=['all'], timestamp=datetime.datetime.utcnow()):
		"""  
		topic (required): message type
		sender_id (required): id property of original sender
		sender_type (optional): type of sender, ie. collection point type, module name, hostname, etc
		extended_data (optional): payload to deliver to recipient(s)
		recipients (optional): module name, which module(s) the message will be delivered to, ie. `websocket_server`.
								use an array of strings to define multiple modules to send to.
								use ['all'] or 'all' to send to all available modules.
								use ['local_only'] or 'local_only' to send only to modules with `low_cost` prop set to True
		"""
		super(Message, self).__init__()
		self.topic = topic
		self.sender_id = sender_id
		self.sender_type = sender_type
		self.extended_data = extended_data
		self.recipients = recipients
		self.timestamp='{0}'.format(timestamp)

	def stringify(self):
		""" Get JSON string dump of the message object. """
		return json.dumps(self.__dict__)

	def __str__(self):
		""" Allow 'pretty' printing of Message objects. """
		return json.dumps(self.__dict__)

	@property
	def topic(self):
		return self.topic
	@topic.setter
	def topic(self, value):
		self.topic = value

	@property
	def sender_id(self):
		return self.sender_id
	@sender_id.setter
	def sender_id(self, value):
		self.sender_id = value

	@property
	def sender_type(self):
		return self.send_type
	@sender_type.setter
	def sender_type(self, value):
		self.sender_type = value

	@property
	def extended_data(self):
		return self.extended_data
	@extended_data.setter
	def extended_data(self, value):
		self.extended_data = value

	@property
	def recipients(self):
		return self.recipients
	@recipients.setter
	def recipients(self, value):
		self.recipients = value

	@property
	def timestamp(self):
		return self.timestamp
	@timestamp.setter
	def timestamp(self, value):
		self.timestamp = value
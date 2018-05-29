""" 
ConfigLoader
Abstract ConfigLoader implementation.
"""

from .threadsafeLogger import ThreadsafeLogger
import configparser
import os.path
import json

class ConfigLoader(object):
	def __init__(self, name, path, loggingQueue):
		super(ConfigLoader, self).__init__()
		self.name = name
		self.path = path
		self.loggingQueue = loggingQueue

		self.configParser = configparser.ConfigParser()
		self.logger = ThreadsafeLogger(self.loggingQueue, self.name)

	def load(self):
		config = {}
		config = self.load_config(config)
		config = self.load_secrets(config)
		return config

	def load_secrets(self, config):
		return config

	def load_config(self, config):
		return config
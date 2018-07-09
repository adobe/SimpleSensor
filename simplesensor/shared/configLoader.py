""" 
ConfigLoader
Abstract ConfigLoader implementation.
"""

from .threadsafeLogger import ThreadsafeLogger
import configparser
import os.path
import json

class ConfigLoader(object):
	def __init__(self, module_name, config_dir, config_file_names, logging_queue):
		super(ConfigLoader, self).__init__()
		self.moduleName = module_name
		self.configDir = config_dir
		assert type(config_file_names) in {str, list}
		if type(config_file_names) is str: config_file_names = [config_file_names]
		self.fileNames = config_file_names
		self.loggingQueue = logging_queue

		self.configParser = configparser.ConfigParser()
		self.logger = ThreadsafeLogger(self.loggingQueue, "%s-configLoader"%self.moduleName)

	def load(self):
		config = {}
		for file_name in self.fileNames:
			print('filename: ', file_name)
			file_path = os.path.join(self.configDir, file_name)
			try:
				config = self.load_file(config, file_path)
			except Exception as e:
				self.logger.error('Error parsing config path %s : %s'%(file_path, e))
		return config

	def load_file(self, config, file_path):
		""" Loads a file from file_path into the config dict. """
		try:
			with open(file_path) as f:
				self.configParser.readfp(f)
		except IOError:
			self.configParser.read(file_path)

		# _, file = os.path.split(file_path)

		for section in self.configParser.sections():
			if section not in config: config[section] = {}
			for key in self.configParser[section]:
				config[section][self.pascalify(key)] = self.cast_estimated_type(self.configParser.get(section, key))
		return config

	def pascalify(self, astring):
		""" Stupid convert underscore or hyphen divided string to PascalCase. """
		spl = astring.split('_')
		if len(spl)==0: spl = astring.spl('-')
		return ''.join(map(str.capitalize, spl))

	def cast_estimated_type(self, astring):
		""" Placeholder. """
		return astring
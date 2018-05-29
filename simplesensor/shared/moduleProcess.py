""" 
ModuleProcess
Abstract class each module extends.
Implements methods that will always be needed.
"""

from simplesensor.shared.threadsafeLogger import ThreadsafeLogger
from multiprocessing import Process
import time

class ModuleProcess(Process):
	def __init__(self, baseConfig, pInBoundEventQueue, pOutBoundEventQueue, loggingQueue):
		super(ModuleProcess, self).__init__()
		self.config = baseConfig
		self.inQueue = pInBoundEventQueue
		self.outQueue = pOutBoundEventQueue
		self.loggingQueue = loggingQueue
		self.threadProcessQueue = None

		self.alive = False
		self.lowCost = False

		self.logger = ThreadsafeLogger(self.loggingQueue, __name__)

	def listen(self):
		""" Spawn thread to listen for incoming messages. """
		self.alive = True
		self.threadProcessQueue = Thread(target=self.process_queue)
		self.threadProcessQueue.setDaemon(True)
		self.threadProcessQueue.start()

	def shutdown(self):
		""" Handle shutdown message. """
		self.alive = False
		self.threadProcessQueue.join()
		time.sleep(1)
		self.exit = True

	def send_message(self, message):
		self.logger.error('Module `send_message` function is not implemented!')

	def process_queue(self):
		""" Monitor queue of messages from main process to this thread. """

		while self.alive:
			if ~self.inQueue.empty():
				try:
					message = self.inQueue.get(block=False,timeout=1)
					if message:
						if message.topic.upper() == "SHUTDOWN":
							self.shutdown()
						else:
							self.send_message(message)
				except Exception as e:
					self.logger.error('Error getting message: %s'%e)
			else:
				time.sleep(.25)
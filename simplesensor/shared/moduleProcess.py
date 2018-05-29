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

		self.listenForIncoming = True
		self.alive = False
		self.lowCost = False

		self.logger = ThreadsafeLogger(self.loggingQueue, __name__)

	def run(self):
		""" Process entry point. """
		self.alive = True
		if self.listenForIncoming:
			self.listen()

	def low_cost(self):
		""" lowCst property getter """
		return self.lowCost

	def listen(self):
		""" Spawn thread to listen for incoming messages. """
		self.threadProcessQueue = Thread(target=self.process_queue)
		self.threadProcessQueue.setDaemon(True)
		self.threadProcessQueue.start()

	def shutdown(self):
		""" Handle shutdown message. """
		self.alive = False
		if self.listenForIncoming:
			self.threadProcessQueue.join()
		time.sleep(1)
		self.exit = True

	def send_message(self, message):
		""" Put outgoing message onto outgoing queue. """
		self.outQueue.put(message)

	def handle_message(self, message):
		""" Handle incoming message.
		This function should be overridden. """
		self.logger.error('Error: Message not handled, '
			+ 'handle_message function not implemented')

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
							self.handle_message(message)
				except Exception as e:
					self.logger.error('Error getting message: %s'%e)
			else:
				time.sleep(.25)
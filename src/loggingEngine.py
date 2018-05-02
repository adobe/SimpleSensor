'''
Threadsafe logging engine
'''
import logging
import logging.config
import multiprocessing
import time
from threading import Thread
import os.path

class LoggingEngine(Thread):

    def __init__(self, loggingQueue):
        super(LoggingEngine, self).__init__()
        self.alive = True
        self.queue = loggingQueue

        try:
            logging.config.fileConfig("./config/logging.conf")
        except:
            logging.config.fileConfig(os.path.join(os.path.dirname(__file__),"./config/logging.conf"))
        self.logger = logging.getLogger('main')

    def run(self):
        """ Main thread entry point.
        Starts watching logging queue and printing to console
        """
        self.logger.info("Starting %s" % (__name__),extra={"loggername":"LoggingEngine"})
        self.alive = True
 
        #start up the queue read loop thread
        self.processQueue()

        return

    def shutdown(self):
        """ Declare thread dead, shutdown. """
        self.logger.info("Shutting down LoggingEngine", extra={"loggername":"LoggingEngine"})
        self.alive = False
        time.sleep(1)
        self.exit = True

    def processQueue(self):
        """ Process queue of logger messages """
        while self.alive:
            if (self.queue.empty() == False):
                try:
                    message = self.queue.get(block=False, timeout=1)
                    if message is not None:
                        if message == "SHUTDOWN":
                            self.logger.debug("SHUTDOWN handled", extra={"loggername":"LoggingEngine"})
                            self.shutdown()
                        else:
                            self.logger.log(message['level'], message['msg'], extra=message['extra'])

                except Exception as e:
                    self.logger.warn("LoggingEngine unable to read queue : %s " %e, extra={"loggername":"LoggingEngine"})
            else:
                time.sleep(.25)

        return

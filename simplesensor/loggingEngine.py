'''
LoggingEngine
Loads logging module config from file, reads logging messages from all threads and outputs them to stdout.
'''
from threading import Thread
import multiprocessing
import logging
import logging.config
import time
import os.path

class LoggingEngine(Thread):

    def __init__(self, loggingQueue):

        super(LoggingEngine, self).__init__()

        self.alive = True
        self.queue = loggingQueue

        try:
            print('os.path.dirname: ', os.path.dirname(__file__))
            conf_path = os.path.join(os.path.dirname(__file__), 'config', 'logging.conf')
            print('conf path: ', conf_path)
            logging.config.fileConfig(conf_path)
        except Exception as e:
            print('Exception loading logging config: ', e)
        self.logger = logging.getLogger('main')

    def run(self):
        """ Main thread entry point.
        Starts watching logging queue and printing to console
        """
        self.logger.info("Starting %s" % (__name__), extra={"loggername":"LoggingEngine"})
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

'''
LoggingEngine
Loads logging module config from file, reads logging messages from all threads and outputs them to stdout.
'''
from threading import Thread
from simplesensor.shared.message import Message
from multiprocessing import Process
import logging
import logging.config
import time
import os
import os.path

class LoggingEngine(Thread):

    def __init__(self, loggingQueue, config):

        super(LoggingEngine, self).__init__()

        self.config = config
        self.alive = True
        self.queue = loggingQueue

        try:
            conf_path = os.path.join(os.path.dirname(__file__), 'config', 'logging.conf')
            logging.config.fileConfig(conf_path)
        except Exception as e:
            print('Exception loading logging config: ', e)
        self.logger = logging.getLogger('main')

        if os.name is 'posix':
            # set streamhandler terminators on posix systems
            for handler in self.logger.handlers:
                if type(handler) is logging.StreamHandler:
                    handler.terminator = '\r\n'

        # add file handler
        try:
            file = os.path.abspath(os.path.expanduser(self.config['DefaultLog']))
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            fhandler = logging.handlers.RotatingFileHandler(
                filename=file, 
                encoding='utf8',
                maxBytes=10485760,
                backupCount=5)
            self.logger.addHandler(fhandler)
        except Exception as e:
            print('Exception loading file handler: ', e)


    def run(self):
        """ Main thread entry point.
        Starts watching logging queue and printing to console
        """
        self.logger.info("Starting %s" % (__name__), extra={"loggername":"LoggingEngine"})
        self.alive = True
 
        #start up the queue read loop thread
        self.process_queue()

        return

    def shutdown(self):
        """ Declare thread dead, shutdown. """
        self.logger.info("Shutting down LoggingEngine", extra={"loggername":"LoggingEngine"})
        self.alive = False
        time.sleep(1)
        self.exit = True

    def process_queue(self):
        """ Process queue of logger messages """
        while self.alive:
            if (self.queue.empty() == False):
                try:
                    message = self.queue.get(block=False, timeout=1)
                    if message is not None:
                        if type(message) is Message and message.topic.upper() == "SHUTDOWN":
                            self.logger.debug("SHUTDOWN handled", extra={"loggername":"LoggingEngine"})
                            self.shutdown()
                        else:
                            self.logger.log(message['level'], message['msg'], extra=message['extra'])

                except Exception as e:
                    self.logger.warn("LoggingEngine unable to read queue : %s " %e, extra={"loggername":"LoggingEngine"})
            else:
                time.sleep(.25)

        return

"""
ThreadsafeLogger
Facade to a queue to allow adding messages to a multiprocess message queue.
"""
from logging import INFO, DEBUG, CRITICAL, WARNING, WARN, ERROR

__version__ = '1.0.0'

class ThreadsafeLogger(object):

    def __init__(self, q, name="no name given"):
        self.q = q
        self.loggerName = name
        self.extra = {"loggername":self.loggerName}

    def info(self, msg):
        self.q.put({'level':INFO,'msg':msg,'extra':self.extra})

    def debug(self, msg):
        self.q.put({'level':DEBUG,'msg':msg,'extra':self.extra})

    def critical(self, msg):
        self.q.put({'level':CRITICAL,'msg':msg,'extra':self.extra})

    def warning(self, msg):
        self.q.put({'level':WARNING,'msg':msg,'extra':self.extra})

    def warn(self, msg):
        self.q.put({'level':WARN,'msg':msg,'extra':self.extra})

    def error(self, msg):
        self.q.put({'level':ERROR,'msg':msg,'extra':self.extra})

    

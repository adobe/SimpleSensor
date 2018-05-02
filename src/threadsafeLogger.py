"""
simple facade to a queue to enable multi process logging
author: DaViD bEnGe
date: 9/7/2017

"""
import logging

__version__ = '1.0.0'

class ThreadsafeLogger(object):

    def __init__(self, q, name="no name given"):
        self.q = q
        self.loggerName = name
        self.extra = {"loggername":self.loggerName}

    def info(self, msg):
        self.q.put({'level':logging.INFO,'msg':msg,'extra':self.extra})

    def debug(self, msg):
        self.q.put({'level':logging.DEBUG,'msg':msg,'extra':self.extra})

    def critical(self, msg):
        self.q.put({'level':logging.CRITICAL,'msg':msg,'extra':self.extra})

    def warning(self, msg):
        self.q.put({'level':logging.WARNING,'msg':msg,'extra':self.extra})

    def warn(self, msg):
        self.q.put({'level':logging.WARN,'msg':msg,'extra':self.extra})

    def error(self, msg):
        self.q.put({'level':logging.ERROR,'msg':msg,'extra':self.extra})

    

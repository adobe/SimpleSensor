import multiprocessing as mp
import sys
from importlib import import_module
from collectionPointEvent import CollectionPointEvent
import time
from loggingEngine import LoggingEngine
from threadsafeLogger import ThreadsafeLogger
import msvcrt
from select import select
import configLoader

# List of threads to handle
threads = []

# Dict of threadsafe queues to handle
queues = {}

# Logging queue setup
loggingQueue = mp.Queue()
logger = ThreadsafeLogger(loggingQueue, "main")

# Logging output engine
loggingEngine = LoggingEngine(loggingQueue=loggingQueue)
threads.append(loggingEngine)
loggingEngine.start()

# Config
baseConfig = configLoader.load(logger)

_collectionModuleNames = baseConfig['CollectionModules']
_communicationModuleNames = baseConfig['CommunicationModules']
_collectionModules = {}
_communicationModules = {}

# Collection point queues
cpEventOutboundChannel=mp.Queue()
cpEventInboundChannel=mp.Queue()

# For each collection module, import, initialize
for moduleName in _collectionModuleNames:
    try:
        sys.path.append('./collection_modules/%s'%moduleName)
        _collectionModules[moduleName] = import_module('collection_modules.%s'%moduleName)

        queues[moduleName] = {}
        # queues[moduleName]['in'] = mp.Queue()
        queues[moduleName]['out'] = mp.Queue()
    except Exception as e:
        logger.error('Error importing %s: %s'%(moduleName, e))

# For each collection module, import, initialize, and create an in/out queue
for moduleName in _communicationModuleNames:
    try:
        logger.debug('importing %s'%(moduleName))
        sys.path.append('./communication_modules/%s'%moduleName)
        _communicationModules[moduleName] = import_module('communication_modules.%s'%moduleName)

        queues[moduleName] = {}
        queues[moduleName]['in'] = mp.Queue()
        queues[moduleName]['out'] = mp.Queue()
    except Exception as e:
        logger.error('Error importing %s: %s'%(moduleName, e))


alive = True

def sendOutboundEventMessage(msg):

    """ Put outbound message onto queues of all active communication channel threads.
    Always send string messages, as they are control messages like 'shutdown'.
    """

    #TODO: Define local channels
    # logger.debug('message: %s'%msg)
    for moduleName in _communicationModuleNames:
        if type(msg) is str or not msg.localOnly:
            queues[moduleName]['out'].put_nowait(msg)
            logger.debug("%s queue size is %s"%(moduleName, queues[moduleName]['out'].qsize()))

def loadCommunicationChannels():
    """ Create a thread for each communication channel specified in base.conf """

    for moduleName in _communicationModuleNames:
        logger.info('Loading communication module : %s'%moduleName)
        thread = _communicationModules[moduleName].CommunicationMethod(baseConfig, 
                                                   queues[moduleName]['out'], 
                                                   queues[moduleName]['in'], 
                                                   loggingQueue)
        threads.append(thread)
        thread.start()

def loadCollectionPoints():
    """ Load collection points.
    Currently loads and monitors only one collection point/queue.
    May extend this to multiple collection points in the future.

    If there are multiple collection points, use a unique queue for the outbound
    messages for each of them, and one queue for inbound messages. 
    """
    for moduleName in _collectionModuleNames:
        try:
            logger.info('Loading collection module : %s'%moduleName)
            thread = _collectionModules[moduleName].CollectionMethod(baseConfig, 
                                                    queues[moduleName]['out'], 
                                                    cpEventInboundChannel, 
                                                    loggingQueue)
            threads.append(thread)
            thread.start()

        except Exception as e:
            print(e)
            logger.error('Error importing %s: %s'%(moduleName, e))

def getch():
    """ Returns a character from keyboard buffer. """
    return sys.stdin.read(1)

def kbhit():
    """ Returns a non-zero integer if a key is in the keyboard buffer. """
    dr,dw,de = select([sys.stdin], [], [], 0)
    return dr

def main():
    """ Main control logic. 

    Initiate all communication channels and collection point.
    Loop to monitor messages from collection point, 
    handing them off to communication channels as they come in.
    """

    logger.info('Loading communication channels')
    loadCommunicationChannels()

    logger.info("Loading collection points")
    loadCollectionPoints()

    while alive:
        #TODO: Remove Windows dependency to catch esc key
        if msvcrt.kbhit():
            ch = msvcrt.getwche()
            if ch == u'\x1b':
                break
                shutdown()

        # Listen to main collection point for events
        if (cpEventInboundChannel.empty() == False):
            try:
                message = cpEventInboundChannel.get(block=False,timeout=1)
                if message is not None:
                    if message == "SHUTDOWN":
                        logger.info("SHUTDOWN handled")
                        shutdown()
                    else:
                        sendOutboundEventMessage(message)
            except Exception as e:
                logger.error("Main unable to read queue : %s " %e)
        else:
            time.sleep(.25)

    shutdown()

def shutdown():
    """ Send shutdown message to all communication channel threads
    and collection points, join and exit them. 
    """

    logger.info("Shutting down main process")

    # Send to communication methods
    sendOutboundEventMessage("SHUTDOWN")

    # Send to collection methods
    for moduleName in _collectionModuleNames:
        queues[moduleName]['out'].put_nowait("SHUTDOWN")

    alive = False
    
    for t in threads:
        t.join(timeout=1.0)

    loggingQueue.put_nowait("SHUTDOWN")
    sys.exit(0)

if __name__ == '__main__':
    """ Main entry point for running on cmd line. """
    python_version = sys.version_info.major
    if python_version == 3:
        main()
    else:
        logger.error("You need to run Python version 3.x!  Your trying to run this with major version %s" % python_version)
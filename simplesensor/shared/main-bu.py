"""
Main
Program entrypoint
"""

from src.collectionPointEvent import CollectionPointEvent
from src.threadsafeLogger import ThreadsafeLogger
from src.loggingEngine import LoggingEngine
from importlib import import_module
import multiprocessing as mp
from src import configLoader
from threading import Thread
import time
import sys

def start():
    python_version = sys.version_info.major
    if python_version == 3:
        initialize()
        start_input_thread()
        import_modules()
        alive = True
        mp.set_start_method('fork')
        main()
    else:
        logger.error("You need to run Python version 3.x!  Your trying to run this with major version %s" % python_version)

def initialize():
    # List of processes to handle
    processes = []

    # Dict of threadsafe queues to handle
    queues = {}

    # Logging queue setup
    loggingQueue = mp.Queue()
    logger = ThreadsafeLogger(loggingQueue, "main")

    # Logging output engine
    loggingEngine = LoggingEngine(loggingQueue=loggingQueue)
    processes.append(loggingEngine)
    loggingEngine.start()

    # Config
    baseConfig = configLoader.load(loggingQueue, "main")

    _collectionModuleNames = baseConfig['CollectionModules']
    print('collectrion module names: ', _collectionModuleNames)
    _communicationModuleNames = baseConfig['CommunicationModules']
    print('communication module names: ', _communicationModuleNames)
    _collectionModules = {}
    _communicationModules = {}

    # Collection point queues
    cpEventOutboundChannel=mp.Queue()
    cpEventInboundChannel=mp.Queue()
    comEventInboundChannel=mp.Queue()

def _find_getch():
    """ Returns a getch function for the system in use. """
    try:
        import termios
    except ImportError:
        # Return Windows' getch
        import msvcrt
        return msvcrt.getch

    # Create and return a getch that manipulates the tty
    import tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

def process_input(toexit, getch):
    """ Process keystrokes, exit on esc key. """
    ch = getch()
    if ch == b'\x1b':
        toexit.append(True)

def start_input_thread():
    # Set up input thread to watch for esc key
    toExit=[]
    inputThread = Thread(target=process_input, args=(toExit, _find_getch()))
    inputThread.setDaemon(True)
    inputThread.start()

def import_modules():
    # For each collection module, import, initialize
    for moduleName in _collectionModuleNames:
        try:
            logger.debug('importing %s'%(moduleName))
            sys.path.append('./src/collection_modules/%s'%moduleName)
            _collectionModules[moduleName] = import_module('src.collection_modules.%s'%moduleName)

            queues[moduleName] = {}
            # queues[moduleName]['in'] = mp.Queue()
            queues[moduleName]['out'] = mp.Queue()
        except Exception as e:
            logger.error('Error importing %s: %s'%(moduleName, e))

    # For each collection module, import, initialize, and create an in/out queue
    for moduleName in _communicationModuleNames:
        try:
            logger.debug('importing %s'%(moduleName))
            sys.path.append('./src/communication_modules/%s'%moduleName)
            _communicationModules[moduleName] = import_module('src.communication_modules.%s'%moduleName)

            queues[moduleName] = {}
            # queues[moduleName]['in'] = mp.Queue()
            # queues[moduleName]['in'] = comEventInboundChannel
            queues[moduleName]['out'] = mp.Queue()
        except Exception as e:
            logger.error('Error importing %s: %s'%(moduleName, e))

def sendOutboundEventMessage(msg, recipients=['all']):

    """ Put outbound message onto queues of all active communication channel threads.
    Always send string messages, as they are control messages like 'shutdown'.
    """
    if type(msg) == CollectionPointEvent or recipients == ['all']:
        # Send to all communication channels
        for moduleName in _communicationModuleNames:
            try:
                if type(msg) is str or not msg._localOnly:
                    queues[moduleName]['out'].put_nowait(msg)
                    logger.debug("%s queue size is %s"%(moduleName, queues[moduleName]['out'].qsize()))
            except Exception as e:
                logger.error('Error adding message to all module queues %s'%e)
    else:
        for recipient in recipients:
            try:
                queues[recipient]['out'].put_nowait(msg)
                logger.debug("%s queue size is %s"%(recipient, queues[recipient]['out'].qsize()))
            except Exception as e:
                logger.error('Error adding message to queue: %s'%e)

def loadCommunicationChannels():
    """ Create a process for each communication channel specified in base.conf """

    for moduleName in _communicationModuleNames:
        logger.info('Loading communication module : %s'%moduleName)
        proc = _communicationModules[moduleName].CommunicationModule(baseConfig, 
                                                   queues[moduleName]['out'], 
                                                   # queues[moduleName]['in'],
                                                   comEventInboundChannel, 
                                                   loggingQueue)
        processes.append(proc)
        proc.start()

def loadCollectionPoints():
    """ Create a new process for each collection point module specified in base.conf """
    for moduleName in _collectionModuleNames:
        try:
            logger.info('Loading collection module : %s'%moduleName)
            proc = _collectionModules[moduleName].CollectionModule(baseConfig, 
                                                    queues[moduleName]['out'], 
                                                    cpEventInboundChannel, 
                                                    loggingQueue)
            processes.append(proc)
            proc.start()

        except Exception as e:
            print(e)
            logger.error('Error importing %s: %s'%(moduleName, e))

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

    while alive and not toExit:
        # Listen to inbound message queues for messages
        if (cpEventInboundChannel.empty() == False):
            try:
                message = cpEventInboundChannel.get(block=False, timeout=1)
                if message is not None:
                    if message == "SHUTDOWN":
                        logger.info("SHUTDOWN handled")
                        shutdown()
                    else:
                        sendOutboundEventMessage(message)
            except Exception as e:
                logger.error("Unable to read collection point queue : %s " %e)

        elif (comEventInboundChannel.empty() == False):
            try:
                message = comEventInboundChannel.get(block=False, timeout=1)
                if message is not None:
                    if message == "SHUTDOWN":
                        logger.info("SHUTDOWN handled")
                        shutdown()
                    else:
                        sendOutboundEventMessage(message, message._recipients)
            except Exception as e:
                logger.error("Unable to read communication channel queue : %s " %e)
        else:
            time.sleep(.25)

    shutdown()

def shutdown():
    """ Send shutdown message to all communication channel threads
    and collection points, join and exit them. 
    """

    logger.info("Shutting down main process")

    # Send to communication methods
    sendOutboundEventMessage("SHUTDOWN", ['all'])

    # Send to collection methods
    for moduleName in _collectionModuleNames:
        queues[moduleName]['out'].put_nowait("SHUTDOWN")

    loggingQueue.put_nowait("SHUTDOWN")

    killProcesses()
    alive = False

    sys.exit(0)

def killProcesses():
    """ Wait for each process to die until timeout is reached, then terminate. """
    print('Killing processes...')
    timeout = 5
    for p in processes:
        p_sec = 0
        for second in range(timeout):
            if p.is_alive():
                time.sleep(1)
                p_sec += 1
        if p_sec >= timeout:
            print('Terminating process %s'%p)
            p.terminate()

if __name__ == '__main__':
    """ Main entry point for running on cmd line. """
    python_version = sys.version_info.major
    if python_version == 3:
        main()
    else:
        logger.error("You need to run Python version 3.x!  Your trying to run this with major version %s" % python_version)

    # Set multiprocessing start method
    mp.set_start_method('fork')
"""
Main
Program entrypoint. 
Can be run with `python main.py`
Or through the CLI with `scly start` after installing.
"""

from simplesensor.shared.threadsafeLogger import ThreadsafeLogger
from simplesensor.loggingEngine import LoggingEngine
from simplesensor.shared.message import Message
from importlib import import_module
import multiprocessing as mp
from simplesensor import configLoader
from threading import Thread
import simplesensor
import time
import sys
import os.path

# Dict of processes, threadsafe queues to handle
# Keys will be the module names
processes = {}
queues = {}

# Define a single inbound message queue for each of the module types.
# These are shared among modules since the messages should come in order.
# The main process (main.py) handles forwarding inbound messages to the correct recipient(s).
queues['cpInbound']=mp.Queue()
queues['comInbound']=mp.Queue()

# Logging queue setup
queues['logging'] = mp.Queue()
logger = ThreadsafeLogger(queues['logging'], "main")

# Logging output engine
loggingEngine = LoggingEngine(loggingQueue=queues['logging'])
processes['logging'] = loggingEngine
loggingEngine.start()

# Config
baseConfig = configLoader.load(queues['logging'], "main")

_collectionModuleNames = baseConfig['CollectionModules']
_communicationModuleNames = baseConfig['CommunicationModules']
if len(_collectionModuleNames)==0 or len(_communicationModuleNames)==0:
    logger.warn('Without at least one of each communication and' 
        + 'collection modules active, SimpleSensor does not do much.'
        + 'Use command `scly config --name base` to configure modules.'
        + 'Use command `scly install --name <some_branch> --type <communication/collection>` '
        + 'to install a module. See https://github.com/AdobeAtAdobe/SimpleSensor/blob/master/README.md'
        + 'for more details.')

_collectionModules = {}
_communicationModules = {}

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

getch = _find_getch()

def process_input(toexit):
    """ Process keystrokes, exit on esc key. """
    ch = getch()
    if ch == b'\x1b':
        toexit.append(True)

# Set up input thread to watch for esc key
toExit=[]
inputThread = Thread(target=process_input, args=(toExit,))
inputThread.setDaemon(True)
inputThread.start()

# For each collection module, import, initialize
for moduleName in _collectionModuleNames:
    try:
        logger.debug('importing %s'%(moduleName))
        _collectionModules[moduleName] = import_module('simplesensor.collection_modules.%s'%moduleName)

        queues[moduleName] = {}
        # Each module has it's own incoming message queue (outbound from main proc)
        # This is for cases where messages should be handled by specific modules, not all.
        queues[moduleName]['out'] = mp.Queue()
    except Exception as e:
        logger.error('Error importing %s: %s'%(moduleName, e))

# For each collection module, import, initialize, and create an in/out queue
for moduleName in _communicationModuleNames:
    try:
        logger.debug('importing %s'%(moduleName))
        _communicationModules[moduleName] = import_module('simplesensor.communication_modules.%s'%moduleName)

        queues[moduleName] = {}
        queues[moduleName]['out'] = mp.Queue()
    except Exception as e:
        logger.error('Error importing %s: %s'%(moduleName, e))

alive = True

def send_message(message):

    """ Put outbound message onto queues of all active communication channel threads,
    or the modules defined in the recipients field of the message.
    Always send string messages, as they are control messages like 'SHUTDOWN'.
    """

    if type(message.recipients) == str: message.recipients = [message.recipients]
    if message.recipients == ['all']:
        # Send to all communication channels
        for moduleName in _communicationModuleNames:
            try:
                queues[moduleName]['out'].put_nowait(msg)
                logger.debug("%s queue size is %s"%(moduleName, queues[moduleName]['out'].qsize()))
            except Exception as e:
                logger.error('Error adding message to module %s queue: %s'%(moduleName, e))

    elif message.recipients == ['local_only']:
        # Send to all channels with property `low_cost` set to True
        for moduleName in _communicationModuleNames:
            if processes[moduleName].low_cost() == True:
                try:
                    queues[moduleName]['out'].put_nowait(msg)
                    logger.debug("%s queue size is %s"%(moduleName, queues[moduleName]['out'].qsize()))
                except Exception as e:
                    logger.error('Error adding message to %s queue: %s'%(moduleName, e))

    else:
        # Send to the set recipients
        for recipient in message.recipients:
            try:
                queues[recipient]['out'].put_nowait(msg)
                logger.debug("%s queue size is %s"%(recipient, queues[recipient]['out'].qsize()))
            except Exception as e:
                logger.error('Error adding message to %s queue: %s'%(recipient, e))

def load_communication_channels():
    """ Create a process for each communication channel specified in base.conf """

    for moduleName in _communicationModuleNames:
        try:
            logger.info('Loading communication module : %s'%moduleName)
            proc = _communicationModules[moduleName].CommunicationModule(baseConfig, 
                                                       queues[moduleName]['out'], 
                                                       queues['comInbound'], 
                                                       queues['logging'])
            print('websocket_server.thing: ', proc.thing)
            processes[moduleName] = proc
            proc.start()

        except Exception as e:
            logger.error('Error importing %s: %s'%(moduleName, e))

def load_collection_points():
    """ Create a new process for each collection point module specified in base.conf """
    for moduleName in _collectionModuleNames:
        try:
            logger.info('Loading collection module : %s'%moduleName)
            proc = _collectionModules[moduleName].CollectionModule(baseConfig, 
                                                    queues[moduleName]['out'], 
                                                    queues['cpInbound'], 
                                                    queues['logging'])
            processes[moduleName] = proc
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
    load_communication_channels()

    logger.info("Loading collection points")
    load_collection_points()

    while alive and not toExit:
        # Listen to inbound message queues for messages
        if (queues['cpInbound'].empty() == False):
            try:
                message = queues['cpInbound'].get(block=False, timeout=1)
                if message is not None:
                    if message == "SHUTDOWN":
                        logger.info("SHUTDOWN handled")
                        shutdown()
                    else:
                        send_message(message)
            except Exception as e:
                logger.error("Unable to read collection point queue : %s " %e)

        elif (queues['comInbound'].empty() == False):
            try:
                message = queues['comInbound'].get(block=False, timeout=1)
                if message is not None:
                    if message == "SHUTDOWN":
                        logger.info("SHUTDOWN handled")
                        shutdown()
                    else:
                        send_message(message)
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
    event = Event(topic='SHUTDOWN', sender_id='main')
    send_message(event)

    # Send to collection methods
    for moduleName in _collectionModuleNames:
        queues[moduleName]['out'].put_nowait("SHUTDOWN")

    queues['logging'].put_nowait("SHUTDOWN")

    kill_processes()
    alive = False

    sys.exit(0)

def kill_processes():
    """ Wait for each process to die until timeout is reached, then terminate. """
    print('Killing processes...')
    timeout = 5
    for name, proc in processes.items():
        p_sec = 0
        for second in range(timeout):
            if proc.is_alive():
                time.sleep(1)
                p_sec += 1
        if p_sec >= timeout:
            print('Terminating process %s - %s'%(name, proc))
            proc.terminate()

def start():
    """ Main entry point for running on cmd line. """
    python_version = sys.version_info.major
    if python_version == 3:
        main()
    else:
        logger.error("You need to run Python version 3.x!  Your trying to run this with major version %s" % python_version)

    # Set multiprocessing start method
    mp.set_start_method('fork')

if __name__ == '__main__':
    """ Main entry point for running on cmd line. """
    start()
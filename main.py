import multiprocessing as mp
import sys
import os
import inspect
from websocketServer import CecIotWebsocketServer
from azureIotHub import AzureIotHubConnectionThread
from collectionPointEvent import CollectionPointEvent
import time
from loggingEngine import LoggingEngine
from threadsafeLogger import ThreadsafeLogger
from cv2 import waitKey
import msvcrt
import configNormalizer
from mqtt import MQTTClient

# List of threads to handle
threads = []

# Logging queue setup
loggingQueue = mp.Queue()
logger = ThreadsafeLogger(loggingQueue,"main")

# Logging output engine
loggingEngine = LoggingEngine(loggingQueue=loggingQueue)
threads.append(loggingEngine)
loggingEngine.start()

# Config
baseConfig = configNormalizer.loadConfig(logger)

# Add collection point modules to path
for module in baseConfig['Modules']:
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], os.path.join("collection_modules", module))))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

# Import main collection point
from camCollectionPoint import CamCollectionPoint as CollectionPoint

# Queues
websocketEventOutboundChannel=mp.Queue()
websocketEventInboundChannel=mp.Queue()
azureEventOutboundChannel=mp.Queue()
mqttEventOutboundChannel=mp.Queue()
cpEventOutboundChannel=mp.Queue()
cpEventInboundChannel=mp.Queue()
threadWebsocketServer = None
threadAzureIotHubConnection = None
mainCollectionPoint = None
alive = True

# Constants
_useAzure = baseConfig['UseAzure']
_useMqtt = baseConfig['UseMqtt']
_exposeWebsocket = baseConfig['ExposeWebsocket']

def sendOutboundEventMessage(msg):

    """ Put outbound message onto queues of all active communication channel threads.
    Always send string messages, as they are control messages like 'shutdown'.
    """

    #TODO: Make communication channels modular, define local channels

    if _useAzure is True:
        if type(msg) is str or not msg.localOnly:
            azureEventOutboundChannel.put_nowait(msg)

    if _useMqtt:
        if type(msg) is str or not msg.localOnly:
            mqttEventOutboundChannel.put_nowait(msg)

    if _exposeWebsocket:
        websocketEventOutboundChannel.put_nowait(msg)

    logger.debug("Websocket queue size is %s, Azure queue size is %s, MQTT queue size is %s" % (
        websocketEventOutboundChannel.qsize(),
        azureEventOutboundChannel.qsize(), 
        mqttEventOutboundChannel.qsize()))

def shutdown():

    """ Send shutdown message to all communication channel threads, join and exit them. """

    logger.info("Shutting down main process")
    sendOutboundEventMessage("SHUTDOWN")
    cpEventOutboundChannel.put_nowait("SHUTDOWN")
    alive = False
    
    for t in threads:
        t.join(timeout=1.0)

    loggingQueue.put_nowait("SHUTDOWN")
    sys.exit(0)

def loadCommunicationChannels():

    """ Create a thread for each communication channel specified in base.conf """

    if _useAzure:
        azureIotThread = AzureIotHubConnectionThread(baseConfig,azureEventOutboundChannel,None,loggingQueue)
        threads.append(azureIotThread)
        azureIotThread.start()

    if _useMqtt:
        mqttThread = MQTTClient(baseConfig, mqttEventOutboundChannel, None, loggingQueue)
        threads.append(mqttThread)
        mqttThread.start()

    if _exposeWebsocket:
        websocketThread = CecIotWebsocketServer(baseConfig,websocketEventOutboundChannel,websocketEventInboundChannel, loggingQueue)
        threads.append(websocketThread)
        websocketThread.start()

def main():

    """ Main control logic. 

    Initiate all communication channels and collection point.
    Loop to monitor messages from collection point, 
    handing them off to communication channels as they come in.
    """

    logger.info('Loading communication channels')
    loadCommunicationChannels()

    logger.info("Starting main collection point process")
    mainCollectionPoint = CollectionPoint(baseConfig, cpEventInboundChannel, cpEventOutboundChannel, loggingQueue)
    threads.append(mainCollectionPoint)
    mainCollectionPoint.start()

    while alive:
        #TODO: Remove Windows dependency to catch esc key
        if msvcrt.kbhit():
            ch = msvcrt.getwche()
            if ch == u'\x1b':
                logger.info("Handing request to shutdown")
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

if __name__ == '__main__':
    """ Main entry point for Windows. """
    python_version = sys.version_info.major
    if python_version == 3:
        main()
    else:
        logger.error("You need to run Python version 3.x!  Your trying to run this with major version %s" % python_version)
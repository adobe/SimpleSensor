"""
Websocket server for local event broadcast
author: DaViD bEnGe + MaX
date: 6/6/2017

https://github.com/Pithikos/python-websocket-server

"""
from multiprocessing import Process
import time
from threading import Thread
import sys
import json
from websocket_server import WebsocketServer
from threadsafeLogger import ThreadsafeLogger
from ssmsg import SSMSG

class WebsocketServerModule(Process):

    def __init__(self, baseConfig, pInBoundEventQueue, pOutBoundEventQueue, loggingQueue):

        super(WebsocketServerModule, self).__init__()
        self.alive = True
        self.config = baseConfig
        self.inQueue = pInBoundEventQueue  # inQueue are messages from the main process to websocket clients
        self.outQueue = pOutBoundEventQueue  # outQueue are messages from clients to main process
        self.websocketServer = None
        self.loggingQueue = loggingQueue
        self.threadProcessQueue = None

        # Constants
        self._port = self.config['WebsocketPort']
        self._host = self.config['WebsocketHost']

        # logging setup
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

    def run(self):

        """ Main thread entry point.

        Sets up websocket server and event callbacks.
        Starts thread to monitor inbound message queue.
        """

        self.logger.info("Starting websocket %s" % __name__)
        self.websocketServer = WebsocketServer(self._port, host=self._host)
        self.websocketServer.set_fn_new_client(self.newWebSocketClient)
        self.websocketServer.set_fn_message_received(self.websocketMessageReceived)
        self.alive = True

        self.threadProcessQueue = Thread(target=self.processQueue)
        self.threadProcessQueue.setDaemon(True)
        self.threadProcessQueue.start()

        self.websocketServer.run_forever()

    def newWebSocketClient(self, client, server):
        """ Client joined callback - called whenever a new client joins. """

        self.logger.debug("Client joined")

    def websocketMessageReceived(self, client, server, message):
        """ Message received callback - called whenever a new message is received. """

        self.logger.debug('Message received: %s'%message)
        # topic sender recipient extradata localonly
        message = json.loads(message)
        _msg = SSMSG(
            message['data']['_topic'], 
            message['data']['_sender'], 
            message['data']['_recipients'], 
            message['data']['_extraData'], 
            False)
        self.outQueue.put_nowait(_msg)

    def shutdown(self):
        """ Handle shutdown message. 
        Close and shutdown websocket server.
        Join queue processing thread.
        """

        self.logger.info("Shuting down websocket server %s" % __name__)

        try:
            self.logger.info("Closing websocket")
            self.websocketServer.server_close()
        except Exception as e:
            self.logger.error("Websocket close error : %s " %e)

        try:
            self.logger.info("Shutdown websocket")
            self.websocketServer.shutdown()
        except Exception as e:
            self.logger.error("Websocket shutdown error : %s " %e)

        self.alive = False
        
        self.threadProcessQueue.join()

        time.sleep(1)
        self.exit = True

    def sendOutMessage(self, message):
        """ Send message to listening clients. """
        self.websocketServer.send_message_to_all(json.dumps(message.__dict__))

    def processQueue(self):
        """ Monitor queue of messages from main process to this thread. """

        while self.alive:
            if (self.inQueue.empty() == False):
                try:
                    message = self.inQueue.get(block=False,timeout=1)
                    if message is not None:
                        if message == "SHUTDOWN":
                            self.logger.debug("SHUTDOWN handled")
                            self.shutdown()
                        else:
                            self.sendOutMessage(message)
                except Exception as e:
                    self.logger.error("Websocket unable to read queue : %s " %e)
            else:
                time.sleep(.25)

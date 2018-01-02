"""
Threaded MQTT client
author: MaX EdeLL
date: 12/12/2017
"""

import logging
import time
import json
from threading import Thread
import paho.mqtt.client as mqtt
from threadsafeLogger import ThreadsafeLogger


class MQTTClientModule(Thread):
    """ Threaded MQTT client for processing and publishing outbound messages"""

    def __init__(self, baseConfig, pInBoundEventQueue, pOutBoundEventQueue, loggingQueue):

        super(MQTTClientModule, self).__init__()
        self.config = baseConfig
        self.alive = True
        self.inQueue = pInBoundEventQueue

        # Constants
        self._keepAlive = self.config['MqttKeepAlive']
        self._feedName = self.config['MqttFeedName']
        self._username = self.config['MqttUsername']
        self._key = self.config['MqttKey']
        self._host = self.config['MqttHost']
        self._port = self.config['MqttPort']
        self._publishJson = self.config['MqttPublishJson']
        self._publishFaceValues = self.config['MqttPublishFaceValues']

        # MQTT setup
        self._client = mqtt.Client()
        self._client.username_pw_set(self._username, self._key)
        self._client.on_connect    = self.onConnect
        self._client.on_disconnect = self.onDisconnect
        self._client.on_message    = self.onMessage
        self.mqttConnected = False

        # Logging setup
        self.logger = ThreadsafeLogger(loggingQueue, "MQTT")

    def onConnect(self, client, userdata, flags, rc):
        self.logger.debug('MQTT onConnect called')
        # Result code 0 is success
        if rc == 0:
            self.mqttConnected = True

            # Subscribe to feed here
        else:
            self.logger.error('MQTT failed to connect: %s'%rc)
            raise RuntimeError('MQTT failed to connect: %s'%rc)

    def onDisconnect(self, client, userdata, rc):
        self.logger.debug('MQTT onDisconnect called')
        self.mqttConnected = False
        if rc != 0:
            self.logger.debug('MQTT disconnected unexpectedly: %s'%rc)
            self.handleReconnect(rc)

    def onMessage(self, client, userdata, msg):
        self.logger.debug('MQTT onMessage called for client: %s'%client)

    def connect(self):
        """ Connect to MQTT broker
        Skip calling connect if already connected.
        """
        if self.mqttConnected:
            return

        self._client.connect(self._host, port=self._port, keepalive=self._keepAlive)

    def disconnect(self):
        """ Check if connected"""
        if self.mqttConnected:
            self._client.disconnect()

    def subscribe(self, feed=False):
        """Subscribe to feed, defaults to feed specified in config"""
        if not feed: feed = _feedName
        self._client.subscribe('{0}/feeds/{1}'.format(self._username, feed))

    def publish(self, value, feed=False):
        """Publish a value to a feed"""
        if not feed: feed = _feedName
        self._client.publish('{0}/feeds/{1}'.format(self._username, feed), payload=value)

    def publishFaceValues(self, message):
        """ Publish face detection values to individual MQTT feeds
        Parses _extendedData.predictions.faceAttributes property
        Works with Azure face API responses and 
        """
        try:
            for face in message._extendedData['predictions']:
                faceAttrs = face['faceAttributes']
                for key in faceAttrs:
                    if type(faceAttrs[key]) is dict:
                        val = self.flattenDict(faceAttrs[key])
                        print('val: ', val)
                    else:
                        val = faceAttrs[key]
                    self.publish(val, key)
        except Exception as e:
            self.logger.error('Error publishing values: %s'%e)

    def flattenDict(self, aDict):
        """ Get average of simple dictionary of numerical values """
        try:
            val = float(sum(aDict[key] for key in aDict)) / len(aDict)
        except Exception as e:
            self.logger.error('Error flattening dict, returning 0: %s'%e)
        return val or 0

    def publishJsonMessage(self, message):
        msg_str = self.stringifyMessage(message)
        self.publish(msg_str)

    def stringifyMessage(self, message):
        """ Dump into JSON string """
        return json.dumps(message.__dict__).encode('utf8')

    def processQueue(self):
        self.logger.info('Processing queue')

        while self.alive:
            # Pump the loop
            self._client.loop(timeout=1)
            if (self.inQueue.empty() == False):
                try:
                    message = self.inQueue.get(block=False,timeout=1)
                    if message is not None and self.mqttConnected:
                        if message == "SHUTDOWN":
                            self.logger.debug("SHUTDOWN command handled")
                            self.shutdown()
                        else:
                            # Send message as string or split into channels
                            if self._publishJson:
                                self.publishJsonMessage(message)
                            elif self._publishFaceData:
                                self.publishFaceValues(message)
                            else:
                                self.publishValues(message)

                except Exception as e:
                    self.logger.error("MQTT unable to read queue : %s " %e)
            else:
                time.sleep(.25)

    def shutdown(self):
        self.logger.info("Shutting down MQTT %s" % (mp.current_process().name))
        self.alive = False
        time.sleep(1)
        self.exit = True

    def run(self):
        """ Thread start method"""
        self.logger.info("Running MQTT")

        self.connect()
        self.alive = True

        # Start queue loop
        self.processQueue()
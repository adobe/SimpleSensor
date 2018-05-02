'''
Module specific config
'''
import configparser
import os.path
import json
from src.threadsafeLogger import ThreadsafeLogger

def load(loggingQueue, name):
    """ Load module specific config into dictionary, return it"""    
    logger = ThreadsafeLogger(loggingQueue, '{0}-{1}'.format(name, 'ConfigLoader'))
    thisConfig = {}
    configParser = configparser.ConfigParser()

    thisConfig = loadSecrets(thisConfig, logger, configParser)
    thisConfig = loadModule(thisConfig, logger, configParser)
    return thisConfig

def loadSecrets(thisConfig, logger, configParser):
    """ Load module specific secrets """
    try:
        with open("./config/secrets.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/secrets.conf"))
        exit

    """ MQTT key """
    try:
        val=configParser.get('Secrets','mqtt_key')
    except:
        val = 'FakeKey'
    thisConfig['MqttKey'] = val
    logger.info("MQTT key : %s" % thisConfig['MqttKey'])

    return thisConfig

def loadModule(thisConfig, logger, configParser):

    try:
        val=configParser.get('ModuleConfig','mqtt_host')
    except:
        val = 'www.notahost.com/api'
    thisConfig['MqttHost'] = val
    logger.info("MQTT host : %s" % thisConfig['MqttHost'])

    try:
        val=configParser.getint('ModuleConfig','mqtt_port')
    except:
        val = 9999
    thisConfig['MqttPort'] = val
    logger.info("MQTT port : %s" % thisConfig['MqttPort'])

    try:
        val=configParser.get('ModuleConfig','mqtt_username')
    except:
        val = 'FakeUsername'
    thisConfig['MqttUsername'] = val
    logger.info("MQTT username : %s" % thisConfig['MqttUsername'])

    try:
        val=configParser.get('ModuleConfig','mqtt_feed_name')
    except:
        val = 'Test'
    thisConfig['MqttFeedName'] = val
    logger.info("MQTT feed name : %s" % thisConfig['MqttFeedName'])

    try:
        val=configParser.getint('ModuleConfig','mqtt_keep_alive')
    except:
        val = 60
    thisConfig['MqttKeepAlive'] = val
    logger.info("MQTT keep alive in seconds : %s" % thisConfig['MqttKeepAlive'])

    try:
        val=configParser.getboolean('ModuleConfig','mqtt_publish_json')
    except:
        val = False
    thisConfig['MqttPublishJson'] = val
    logger.info("MQTT publish messages as stringified JSON : %s" % thisConfig['MqttPublishJson'])

    try:
        val=configParser.getboolean('ModuleConfig','mqtt_publish_face_values')
    except:
        val = False
    thisConfig['MqttPublishFaceValues'] = val
    logger.info("MQTT publish face data results as values : %s" % thisConfig['MqttPublishFaceValues'])

    return thisConfig
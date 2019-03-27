'''
Module specific config
'''
import configparser
import os.path
import json
from simplesensor.shared.threadsafeLogger import ThreadsafeLogger

def load(loggingQueue, name):
    """ Load module specific config into dictionary, return it"""    
    logger = ThreadsafeLogger(loggingQueue, '{0}-{1}'.format(name, 'ConfigLoader'))
    thisConfig = {}
    configParser = configparser.ConfigParser()

    thisConfig = load_secrets(thisConfig, logger, configParser)
    thisConfig = load_module(thisConfig, logger, configParser)
    return thisConfig

def load_secrets(thisConfig, logger, configParser):
    """ Load module specific secrets """
    try:
        with open("./config/secrets.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/secrets.conf"))
        exit

    """MQTT Key"""
    try:
        configValue=configParser.get('Secrets','mqtt_key')
    except:
        configValue = 'na'
    logger.info("MQTT key : %s" % configValue)
    thisConfig['MqttKey'] = configValue

    return thisConfig

def load_module(thisConfig, logger, configParser):
    """ Load module config """
    try:
        with open("./config/module.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/module.conf"))
        exit

    """mqtt host"""
    try:
        configValue=configParser.get('ModuleConfig','mqtt_host')
    except:
        configValue = 'io.adafruit.com'
    logger.info("MQTT host : %s" % configValue)
    thisConfig['MqttHost'] = configValue

    """mqtt port"""
    try:
        configValue=configParser.getint('ModuleConfig','mqtt_port')
    except:
        configValue = 1883
    logger.info("MQTT port : %s" % configValue)
    thisConfig['MqttPort'] = configValue

    """mqtt username"""
    try:
        configValue=configParser.get('ModuleConfig','mqtt_username')
    except:
        configValue = 'invalid_default_user'
    logger.info("MQTT username : %s" % configValue)
    thisConfig['MqttUsername'] = configValue

    """mqtt feed name"""
    try:
        configValue=configParser.get('ModuleConfig','mqtt_feed_name')
    except:
        configValue = 'invalid_default_feed'
    logger.info("MQTT feed name : %s" % configValue)
    thisConfig['MqttFeedName'] = configValue

    """mqtt keep alive"""
    try:
        configValue=configParser.getint('ModuleConfig','mqtt_keep_alive')
    except:
        configValue = 60
    logger.info("MQTT keep alive : %s" % configValue)
    thisConfig['MqttKeepAlive'] = configValue

    """mqtt publish json"""
    try:
        configValue=configParser.getboolean('ModuleConfig','mqtt_publish_json')
    except:
        configValue = False
    logger.info("MQTT publish JSON : %s" % configValue)
    thisConfig['MqttPublishJson'] = configValue

    """min simple sensor version"""
    try:
        configValue=configParser.get('ModuleConfig','min_ss_version')
    except:
        logger.eror("Min SimpleSensor verion was not defined")
        configValue = "99999.9999.9"
    logger.info("Min SimpleSensor verion : %s" % configValue)
    thisConfig['MinSimpleSensorVersion'] = configValue

    """module tested versions"""
    try:
        configValue=list(filter(None, [x.strip() for x in configParser.get('ModuleConfig','ss_tested_versions').splitlines()]))
    except:
        configValue = ""
    logger.info("Module tested SimpleSensor verions : %s" % configValue)
    thisConfig['SimpleSensorTestedVersions'] = configValue

    return thisConfig
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

    return thisConfig

def load_module(thisConfig, logger, configParser):
    """ Load module config """
    try:
        with open("./config/module.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/module.conf"))
        exit

    """websocket host"""
    try:
        configValue=configParser.get('ModuleConfig','websocket_host')
    except:
        configValue = '127.0.0.1'
    logger.info("Websocket server host : %s" % configValue)
    thisConfig['WebsocketHost'] = configValue

    """websocket port"""
    try:
        configValue=configParser.getint('ModuleConfig','websocket_port')
    except:
        configValue = 13254
    logger.info("Websocket server port : %s" % configValue)
    thisConfig['WebsocketPort'] = configValue

    """min simple sensor version"""
    try:
        configValue=configParser.get('ModuleConfig','min_ss_version')
    except:
        logger.error("Min SimpleSensor verion was not defined")
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
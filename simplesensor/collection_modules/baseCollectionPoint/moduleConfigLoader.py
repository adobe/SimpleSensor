'''
Module specific config
'''
from simplesensor.threadsafeLogger import ThreadsafeLogger
import configparser
import os.path

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

    # Put secret parsing here

    return thisConfig

def loadModule(thisConfig, logger, configParser):
    """ Load module config """
    try:
        with open("./config/module.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/module.conf"))
        exit

    """collection point type"""
    try:
        configValue=configParser.get('ModuleConfig','collection_point_type')
    except:
        configValue = 'face-detect'
    logger.info("Collection point type : %s" % configValue)
    thisConfig['CollectionPointType'] = configValue

    """collection point id"""
    try:
        configValue=configParser.get('ModuleConfig','collection_point_id')
    except:
        configValue = 'face-detect1'
    logger.info("Collection point ID : %s" % configValue)
    thisConfig['CollectionPointId'] = configValue

    """show video stream"""
    try:
        configValue=configParser.getboolean('ModuleConfig','show_video_stream')
    except:
        configValue = False
    logger.info("Show video stream : %s" % configValue)
    thisConfig['ShowVideoStream'] = configValue

    return thisConfig

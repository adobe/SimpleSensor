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
        configParser.read(os.path.join(os.path.dirname(__file__),"config/secrets.conf"))
        exit

    """ Azure connection string """
    try:
        AZURE_CONNECTION_STRING=configParser.get('Secrets','azure_connection_string')
    except:
        AZURE_CONNECTION_STRING = None
    thisConfig['AzureConnectionString'] = AZURE_CONNECTION_STRING
    if thisConfig['UseAzure']:
        logger.info("Azure Connection String : %s" % thisConfig['AzureConnectionString'])

    return thisConfig

def loadModule(thisConfig, logger, configParser):
    """ Load module config """
    try:
        with open("./config/module.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"config/module.conf"))
        exit

    try:
        USE_AZURE=configParser.getboolean('BaseConfig','use_azure')
    except:
        USE_AZURE = False
    thisConfig['UseAzure'] = USE_AZURE
    logger.info("Use Azure : %s" % thisConfig['UseAzure'])

    try:
        AZURE_MESSAGE_TIMEOUT=configParser.getint('BaseConfig','azure_message_timeout')
    except:
        AZURE_MESSAGE_TIMEOUT = 10000
    thisConfig['AzureMessageTimeout'] = AZURE_MESSAGE_TIMEOUT
    if thisConfig['UseAzure']:
        logger.info("Azure Message Timeout : %s" % thisConfig['AzureMessageTimeout'])

    try:
        AZURE_TIMEOUT=configParser.getint('BaseConfig','azure_timeout')
    except:
        AZURE_TIMEOUT = 241000
    thisConfig['AzureTimeout'] = AZURE_TIMEOUT
    if thisConfig['UseAzure']:
        logger.info("Azure Timeout : %s" % thisConfig['AzureTimeout'])

    try:
        AZURE_MINIMUM_POLLING_TIME=configParser.getint('BaseConfig','azure_minimum_polling_time')
    except:
        AZURE_MINIMUM_POLLING_TIME = 241000
    thisConfig['AzureMinimumPollingTime'] = AZURE_MINIMUM_POLLING_TIME
    if thisConfig['UseAzure']:
        logger.info("Azure Minimum Polling Time : %s" % thisConfig['AzureMinimumPollingTime'])

    try:
        val=configParser.getboolean('BaseConfig','azure_device_created')
    except:
        val = False
    thisConfig['AzureDeviceCreated'] = val
    logger.info("Azure device has been created : %s" % thisConfig['AzureDeviceCreated'])

    return thisConfig

def setAzureClientAsCreated():
    configParser.set('ModuleConfig', 'azure_device_created', True)

    with open('config/collectionPoint.conf', 'wb') as configfile:
        configParser.write(configfile)
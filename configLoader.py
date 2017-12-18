'''
Author: dAvid B3nge
the main file was getting all yucked up with this config reading and normalizing so I broke it into an secondary file to make it more manageable
'''
import configparser
import os.path
import json

baseConfig = {}
configParser = configparser.ConfigParser()
configFilePath = None

def load(logger):
    """ Build dictionary of config values, return it """
    loadBase(logger)
    loadSecrets(logger)
    return baseConfig

def loadSecrets(logger):
    """ Load secrets.conf into baseConfig"""
    try:
        with open("/secrets.conf") as f:
            configParser.readfp(f)
            configFilePath = "/secrets.conf"
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"config/secrets.conf"))
        configFilePath = os.path.join(os.path.dirname(__file__),"config/secrets.conf")
        exit

    """ Azure connection string """
    try:
        AZURE_CONNECTION_STRING=configParser.get('Secrets','azure_connection_string')
    except:
        AZURE_CONNECTION_STRING = None
    baseConfig['AzureConnectionString'] = AZURE_CONNECTION_STRING
    if baseConfig['UseAzure']:
        logger.info("Azure Connection String : %s" % baseConfig['AzureConnectionString'])

    """ MQTT key """
    try:
        val=configParser.get('Secrets','mqtt_key')
    except:
        val = 'FakeKey'
    baseConfig['MqttKey'] = val
    logger.info("MQTT key : %s" % baseConfig['MqttKey'])

def loadBase(logger):
    """ Load base.conf into baseConfig"""
    try:
        with open("/base.conf") as f:
            configParser.readfp(f)
            configFilePath = "/base.conf"
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"config/base.conf"))
        configFilePath = os.path.join(os.path.dirname(__file__),"config/base.conf")
        exit

    """collection point id"""
    try:
        COLLECTION_POINT_ID=configParser.get('BaseConfig','collection_point_id')
    except:
        COLLECTION_POINT_ID = 'noId'
    logger.info("Collection point id is set to : %s" % COLLECTION_POINT_ID)
    baseConfig['CollectionPointId'] = COLLECTION_POINT_ID

    """collection point type"""
    try:
        COLLECTION_POINT_TYPE=configParser.get('BaseConfig','collection_point_type')
    except:
        COLLECTION_POINT_TYPE = 'noId'
    logger.info("Collection point type is set to : %s" % COLLECTION_POINT_TYPE)
    baseConfig['CollectionPointType'] = COLLECTION_POINT_TYPE

    """slact channel webhook url"""
    try:
        SLACK_CHANNEL_WEBHOOK_URL=configParser.get('BaseConfig','slack_channel_webhook_url')
        if len(SLACK_CHANNEL_WEBHOOK_URL) < 1:
            None
    except:
        SLACK_CHANNEL_WEBHOOK_URL = None
    logger.info("Slack channel webhook is set to : %s" % SLACK_CHANNEL_WEBHOOK_URL)
    baseConfig['SlackChannelWebhookUrl'] = SLACK_CHANNEL_WEBHOOK_URL

    """Test mode"""
    try:
        TEST_MODE=configParser.getboolean('BaseConfig','test_mode')
    except:
        TEST_MODE = False
    logger.info("Test mode is set to : %s" % TEST_MODE)
    baseConfig['TestMode'] = TEST_MODE


    ################ WEB SOCKET ################
    try:
        EXPOSE_WEBSOCKET=configParser.getboolean('BaseConfig','expose_websocket')
    except:
        EXPOSE_WEBSOCKET = False
    logger.info("Use Websocket: %s" % EXPOSE_WEBSOCKET)
    baseConfig['ExposeWebsocket'] = EXPOSE_WEBSOCKET
    """websocket port"""
    try:
        WEBSOCKET_PORT=configParser.getint('BaseConfig','websocket_port')
    except:
        WEBSOCKET_PORT = 0
    baseConfig['WebsocketPort'] = WEBSOCKET_PORT
    if baseConfig['ExposeWebsocket']:
        logger.info("Websocket port: %s" % baseConfig['WebsocketPort'])

    """websocket host"""
    try:
        WEBSOCKET_HOST=configParser.get('BaseConfig','websocket_host')
    except:
        WEBSOCKET_HOST = 0
    baseConfig['WebsocketHost'] = WEBSOCKET_HOST
    if baseConfig['ExposeWebsocket']:
        logger.info("Websocket host: %s" % baseConfig['WebsocketHost'])


    ################ AZURE ################
    try:
        USE_AZURE=configParser.getboolean('BaseConfig','use_azure')
    except:
        USE_AZURE = False
    baseConfig['UseAzure'] = USE_AZURE
    logger.info("Use Azure : %s" % baseConfig['UseAzure'])

    try:
        AZURE_MESSAGE_TIMEOUT=configParser.getint('BaseConfig','azure_message_timeout')
    except:
        AZURE_MESSAGE_TIMEOUT = 10000
    baseConfig['AzureMessageTimeout'] = AZURE_MESSAGE_TIMEOUT
    if baseConfig['UseAzure']:
        logger.info("Azure Message Timeout : %s" % baseConfig['AzureMessageTimeout'])

    try:
        AZURE_TIMEOUT=configParser.getint('BaseConfig','azure_timeout')
    except:
        AZURE_TIMEOUT = 241000
    baseConfig['AzureTimeout'] = AZURE_TIMEOUT
    if baseConfig['UseAzure']:
        logger.info("Azure Timeout : %s" % baseConfig['AzureTimeout'])

    try:
        AZURE_MINIMUM_POLLING_TIME=configParser.getint('BaseConfig','azure_minimum_polling_time')
    except:
        AZURE_MINIMUM_POLLING_TIME = 241000
    baseConfig['AzureMinimumPollingTime'] = AZURE_MINIMUM_POLLING_TIME
    if baseConfig['UseAzure']:
        logger.info("Azure Minimum Polling Time : %s" % baseConfig['AzureMinimumPollingTime'])

    try:
        val=configParser.getboolean('BaseConfig','azure_device_created')
    except:
        val = False
    baseConfig['AzureDeviceCreated'] = val
    logger.info("Azure device has been created : %s" % baseConfig['AzureDeviceCreated'])


    ################ MQTT ################
    try:
        val=configParser.getboolean('BaseConfig','use_mqtt')
    except:
        val = False
    baseConfig['UseMqtt'] = val
    logger.info("Use MQTT : %s" % baseConfig['UseMqtt'])

    try:
        val=configParser.get('BaseConfig','mqtt_host')
    except:
        val = 'www.notahost.com/api'
    baseConfig['MqttHost'] = val
    logger.info("MQTT host : %s" % baseConfig['MqttHost'])

    try:
        val=configParser.getint('BaseConfig','mqtt_port')
    except:
        val = 9999
    baseConfig['MqttPort'] = val
    logger.info("MQTT port : %s" % baseConfig['MqttPort'])

    try:
        val=configParser.get('BaseConfig','mqtt_username')
    except:
        val = 'FakeUsername'
    baseConfig['MqttUsername'] = val
    logger.info("MQTT username : %s" % baseConfig['MqttUsername'])

    try:
        val=configParser.get('BaseConfig','mqtt_feed_name')
    except:
        val = 'Test'
    baseConfig['MqttFeedName'] = val
    logger.info("MQTT feed name : %s" % baseConfig['MqttFeedName'])

    try:
        val=configParser.getint('BaseConfig','mqtt_keep_alive')
    except:
        val = 60
    baseConfig['MqttKeepAlive'] = val
    logger.info("MQTT keep alive in seconds : %s" % baseConfig['MqttKeepAlive'])

    try:
        val=configParser.getboolean('BaseConfig','mqtt_publish_json')
    except:
        val = False
    baseConfig['MqttPublishJson'] = val
    logger.info("MQTT publish messages as stringified JSON : %s" % baseConfig['MqttPublishJson'])

    try:
        val=configParser.getboolean('BaseConfig','mqtt_publish_face_values')
    except:
        val = False
    baseConfig['MqttPublishFaceValues'] = val
    logger.info("MQTT publish face data results as values : %s" % baseConfig['MqttPublishFaceValues'])


    ################ MODULES ################

    try:
        strVal = configParser.get('BaseConfig', 'collection_modules')
        val = json.loads(strVal)
    except:
        strVal = 'camCollectionPoint'
        val = [strVal]
    baseConfig['CollectionModules'] = val
    logger.info("Collection point modules to use : %s" % strVal)

    try:
        strVal = configParser.get('BaseConfig', 'communication_modules')
        val = json.loads(strVal)
    except:
        strVal = 'websocketServer'
        val = [strVal]
    baseConfig['CommunicationModules'] = val
    logger.info("Communication method modules to use : %s" % strVal)

    logger.info("App config for base %s done" % configParser.get('BaseConfig','collection_point_id'))

    return baseConfig

def setAzureClientAsCreated():
    configParser.set('BaseConfig', 'azure_device_created', True)

    with open(configFilePath, 'wb') as configfile:
        configParser.write(configfile)

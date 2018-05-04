"""
Module specific config loader
"""
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
    """ Load module specific secrets which at this time we really dont have any"""
    try:
        with open("./config/secrets.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/secrets.conf"))
        exit

    #we dont have any secrets to 

    return thisConfig

def loadModule(thisConfig, logger, configParser):
    logger.info("Loading config")
    """ Load module config """
    try:
        with open("./config/module.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"./config/module.conf"))
        

    exit

    try:
        configValue=configParser.get('ModuleConfig','collection_point_id')
    except:
        configValue = "btle1"
    logger.info("Collection point ID : %s" % configValue)
    thisConfig['CollectionPointId'] = configValue

    """gateway type"""
    try:
        configValue=configParser.get('ModuleConfig','gateway_type')
    except:
        configValue = "proximity"
    logger.info("btle gateway type : %s" % configValue)
    thisConfig['GatewayType'] = configValue

    try:
        configValue=configParser.get('ModuleConfig','interface_type')
    except:
        configValue = "btle"
    logger.info("interface : %s" % configValue)
    thisConfig['InterfaceType'] = configValue

    """Proximity Event Interval In Milliseconds"""
    try:
        configValue=configParser.getint('ModuleConfig','proximity_event_interval')
    except:
        configValue = 5000
    logger.info("Proximity Event Interval In Milliseconds : %s" % configValue)
    thisConfig['ProximityEventInterval'] = configValue

    """Leave time in milliseconds"""
    try:
        configValue=configParser.getint('ModuleConfig','leave_time')
    except:
        configValue = 1500
    logger.info("Leave time in milliseconds : %s" % configValue)
    thisConfig['LeaveTime'] = configValue

    """Abandoned client cleanup interval in milliseconds"""
    try:
        configValue=configParser.getint('ModuleConfig','abandoned_client_cleanup_interval')
    except:
        configValue = 300000
    logger.info("Abandoned client cleanup interval in milliseconds : %s" % configValue)
    thisConfig['AbandonedClientCleanupInterval'] = configValue

    """Abandoned client timeout in milliseconds"""
    try:
        configValue=configParser.getint('ModuleConfig','abandoned_client_timeout')
    except:
        configValue = 120000
    logger.info("Abandoned client timeout in milliseconds : %s" % configValue)
    thisConfig['AbandonedClientTimeout'] = configValue

    """Btle rssi client in threshold"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_rssi_client_in_threshold')
    except:
        configValue = -68
    logger.info("Btle rssi client in threshold : %s" % configValue)
    thisConfig['BtleRssiClientInThreshold'] = configValue

    """Btle rssi client in threshold type (rssi or distance)"""
    try:
        configValue=configParser.get('ModuleConfig','btle_rssi_client_in_threshold_type')
    except:
        configValue = "rssi"
    logger.info("Btle rssi client in threshold type : %s" % configValue)
    thisConfig['BtleRssiClientInThresholdType'] = configValue

    """Btle device id (com5 or /dev/ttyACM0)"""
    try:
        configValue=configParser.get('ModuleConfig','btle_device_id')
    except:
        configValue = "com3"
    logger.info("Btle device id : %s" % configValue)
    thisConfig['BtleDeviceId'] = configValue

    """Btle device baud rate is 38400 range is 1200 - 2000000"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_device_baud_rate')
    except:
        configValue = 38400
    logger.info("Btle device baud rate : %s" % configValue)
    thisConfig['BtleDeviceBaudRate'] = configValue

    """Btle advertising major"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_advertising_major')
    except:
        configValue = 100
    logger.info("Btle advertising major : %s" % configValue)
    thisConfig['BtleAdvertisingMajor'] = configValue

    """Btle advertising minor"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_advertising_minor')
    except:
        configValue = 10
    logger.info("Btle advertising minor : %s" % configValue)
    thisConfig['BtleAdvertisingMinor'] = configValue

    """Btle anomaly reset limit"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_anomaly_reset_limit')
    except:
        configValue = 2
    logger.info("Btle anomaly reset limit : %s" % configValue)
    thisConfig['BtleAnomalyResetLimit'] = configValue

    """Btle rssi needed sample size"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_rssi_needed_sample_size')
    except:
        configValue = 1
    logger.info("Btle rssi needed sample size : %s" % configValue)
    thisConfig['BtleRssiNeededSampleSize'] = configValue

    """Btle rssi max sample size"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_rssi_max_sample_size')
    except:
        configValue = 1
    logger.info("Btle rssi max sample size : %s" % configValue)
    thisConfig['BtleRssiMaxSampleSize'] = configValue

    """Btle rssi error variance"""
    try:
        configValue=configParser.getfloat('ModuleConfig','btle_rssi_error_variance')
    except:
        configValue = .12
    logger.info("Btle rssi error variance : %s" % configValue)
    thisConfig['BtleRssiErrorVariance'] = configValue

    """Btle device tx power"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_device_tx_power')
    except:
        configValue = 15
    logger.info("Btle device tx power : %s" % configValue)
    thisConfig['BtleDeviceTxPower'] = configValue

    """Btle client out count threshold"""
    try:
        configValue=configParser.getint('ModuleConfig','btle_client_out_count_threshold')
    except:
        configValue = 5
    logger.info("Btle client out count threshold : %s" % configValue)
    thisConfig['BtleClientOutCountThreshold'] = configValue

    """Slack channel webhook url"""
    try:
        configValue=configParser.get('ModuleConfig','slack_channel_webhook_url')
    except:
        configValue = ""
    logger.info("Slack channel webhook url : %s" % configValue)
    thisConfig['SlackChannelWebhookUrl'] = configValue

    return thisConfig

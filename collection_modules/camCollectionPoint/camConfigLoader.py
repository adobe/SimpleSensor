'''
Author: dAvid B3nge
the main file was getting all yucked up with this config reading and normalizing so I broke it into an secondary file to make it more manageable for each module
'''
import configparser
import os.path
import json
from threadsafeLogger import ThreadsafeLogger

def load(loggingQueue):
    """ Load module specific config into dictionary, return it"""    
    logger = ThreadsafeLogger(loggingQueue, "CamCollectionPoint")
    thisConfig = {}
    configParser = configparser.ConfigParser()

    thisConfig = loadSecrets(thisConfig, logger, configParser)
    thisConfig = loadModule(thisConfig, logger, configParser)
    return thisConfig

def loadSecrets(thisConfig, logger, configParser):
    """ Load module specific secrets """
    try:
        with open("/secrets.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"config/secrets.conf"))
        exit

    thisConfig['Azure'] = {}

    """azure subscription key"""
    try:
        configValue=configParser.get('Secrets','azure_subscription_key')
    except:
        configValue = ""
    logger.info("Azure subscription key : %s" % configValue)
    thisConfig['Azure']['SubscriptionKey'] = configValue

    return thisConfig

def loadModule(thisConfig, logger, configParser):
    """ Load module config """
    try:
        with open("/collectionPoint.conf") as f:
            configParser.readfp(f)
    except IOError:
        configParser.read(os.path.join(os.path.dirname(__file__),"config/collectionPoint.conf"))
        exit

    """use ids camera"""
    try:
        configValue=configParser.getboolean('CollectionPointConfig','use_ids_camera')
    except:
        configValue = False
    logger.info("Use IDS camera : %s" % configValue)
    thisConfig['UseIdsCamera'] = configValue

    """primary target"""
    try:
        configValue=configParser.get('CollectionPointConfig','primary_target')
    except:
        configValue = "closest"
    logger.info("Primary target : %s" % configValue)
    thisConfig['PrimaryTarget'] = configValue

    """closest threshold"""
    try:
        configValue=configParser.getint('CollectionPointConfig','closest_threshold')
    except:
        configValue = 2
    logger.info("Closest threshold : %s" % configValue)
    thisConfig['ClosestThreshold'] = configValue

    """capture width"""
    try:
        configValue=configParser.getint('CollectionPointConfig','capture_width')
    except:
        configValue = 1600
    logger.info("Capture width : %s" % configValue)
    thisConfig['CaptureWidth'] = configValue

    """capture height"""
    try:
        configValue=configParser.getint('CollectionPointConfig','capture_height')
    except:
        configValue = 1200
    logger.info("Capture height : %s" % configValue)
    thisConfig['CaptureHeight'] = configValue

    """target face width"""
    try:
        configValue=configParser.getint('CollectionPointConfig','target_face_width')
    except:
        configValue = 150
    logger.info("Target face width : %s" % configValue)
    thisConfig['TargetFaceWidth'] = configValue

    """min face width"""
    try:
        configValue=configParser.getint('CollectionPointConfig','min_face_width')
    except:
        configValue = 120
    logger.info("Min face width : %s" % configValue)
    thisConfig['MinFaceWidth'] = configValue

    """min face height"""
    try:
        configValue=configParser.getint('CollectionPointConfig','min_face_height')
    except:
        configValue = 120
    logger.info("Min face height : %s" % configValue)
    thisConfig['MinFaceHeight'] = configValue

    """face pixel buffer"""
    try:
        configValue=configParser.getint('CollectionPointConfig','face_pixel_buffer')
    except:
        configValue = 40
    logger.info("Face pixel buffer : %s" % configValue)
    thisConfig['FacePixelBuffer'] = configValue

    """horizontal velocity buffer"""
    try:
        configValue=configParser.getint('CollectionPointConfig','horizontal_velocity_buffer')
    except:
        configValue = 80
    logger.info("Horizontal velocity buffer : %s" % configValue)
    thisConfig['HorizontalVelocityBuffer'] = configValue

    """vertical velocity buffer"""
    try:
        configValue=configParser.getint('CollectionPointConfig','vertical_velocity_buffer')
    except:
        configValue = 60
    logger.info("Vertical velocity buffer : %s" % configValue)
    thisConfig['VerticalVelocityBuffer'] = configValue

    """use velocity"""
    try:
        configValue=configParser.getboolean('CollectionPointConfig','use_velocity')
    except:
        configValue = False
    logger.info("Use velocity : %s" % configValue)
    thisConfig['UseVelocity'] = configValue

    """reset event timer"""
    try:
        configValue=configParser.getint('CollectionPointConfig','reset_event_timer')
    except:
        configValue = 10
    logger.info("Reset event timer : %s" % configValue)
    thisConfig['ResetEventTimer'] = configValue

    """collection threshold"""
    try:
        configValue=configParser.getint('CollectionPointConfig','collection_threshold')
    except:
        configValue = 2
    logger.info("Collection threshold : %s" % configValue)
    thisConfig['CollectionThreshold'] = configValue

    """maximum people"""
    try:
        configValue=configParser.getint('CollectionPointConfig','maximum_people')
    except:
        configValue = 6
    logger.info("Maximum people : %s" % configValue)
    thisConfig['MaximumPeople'] = configValue

    """show video stream"""
    try:
        configValue=configParser.getboolean('CollectionPointConfig','show_video_stream')
    except:
        configValue = True
    logger.info("Show video stream : %s" % configValue)
    thisConfig['ShowVideoStream'] = configValue

    """min nearest neighbors"""
    try:
        configValue=configParser.getint('CollectionPointConfig','min_nearest_neighbors')
    except:
        configValue = 7
    logger.info("Min nearest neighbors : %s" % configValue)
    thisConfig['MinNearestNeighbors'] = configValue

    """compression factor ids only"""
    try:
        configValue=configParser.getint('CollectionPointConfig','compression_factor')
    except:
        configValue = 9
    logger.info("IDS compression factor : %s" % configValue)
    thisConfig['CompressionFactor'] = configValue

    """pixel clock ids only"""
    try:
        configValue=configParser.getint('CollectionPointConfig','pixel_clock')
    except:
        configValue = 18
    logger.info("IDS pixel clock : %s" % configValue)
    thisConfig['PixelClock'] = configValue

    """bits per pixel"""
    try:
        configValue=configParser.getint('CollectionPointConfig','bits_per_pixel')
    except:
        configValue = 8
    logger.info("Bits per pixel : %s" % configValue)
    thisConfig['BitsPerPixel'] = configValue

    """send blob"""
    try:
        configValue=configParser.getboolean('CollectionPointConfig','send_blobs')
    except:
        configValue = False
    logger.info("Send blob : %s" % configValue)
    thisConfig['SendBlobs'] = configValue

    try:
        configValue=configParser.getint('CollectionPointConfig','blob_width')
    except:
        configValue = 320
    logger.info("Blob width : %s" % configValue)
    thisConfig['BlobWidth'] = configValue

    try:
        configValue=configParser.getint('CollectionPointConfig','blob_height')
    except:
        configValue = 240
    logger.info("Blob height : %s" % configValue)
    thisConfig['BlobHeight'] = configValue


    '''AZURE CONFIG '''

    """uri base"""
    try:
        configValue=configParser.get('Azure','uri_base')
    except:
        configValue = "westus.api.cognitive.microsoft.com"
    logger.info("Azure uri base : %s" % configValue)
    thisConfig['Azure']['UriBase'] = configValue


    return thisConfig

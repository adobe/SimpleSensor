import multiprocessing
import time
import threading
import json
import sys
# import iothub_service_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
from iothub_service_client import IoTHubRegistryManager, IoTHubRegistryManagerAuthMethod, IoTHubDeviceMethod
from iothub_service_client import IoTHubDeviceStatus, IoTHubError, IoTHubMessage, IoTHubMessaging
from iothub_service_client_args import get_iothub_opt, OptionError
from threadsafeLogger import ThreadsafeLogger
from datetime import datetime

class AzureIotHubModule(multiprocessing.Process):


    def run(self):
        self.logger.info("Running Azure %s" % (multiprocessing.current_process().name))
        self.alive = True

        '''
        #Messaging - used for sending cloud to device messages
        try:
            self.logger.info('opening iothubmessaging')
            self.iothubMessaging = IoTHubMessaging(self.CONNECTION_STRING)
            # self.iothubMessaging.set_feedback_message_callback(self.feedback_received_callback, self.FEEDBACK_CONTEXT)
            self.iothubMessaging.open(self.open_complete_callback, self.OPEN_CONTEXT)
            self.logger.info('iothubmessaging is open')
        except Exception as e:
            print ("Unexpected error while starting connection to Azure Iot %s" % e )
        '''

        
        #Client - used for sending device to cloud messages
        # try: 
        #     self.client = IoTHubClient(self.DEVICE_CONNECTION_STRING, self.PROTOCOL)
        #     self.client.set_option("messageTimeout", self.MESSAGE_TIMEOUT)
        #     self.client.set_option("logtrace", 0)
        #     self.client.set_option("product_info", "CEC TEST")
        # except Exception as e:
        #     print ("Unexpected error while starting client: %s"%e)
        

        # Send initial message to open connection
        # try:
        #     self.logger.info('sending start message')
        #     message = IoTHubMessage("Open sesame")
        #     self.iothubMessaging.send_async(self.config['CollectionPointId'], message, self.send_complete_callback, 0)
        #     self.logger.info('sent start message')
        # except IoTHubError as iothub_error:
        #     self.logger.error ("IoTHub error while sending start message: %s" % iothub_error )

        self.iothub_device_method = IoTHubDeviceMethod(self.CONNECTION_STRING)

        #setup the queue loop thread 
        try:
            self.threadProcessQueue = threading.Thread(target=self.processQueue)
            # self.threadProcessQueue.setDaemon(True)   #this was acting super freaky and not running the loop
            self.threadProcessQueue.start()
            self.logger.info("Started Azure message queue thread")
        except IoTHubClientError as e: 
            self.logger.error("Unexpected error %s starting thread" % e)
        

    def shutdown(self):
        self.logger.info("Shuting down Azure client %s" % (multiprocessing.current_process().name))
        self.alive = False
        self.iothubMessaging.close()
        self.threadProcessQueue.join()
        time.sleep(1)
        self.exit = True

    def processQueue(self):
        print('in azure iot process q, messagequeue empty:', self.messageQueue.empty())
        self.logger.info('in azure iot process q')
        self.logger.info("Running Azure %s" % (multiprocessing.current_process().name))

        self.client = IoTHubClient(self.DEVICE_CONNECTION_STRING, self.PROTOCOL)
        self.client.set_option("messageTimeout", self.MESSAGE_TIMEOUT)
        self.client.set_option("logtrace", 0)
        self.client.set_option("product_info", "CEC TEST")
        # try:
        #     self.iothubMessaging = IoTHubMessaging(self.CONNECTION_STRING)
        #     # self.iothubMessaging.set_feedback_message_callback(self.feedback_received_callback, self.FEEDBACK_CONTEXT)
        #     self.iothubMessaging.open(self.open_complete_callback, self.OPEN_CONTEXT)
        # except Exception as e:
        #     print ("Unexpected error while starting connection to Azure Iot %s" % e )
        _messageCounter = 0
        while self.alive:
            self.logger.info('in self alive')
            if (self.messageQueue.empty() == False):
                try:
                    print('getting message')
                    message = self.messageQueue.get(block=False,timeout=1)
                    if message is not None:
                        if message == "SHUTDOWN":
                            self.logger.info("SHUTDOWN command handled on %s" % (multiprocessing.current_process().name))
                            self.shutdown()
                            self.logger.info("Done processing SHUTDOWN command")
                        else:
                            #self.logger.debug("Sending (%s)" % json.dumps(message.__dict__))
                            try:
                                print("processing message")
                                print('iothub message before instance: %r'%json.dumps(message.__dict__).encode('utf8'))
                                raw_msg=json.dumps(message.__dict__).encode('utf8')
                                message = IoTHubMessage(bytearray(json.dumps(message.__dict__),'utf8'))
                                print('iothub message: %s'%message)

                                # optional: assign ids
                                dt = datetime.now()
                                message.message_id = "%d" % dt.microsecond  #send the time in milliseconds as the id
                                #message.correlation_id = "correlation_%d" % i
                                # optional: assign properties
                                #prop_map = message.properties()
                                #prop_text = "PropMsg_%d" % i
                                #prop_map.add("Property", prop_text)

                                self.messageCounter+=1
                                _messageCounter += 1
                                '''
                                # Client
                                self.client.send_event_async(message, send_confirmation_callback, message_counter)
                                print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % message_counter )

                                status = self.client.get_send_status()
                                print ( "Send status: %s" % status )
                                time.sleep(30)

                                status = self.client.get_send_status()
                                print ( "Send status: %s" % status )
                                '''
                                def _send_confirmation_callback(message, result, user_context):
                                    self.logger.debug ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
                                    map_properties = message.properties()
                                    self.logger.debug ( "    message_id: %s" % message.message_id )
                                    self.logger.debug ( "    correlation_id: %s" % message.correlation_id )
                                    key_value_pair = map_properties.get_internals()
                                    self.logger.debug ( "    Properties: %s" % key_value_pair )
                                    self.sendCallbacks += 1
                                    self.logger.debug( "    Total calls confirmed: %d" % self.sendCallbacks )

                                # self.iothubMessaging.send_async(self.config['CollectionPointId'],message, self.__send_confirmation_callback,self.messageCounter)
                                print("sending message")
                                # response = self.iothub_device_method.invoke('reader1', 'device_method_name', raw_msg, 60)
                                self.client.send_event_async(message, self.send_confirmation_callback, self.messageCounter)
                                # self.iothubMessaging.send_async(self.config['CollectionPointId'], message, self.send_complete_callback, self.messageCounter)
                                print('caught exception: ', e)
                                print('after send message')

                            except IoTHubError as iothub_error:
                                print ("Unexpected IoTHubError error %s from IoTHub" % iothub_error )
                            except Exception as e:
                                print ("Unexpected error %s from IoTHub" % e )
                except Exception as e:
                    self.logger.error("azure unable to read queue : %s " %e)
            else:
                self.logger.debug("azure queue EMPTY and size: %s " %self.messageQueue.qsize())
                time.sleep(.25)
        print('after while loop')

    def __init__(self,baseConfig,pInBoundEventQueue,pOutBoundEventQueue,loggingQueue):
        super(AzureIotHubModule, self).__init__()
        self.config = baseConfig
        # self.inBoundEventQueue=pInBoundEventQueue
        self.messageQueue = pInBoundEventQueue
        self.outBoundEventQueue=pOutBoundEventQueue

        # logging setup
        self.logger = ThreadsafeLogger(loggingQueue,"AzureIotHub")

        self.logger.info('in azure iothub init')

        self.FEEDBACK_CONTEXT = 1
        self.OPEN_CONTEXT = 0

        # chose HTTP, AMQP or MQTT as transport protocol
        self.PROTOCOL = IoTHubTransportProvider.MQTT

        # String containing Hostname, Device Id & Device Key in the format:
        # "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
        self.CONNECTION_STRING = baseConfig['AzureConnectionString']
        self.DEVICE_CONNECTION_STRING = "xx"
        self.HOSTNAME = "ceciothub.azure-devices.net"
        # self.msg_txt = "{\"deviceId\": \"myPythonDevice\",\"windSpeed\": %.2f}"

        # HTTP options
        # Because it can poll "after 9 seconds" polls will happen effectively
        # at ~10 seconds.
        # Note that for scalabilty, the default value of minimumPollingTime
        # is 25 minutes. For more information, see:
        # https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
        self.timeout = baseConfig['AzureTimeout']
        self.minimum_polling_time = baseConfig['AzureMinimumPollingTime']

        # messageTimeout - the maximum time in milliseconds until a message times out.
        # The timeout period starts at IoTHubClient.send_event_async.
        # By default, messages do not expire.
        self.MESSAGE_TIMEOUT = baseConfig['AzureMessageTimeout']

        self.messageCounter = 0
        #self.iotHubClient = None
        # self.iothubMessaging = None

        #counters
        self.sendCallbacks = 0

        # createdevice
        # if not baseConfig['AzureDeviceCreated']:
        # self.iothub_device = self.__iothub_createdevice() #create the device Id in azure
        # self.DEVICE_CONNECTION_STRING = self.buildDeviceConString(self.iothub_device, self.HOSTNAME)
        self.DEVICE_CONNECTION_STRING = "xx"

    def __iothub_createdevice(self):
        try:
            iothub_registry_manager = IoTHubRegistryManager(self.config['AzureConnectionString'])
            auth_method = IoTHubRegistryManagerAuthMethod.SHARED_PRIVATE_KEY
            new_device = iothub_registry_manager.create_device(self.config['CollectionPointId'], "", "", auth_method)
            self.__print_device_info("New Azure IOT Device Info", new_device)
            return new_device

        except Exception as e:
            if "IoTHubRegistryManagerResult.DEVICE_EXIST" in str(e):
                #device id alread exists
                self.logger.warn("Azure deviceId %s already exists"%self.config['CollectionPointId'])
                iothub_device = iothub_registry_manager.get_device(self.config['CollectionPointId'])
                self.__print_device_info("Existing Azure IOT Device Info", iothub_device)
                return iothub_device
            else:
                self.logger.error("Error checking IoTHubRegistryManager %s" % e)
        except KeyboardInterrupt:
            print ( "iothub_createdevice stopped" )

    def __print_device_info(self,title,iothub_device):
        self.logger.info( title + ":" )
        self.logger.info( "iothubDevice.deviceId                    = {0}".format(iothub_device.deviceId) )
        self.logger.info( "iothubDevice.primaryKey                  = {0}".format(iothub_device.primaryKey) )
        self.logger.info( "iothubDevice.secondaryKey                = {0}".format(iothub_device.secondaryKey) )
        self.logger.info( "iothubDevice.connectionState             = {0}".format(iothub_device.connectionState) )
        self.logger.info( "iothubDevice.status                      = {0}".format(iothub_device.status) )
        self.logger.info( "iothubDevice.lastActivityTime            = {0}".format(iothub_device.lastActivityTime) )
        self.logger.info( "iothubDevice.cloudToDeviceMessageCount   = {0}".format(iothub_device.cloudToDeviceMessageCount) )
        self.logger.info( "iothubDevice.isManaged                   = {0}".format(iothub_device.isManaged) )
        self.logger.info( "iothubDevice.authMethod                  = {0}".format(iothub_device.authMethod) )
        self.logger.info( "" )

    def send_confirmation_callback(self, message, result, user_context):
        self.logger.debug ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
        map_properties = message.properties()
        self.logger.debug ( "    message_id: %s" % message.message_id )
        self.logger.debug ( "    correlation_id: %s" % message.correlation_id )
        key_value_pair = map_properties.get_internals()
        self.logger.debug ( "    Properties: %s" % key_value_pair )
        self.sendCallbacks += 1
        self.logger.debug( "    Total calls confirmed: %d" % self.sendCallbacks )

    def logClientEventSend(self,message,sentMessage):
        self.logger.debug("")
        self.logger.debug("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        self.logger.debug("ZZZZZ %s ZZZZZ" %message)
        self.logger.debug("")
        self.logger.debug("%s" %sentMessage)
        self.logger.debug("")
        self.logger.debug("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        self.logger.debug("")

    
    def __iothub_client_init(self):
        # prepare iothub client
        # self.iotHubClient = IoTHubMessaging(self.CONNECTION_STRING)
        # self.iotHubClient.set_feedback_message_callback(self.feedback_received_callback, self.FEEDBACK_CONTEXT)

        #self.iotHubClient.open(self.open_complete_callback, self.OPEN_CONTEXT)

        self.client = IoTHubClient(self.CONNECTION_STRING, self.PROTOCOL)
        self.client.set_option("messageTimeout", self.MESSAGE_TIMEOUT)
        self.client.set_option("logtrace", 0)
        self.client.set_option("product_info", "CEC TEST")
    
    def send_complete_callback(self, context, messaging_result):
        # context = 0
        print ( 'Azure IoTHub callback context: {0}'.format(context) )
        print ( 'Azure message result: {0}'.format(messaging_result) )
    
    def feedback_received_callback(self,context, batch_user_id, batch_lock_token, feedback_records):
        print ( 'received_callback called with context: {0}'.format(context) )

    def buildDeviceConString(self, iothub_device, hostname):
        #HostName=<hostName>;DeviceId=<deviceId>;SharedAccessKey=<primaryKey>
        return "HostName={0};DeviceId={1};SharedAccessKey={2}".format(hostname, iothub_device.deviceId, iothub_device.primaryKey)
    def open_complete_callback(self,context):
        #now that the connection is open to Azure lets start listening to the queue
        print( 'open_complete_callback called with context: {0}'.format(context) )
        # self.alive = True

        #setup the queue loop thread 
        # try:
        #     self.threadProcessQueue = threading.Thread(target=self.processQueue)
        #     # self.threadProcessQueue.setDaemon(True)   #this was acting super freaky and not running the loop
        #     self.threadProcessQueue.start()
        #     self.logger.info("Started Azure message queue thread")
        # except Exception as e: 
        #     self.logger.error("Unexpected error %s starting thread" % e)
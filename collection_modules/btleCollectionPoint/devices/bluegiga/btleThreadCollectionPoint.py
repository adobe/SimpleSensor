# This work is based on the following effort
#
# https://github.com/jrowberg/bglib/blob/master/Python/Examples/bled112_scanner.py
#
#

import optparse
from pprint import pprint
from serial import Serial
from libs import BGLib
from threadsafeLogger import ThreadsafeLogger

class BtleThreadCollectionPoint(object):

    def __init__(self,clientEventHandler,btleConfig,loggingQueue,debugMode=False):
        # Logger
        self.loggingQueue = loggingQueue
        self.logger = ThreadsafeLogger(loggingQueue, __name__)

        self.btleConfig = btleConfig
        self.clientEventHandler = clientEventHandler
        self.debug = debugMode
        # define basic BGAPI parser
        self.bgapi_rx_buffer = []
        self.bgapi_rx_expected_length = 0

    def start(self):
        packet_mode = False

        # create BGLib object
        self.ble = BGLib()
        self.ble.packet_mode = packet_mode
        self.ble.debug = self.debug

        # add handler for BGAPI timeout condition (hopefully won't happen)
        self.ble.on_timeout += self.my_timeout

        # on busy hander
        self.ble.on_busy = self.on_busy

        # add handler for the gap_scan_response event
        self.ble.ble_evt_gap_scan_response += self.clientEventHandler

        # create serial port object and flush buffers
        self.logger.info("Establishing serial connection to BLED112 on com port %s at baud rate %s"%(self.btleConfig['BtleDeviceId'],self.btleConfig['BtleDeviceBaudRate']))
        self.serial = Serial(port=self.btleConfig['BtleDeviceId'], baudrate=self.btleConfig['BtleDeviceBaudRate'], timeout=1)
        self.serial.flushInput()
        self.serial.flushOutput()

        # disconnect if we are connected already
        self.ble.send_command(self.serial, self.ble.ble_cmd_connection_disconnect(0))
        self.ble.check_activity(self.serial, 1)

        # stop advertising if we are advertising already
        self.ble.send_command(self.serial, self.ble.ble_cmd_gap_set_mode(0, 0))
        self.ble.check_activity(self.serial, 1)

        # stop scanning if we are scanning already
        self.ble.send_command(self.serial, self.ble.ble_cmd_gap_end_procedure())
        self.ble.check_activity(self.serial, 1)

        # set the TX
        # range 0 to 15 (real TX power from -23 to +3dBm)
        #self.ble.send_command(self.serial, self.ble.ble_cmd_hardware_set_txpower(self.btleConfig['btleDeviceTxPower']))
        #self.ble.check_activity(self.serial,1)

        #ble_cmd_connection_update connection: 0 (0x00) interval_min: 30 (0x001e) interval_max: 46 (0x002e) latency: 0 (0x0000) timeout: 100 (0x0064)
        #interval_min 6-3200
        #interval_man 6-3200
        #latency 0-500
        #timeout 10-3200
        self.ble.send_command(self.serial, self.ble.ble_cmd_connection_update(0x00,0x001e,0x002e,0x0000,0x0064))
        self.ble.check_activity(self.serial, 1)

        # set scan parameters
        #scan_interval 0x4 - 0x4000
        #Scan interval defines the interval when scanning is re-started in units of 625us
        # Range: 0x4 - 0x4000
        # Default: 0x4B (75ms)
        # After every scan interval the scanner will change the frequency it operates at
        # at it will cycle through all the three advertisements channels in a round robin
        # fashion. According to the Bluetooth specification all three channels must be
        # used by a scanner.
        #
        #scan_window 0x4 - 0x4000
        # Scan Window defines how long time the scanner will listen on a certain
        # frequency and try to pick up advertisement packets. Scan window is defined
        # as units of 625us
        # Range: 0x4 - 0x4000
        # Default: 0x32 (50 ms)
        # Scan windows must be equal or smaller than scan interval
        # If scan window is equal to the scan interval value, then the Bluetooth module
        # will be scanning at a 100% duty cycle.
        # If scan window is half of the scan interval value, then the Bluetooth module
        # will be scanning at a 50% duty cycle.
        #
        #active 1=active 0=passive
        # 1: Active scanning is used. When an advertisement packet is received the
        # Bluetooth stack will send a scan request packet to the advertiser to try and
        # read the scan response data.
        # 0: Passive scanning is used. No scan request is made.
        #self.ble.send_command(self.serial, self.ble.ble_cmd_gap_set_scan_parameters(0x4B,0x32,1))
        self.ble.send_command(self.serial, self.ble.ble_cmd_gap_set_scan_parameters(0xC8,0xC8,0))
        self.ble.check_activity(self.serial, 1)

        # start scanning now
        self.ble.send_command(self.serial, self.ble.ble_cmd_gap_discover(1))
        self.ble.check_activity(self.serial, 1)

    # handler to notify of an API parser timeout condition
    def my_timeout(self,sender, args):
        self.logger.error( "BGAPI timed out. Make sure the BLE device is in a known/idle state." )
        # might want to try the following lines to reset, though it probably
        # wouldn't work at this point if it's already timed out:
        self.ble.send_command(self.serial, self.ble.ble_cmd_system_reset(0))
        self.ble.check_activity(self.serial, 1)
        self.ble.send_command(self.serial, self.ble.ble_cmd_gap_discover(1))
        self.ble.check_activity(self.serial, 1)

    def on_busy(self,sender, args):
        self.logger.warn( "BGAPI device is busy." )

    def scan(self):
        # check for all incoming data (no timeout, non-blocking)
        self.ble.check_activity(self.serial)

        # check for all incoming data (with timeout)
        # self.ble.check_activity(self.serial,timeout=1)




creeper-btle-collectionpoint
============================

<h2>Setup for I/O Gear BTLE reader</h2>
<ol>
    <li>sudo apt-get update && sudo apt-get upgrade</li>
    <li>sudo apt-get install libusb-dev</li>
    <li>sudo apt-get install libdbus-1-dev</li>
    <li>sudo apt-get install libglib2.0-dev --fix-missing</li>
    <li>sudo apt-get install libudev-dev</li>
    <li>sudo apt-get install libical-dev</li>
    <li>sudo apt-get install libreadline-dev</li>
    <li>sudo apt-get install libdbus-glib-1-dev</li>
    <li>sudo mkdir bluez</li>
    <li>cd bluez</li>
    <li>sudo wget www.kernel.org/pub/linux/bluetooth/bluez-5.19.tar.gz</li>
    <li>sudo gunzip bluez-5.19.tar.gz</li>
    <li>sudo tar xvf bluez-5.19.tar</li>
    <li>cd bluez-5.19</li>
    <li>sudo ./configure --disable-systemd</li>
    <li>sudo make</li>
    <li>sudo make install</li>
    <li>sudo apt-get install python-bluez</li>
    <li>sudo shutdown -r now</li>
</ol>
<br/>
<h2>Setup for BlueGiga 112 usb</h2>
<ol>
    <li>if windows install the windows BlueGiga 112 usb driver</li>
    <li>`activate ss` or `source activate ss`</li>
    <li>pip install pyserial</li>
    <li>pip install requests</li>
</ol>
<br/><br/>
<h2>General Setup</h2>
<ol>
    <li>install code base</li>
    <li>go into the config directory and tweak the ZMQ endpoints and other needed settings. Also tweak the log settings to match your needs.</li>
    <li>If your on windows you will need to install this driver https://www.bluegiga.com/en-US/download/?file=b2lWNsg0R1SG8qXOhOO1LA&title=BLED112%2520Windows%2520Driver&filename=BLED112_Signed_Win_Drv.zip from this site https://www.bluegiga.com/en-US/products/bled112-bluetooth-smart-dongle</li>
    <li>Also on windows go into the device manager and look at which com port the Bluegiga BTLE device is on.  Put that com port in the collectionPoint.conf file under the property BtleDeviceId</li>
</ol>


Run: python main.py
<br/>
<br/>
<br/>
<h2>BTLE config settings</h2>
The config settings are in config/collectionPoint.conf<br/>
This file is used by the RFID project and the BTLE project so you will see settings for both in the file<br/>
CollectionPointId = your name for the device with no special chars or spaces.  This needs to match the name defined in the collectionPoint id in the Creeper Controller server<br/>
GatewayType = proximity by default.  this has the best testing and support.  This means someone is within range.  It will send an event out when someone passes into range as defined by BtleRssiClientInThreshold setting and will continue to send out an event every ProximityEventInterval (default 5 sec).  When a user leaves the in range an out event will be thrown until BtleRssiClientInThresholdType is exceeded.  In the default case of rssi that means when the users signal strengh is goes outside the BtleRssiClientInThreshold and we count them as missing for BtleClientOutCountThreshold number or leaveTimeInMilliseconds has exceeded we throw an out event. The other gate types are IN,OUT,INOUT.  They have not been used in production but they are used as to throw event in a gate type use case.  So IN throws one event when the BTLE is seen.  OUT throws an out when the user is seen,  and INOUT throws one IN message the first time the user is seen and one OUT for the next time the user is seen.  Example use case would be one BTLE at a IN door and another at an exit door. <br/>
leaveTimeInMilliseconds=if the user has not been in range for this time they are considered not in range<br/>
AbandonedClientCleanupInterval=this is a scheduled time that we run a check for any super old clients left abandoned in the system<br/>
AbandonedClientTimeout=this is the max time last seen that we use when doing our AbandonedClientCleanupInterval clean up<br/>
TestMode = outputs a ton of data to the console in big pretty easy to read events<br/>
InterfaceType = btle or rfid loads the correct drivers for the needed interface <br/>
BtleRssiClientInThreshold=upper end of signal strength where we consider the user in.  IG -68 (about 6 meters) anything closer with stronger signal will be considered in range -65, -50, -44, etc and -78 would be OUT.  Use this to tune your distance IF the BtleRssiClientInThresholdType is set to rssi.  If BtleRssiClientInThresholdType is set to distance this will a number like 5 indicating max meters.  Distance is not good at this time I would stick to rssi<br/>
BtleRssiClientInThresholdType = rssi for keying off signal strength or distance which is a calculation of signal strength and broadcast power to figure distance.  I would use rssi, distance was not perfect yet.<br/>
ProximityEventInterval = how often we will send out a message letting clients know the user is in the area.  IG 5000 will send a client in every 5 seconds.
BtleDeviceId = comport id or device path in osx or linux where device can be found<br/>
BtleAdvertisingMajor = ibeacon major we care about<br/>
BtleAdvertisingMinor = ibeacon minor we care about<br/>
BtleAnomalyResetLimit = if we see spikes and weird responses from a device we will reset after this limit has been seen clearing up their count of IN and OUTS<br/>
BtleRssiNeededSampleSize = this is the number of IN RANGE in events we need to see before we send the IN event.  1 is a good number but in weird environments where there can be crazy spikes up and down you may need to adjust this.<br/>
BtleRssiNeededSampleSize = this is the size of the sample we take before we consider user in range.  I would leave this at 1<br/>
BtleRssiErrorVariance = we use this to detect what we consider an anomaly in the signal<br/>
BtleDeviceBaudRate = sevice read baud rate<br/>
BtleDeviceTxPower = btle device transmit power.  sets the device output power</br>
BtleClientOutCountThreshold = how many times a user needs to be seen out of range before we send the out event</br>
SlackChannelWebhookUrl = we use this to warn us if the service fails to connect to the BTLE reader when started.  We have people watching for messages there and responding in emergencies</br>
<br/>
zmq_conf = this is the ZMQ connection config section.  ZMQ is used to connect to the creeper controller.  You will need to point these settings to your creeper controller.<br/>
Request_timeout = how long we wait to when trying to connect before we consider the connection attempt a failure</br>
Request_retries = how many times we retry to send the event before failing<br/>
Server_endpoint = point this to the protocal://host:port of your zmq endpoint.  If your using the standard creeper controller config just change 127.0.0.1 to your host IP or name</br>
<br/>
<h2>quick config</h2>
change BtleDeviceId,BtleAdvertisingMajor,BtleAdvertisingMinor,SlackChannelWebhookUrl set TestMode to true then run it.  Then I would work on tuning BtleRssiClientInThreshold by watching console output and having someone walk in and out of range and watching the rssi value reported.

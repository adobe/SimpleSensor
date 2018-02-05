# SimpleSensor
![TrackingImage](https://adobeatadobe.d1.sc.omtrdc.net/b/ss/adbeaaagit/1/H.27.5--NS/0?AQB=1&ndh=1&ce=UTF-8&ns=adobeatadobe&pageName=github%3Asimplesensor%3Areadme&g=%2FAdobeAtAdobe%2Fsimplesensor&ch=github)
A Python IoT framework to easily integrate sensors of any kind into your projects.  We also have sample clients for standard web sites and Adobe AEM Screens.


## Table of Contents

  * [About](#about "About")
    * [Communication](#communication-channels "About communication channels")
    * [Events](#event-structure "About event structure")
    * [TO DO](#to-do "TO DO list")
    * [Notes](#notes "Notes")
  * [Installation](#install "Installation steps")
  * [Configure](#configure "Configuration steps")
  * [Examples](#examples "Examples")
    * [Data collection](#data-collection-examples "Data collection point examples")
    * [Javascript integration](#javascript-client-examples "Javascript integration examples")
    * [MQTT](#mqtt-examples "MQTT publishing examples")
    * [Logging](#logging-examples "Logging examples")
  * [Contributing](#contributing "Contributing")
    * [Issues](#issues "Issues")
    * [Pull requests](#pull-requests "Pull requests")
    * [Coding style](#coding-style "Coding style")
    * [Code of conduct](#code-of-conduct "Code of conduct")
  * [License](./LICENSE "License")


## About
The number one goal of this effort was to make it dead simple to use sensors.  So, we've isolated and simplified everything other than data collection.  In SimpleSensor's basic use, just collect data and put it in the queue.  Everything else is handled by the other threads, which we have developed for you.  There may be a bit of configuration that needs to be done to turn on and connect to your communication channels, but that’s it.  You could also extend SimpleSensor and add your own modules and communication channels; we'll gladly take pull requests that follow the [contribution guidelines](#contributing "Contributing").

The application is broken down into the following domains
1. Communication channels
2. Logging
3. Data Collection

For examples on how to use these domains, including things you can do with a collection point, an Adobe AEM client, AEM Screens, or plain old Javascipt, see the [Examples](#examples "Examples") section.

For printable camera enclosures, see the [enclosures subdirectory](./other/enclosures), and feel free to contribute your own!

#### Communication Channels
Today we have two communications channels built into the platform.  We will add more over time.
1. Local websocket
2. MQTT

_Azure IoT Hub_ is currently under development

#### Event Structure
CollectionPointEvent |||
--- | -- | --
**Property**|**Type**|**Description**
`cpid`| String | Unique ID of the collection point, ie. `FD1` or `123456`
`cptype`| String | Label of the collection point type, ie. `FaceDetector` or `WaterHeaterMonitor`
`topic`| String | Label of the event, ie `Detected` or `PowerOn`
`eventTime`| ISO 8601 String | Time stamp of when the message was created
`extendedData` | Dictionary | Key/value pairs of any extra data the sensor needs to emit
`localOnly` | Boolean | Whether or not to broadcast the event on low-cost channels only (placeholder, keep `False` for now)
  

##### TO DO
- Greater platform support (stable Linux and macOS installation instructions)
- Wider range of sensors (taking suggestions, open an [issue!](#contributing "contributing"))
- Greater camera support
- Handle `localOnly` flags
- Target detection zone - specify where in camera feed detections should be triggered using grid system
- Communication from sensors to SimpleSensor (code is there, events are not handled yet)

##### Notes
Today we have two support for two types of cameras in our facedetect module:
- [IDS XS](https://en.ids-imaging.com/store/products/cameras/usb-2-0-cameras/ueye-xs/show/all.html "IDS XS Camera")
- Standard usb webcams

Currently tested platforms:
- Windows 10
- AEM 6.3 w/ AEM Screens
- Python 3.6 w/ Anaconda
- OpenCV 3.2

To shutdown, press ESC while the console has focus.


## Install

Get [Anaconda](https://www.anaconda.com/download/ "Download Anaconda"), from command prompt or Anaconda Shell run:
- `conda create -n ss python=3.6 anaconda`
- `activate ss` or `source activate ss`
- `pip install -r requirements.txt`


## Configure
  
#### Step 1: Configure your base
###### Open `/config/base.conf` in your favorite text editor, configure as needed:
Collection Point Params |||
 --- | --- | --- 
 **Property** | **Type** | **Description** 
`collection_point_id` | String | Becomes the `cpid` property of created `CollectionPointEvents`
`collection_point_type` | String | Becomes the `cptype` property of created `CollectionPointEvents`

Websocket Params |||
--- | --- | --- 
**Property** | **Type** | **Description** 
`websocket_port` | Integer | Port number to use for websocket
`websocket_host` | String | Host name to use for websocket, ie. `127.0.0.1` or `0.0.0.0` to allow all network machines access

Azure Params |||
 --- | --- | --- 
**Property** | **Type** | **Description** 
`azure_message_timeout` | Integer | Time until a message times out
`azure_timeout` | Integer | Time until Azure connection times out
`azure_minimum_polling_time` | Integer | Frequency at which to poll for messages
`azure_device_created` | Boolean | Flag to set whether the client has already been initialized, ie. exists on the Azure Console

MQTT Params |||
 --- | --- | --- 
**Property** | **Type** | **Description** 
`mqtt_host` | String | Host name of MQTT broker ie. `io.adafruit.com`
`mqtt_port` | Integer | Port number of MQTT broker, ie. `1883`
`mqtt_feed_name` | String | Feed name to publish to
`mqtt_username` | String | Username to MQTT broker
`mqtt_keep_alive` | Integer | Maximum period in seconds allowed between communications with the broker. If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker.
`mqtt_publish_json` | Boolean | Flag to publish entire message contents as JSON string
`mqtt_publish_face_values` | Boolean | Flag to publish only the values of the extended data to respective feeds. 
**If neither `mqtt_publish_face_values` or `mqtt_publish_json` are enabled** | | Values of the extended data field are published to their own feeds. See [MQTT Examples](#mqtt-examples "MQTT Examples").

**NOTE:** See also [Paho MQTT](https://github.com/eclipse/paho.mqtt.python "Paho MQTT")

Modules |||
 --- | --- | --- 
**Property** | **Type** | **Description** 
`collection_modules` | Array | Collection point module folder names to use, ie. `camCollectionPoint`
`communication_modules` | Array | Communication method folder names to use, ie. `websocketServer`

**NOTE:** These are folder names, not file/class/module names. When adding new modules keep the folder names unique.

Etc |||
 --- | --- | --- 
**Property** | **Type** | **Description** 
`test_mode` | Boolean | Flag to allow for debugging workflows
`slack_channel_webhook_url` | String | Unused for now - for future Slack integration
 
#### Step 2: Configure your secrets
###### Open `/config/secrets.conf.sample` in your favorite text editor, include keys needed by communication methods you wish to use:
Secrets |||
 --- | --- | --- 
 **Property** | **Type** | **Description** 
`mqtt_key` | String | API key or password for your MQTT broker account
`azure_connection_string` | String | Connection string retrieved from your Azure portal

**NOTE:** Save this file as secrets.conf

#### Step 3: Configure your modules

###### Enable/disable packaged modules
In `config/base.conf`, add/remove the folder names of the modules you wish to use. For example, to use both websocket and MQTT messages, set your `communication_modules` to `["websocketServer", "mqttClient"]`

###### Create your own collection point module:
1. Duplicate and rename the `/collection_modules/baseCollectionPoint` directory 
2. Add/replace `collection_modules` array in `config/base.conf` with the name of your new collection point's folder
3. Write your initialization logic in the `__init__()` function
4. Write your collection loop logic in the `run()` function
5. Optionally import constants through a module configuration file, use `camCollectionPoint` as an example

**NOTE:** For details on the included camera/face detection module, see the [module's README](./collection_modules/camCollectionPoint/README.md "camCollectionPoint README")
  

## Examples

#### Data Collection Examples
These are some samples of things you can do within the `run()` function of your `collectionPoint.py`

###### Create a CollectionPointEvent:
```python
_cpType = 'elite_sensor'
_cpid = 'sensor_1337'
_topic = 'Detected'
_coords = (47.6062, 122.3321)
_localOnly = False
msg = (_cpid, _cpType, _topic, extendedData={'location':_coords}, _localOnly)
```

###### Send an event:
```python
self.outQueue.put(msg)
```

###### Creating a MultiTracker:
```python
self.mTracker = MultiTracker("KCF", self.moduleConfig, self.loggingQueue)
```

###### Adding an tracker to your MultiTracker:
```python
ok = self.mmTracker.add(bbox={'x':x,'y':y,'w':w,'h':h}, frame=frame)
```

#### Javascript Client Examples
A sample Javascript client connection via websocket can be found [here](other/examples/standalone_web/README.md "Javascript Client Sample")

###### Create a client:
```javascript
<div id="displayEventsElement"></div>
<script src="websocketClient.js" type="text/javascript"></script>
document.addEventListener("DOMContentLoaded", function(event) {
  var _displayEventsElement = document.getElementById('displayEventsElement');
  var cecWebsocketClient = new WebsocketClient("127.0.0.1", 13254); // Connect to localhost at port 13254
});
```

###### Listen for messages:
```javascript
websocketClient.addEventListener("message", function(eventData){
  // Do something with the event data
  displayEventsElement.append(JSON.stringify(eventData));
});
```

##### MQTT Examples
Publishing messages to MQTT requires an MQTT broker ([Adafruit IO](https://learn.adafruit.com/adafruit-io/mqtt-api "Adafruit IO MQTT API"), for example) to be configured and enabled in `/config/base.conf`. There are two ways to publish MQTT messages currently. 


###### Option 1: Publish JSON
The first method is to publish the entire JSON string dump of the message, if your broker supports it. This is enabled by setting `mqtt_publish_json` to `True` in `/config/base.conf`. The MQTTClient dumps the JSON into utf8 encoding and publishes it like so:
```python
_payload = json.dumps(_msg.__dict__).encode('utf8')
self._client.publish('{0}/feeds/{1}'.format(self._username, _feedName), payload=_payload)
```

###### Option 2: Publish by Key/Value -> Feed/Value
The second method is to publish the values of each key in the extended data to separate feeds. To use this method, set both `mqtt_send_json` and `mqtt_publish_face_values` to `False` in `/config/base.conf`. The `MQTTClient` will now publish each field of the `extendedData` dictionary message to it's own MQTT feed. 

For example, the message created by this code:
```
_cpType = 'elite_sensor'
_cpid = 'sensor_1337'
_topic = 'Detected'
_localOnly = False
_extendedData = {
    "age": 23,
    "gender": 0,
    "glasses": 1,
    "beard": 0.7
}
msg = (_cpid, _cpType, _topic, extendedData=_extendedData, _localOnly)
```
Would result in 4 publish events: 
1. `username/feeds/age` would receive an update value of `23`
2. `username/feeds/gender` would receive an update value of `0`
3. `username/feeds/glasses` would receive an update value of `1`
4. `username/feeds/beard` would receive an update value of `0.7`

**Note** A modified version of this function is also in `mqttClient.py`, which can be used in conjunction with the Azure Face API (or another prediction engine with the same output structure) and the sample `camCollectionPoint`. It only publishes prediction data, and flattens a dictionary of values to an average.


#### Logging Examples
###### Logging levels:
```python
self.logger.info("Starting a thing")
```
```python
self.logger.debug("Made it here!1112")
```
```python
self.logger.warning("This could be bad")
```
```python
self.logger.warn("This also could be bad")
```
```python
self.logger.critical("This *is* bad")
```
```python
self.logger.error("Failed to do the thing: %s"%error)
```


## Contributing
Make a cool collection module that you want to share?  Or fix up a bug?  Maybe you made SimpleSensor work on a new platform?  We're open for contributions, we just ask that they follow some guidelines to keep things clean and efficient.

If you're looking for a place to jump in with contributing, check out our [TO DO](#to-do "TO DO list")

All submissions should come in the form of pull requests and need to be reviewed by project contributors. Read [GitHub's pull request documentation](https://help.github.com/articles/about-pull-requests/) for more information on sending pull requests.

#### Issues
Issues should either include a proposal for a feature or, in the case of bugs, include the expected behavior, the actual behavior, your environment details, and *ideally* steps to reproduce. They should also *ideally* address actual issues with the code, not issues with setting up the environment. 
Please follow the [issue template](./ISSUE_TEMPLATE.md) for consistency.

#### Pull Requests
Pull requests should include references to the title of the issue, and changes proposed in the pull request.
Please follow the [pull request template](./PULL_REQUEST_TEMPLATE.md) for consistency.

#### Coding Style
Try to make your code readable first and foremost. 
Then match the code that surrounds it. 
Otherwise follow these current styles:
- mixedCase function/variable/object names
- mixedCase file and folder names
- \_mixedCase constant names
- lowercase\_with\_underscores config file settings, ie. `some_prop = 1337`
- CamelCase config object variable, ie. `self.config['SomeProp']`
- docstrings for all functions, ie. `""" Function summary """`

#### Code Of Conduct
This project adheres to the Adobe [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to FILLINEMAILHERE.

![AnalyticsImage](https://adobeatadobe.d1.sc.omtrdc.net/b/ss/adbeaaagit/1/H.27.5--NS/0?AQB=1&ndh=1&ce=UTF-8&ns=adobeatadobe&pageName=github%3ASimpleSensor%3Areadme&g=%2FAdobeAtAdobe%2FSimpleSensor&ch=github)

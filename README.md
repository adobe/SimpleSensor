# SimpleSensor - DOCS WIP
A modular and threaded Python IoT framework to easily integrate sensors into your projects.

## Table of Contents

  * [About](#about "About")
    * [Modules](#modules "About modules")
      * [Collection modules](#collection-modules "About collection modules")
      * [Communication modules](#communication-modules "About communication modules")
    * [Logger](#logger "About logger")
  * [Setup](#setup "Setup steps")
  * [Documentation](#documentation "Documentation")
    * [1. Shared](#1-shared "Shared module documentation")
      * [1.1. Message](#11-message "Message class documentation")
      * [1.2. ModuleProcess](#12-moduleprocess "ModuleProcess class documentation")
      * [1.3. ThreadsafeLogger](#13-threadsafelogger "ThreadsafeLogger class documentation")
    * [Contributed modules](https://github.com/AdobeAtAdobe/SimpleSensor_contrib "contributed modules")
  * [Contributing](#contributing "Contributing")
    * [Issues](#issues "Issues")
    * [Pull requests](#pull-requests "Pull requests")
    * [Code of conduct](#code-of-conduct "Code of conduct")
  * [License](./LICENSE "License")


## About
The goal of this project is to make it dead simple to add sensors to your projects. SimpleSensor is modular, you can pick and choose pieces to use from the [contributed modules repo](https://github.com/AdobeAtAdobe/SimpleSensor_contrib) or build your own modules to custom needs. Feel free to contribute back modules, too.

In a basic use case a collection module can simply send messages along a communication module when a certain state or event is detected in a collection module. You can also orchestrate more complicated flows by communicating between modules before sending the message along communication channels.

For samples of how to integrate SimpleSensor with clients such as AEM Screens and vanilla Javascript, check out the [samples branch of the contribution repository](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/samples "Contribution repository samples branch").

### Modules

Modules are the building blocks of SimpleSensor. They typically have at least 4 parts:
1. **Main module class**
2. **Config loader**
3. **Zero or more config files**
4. **An \_\_init\_\_.py**, you must import the module class `as CollectionModule` (this is to simplify dynamic module imports)


The main module class extends the [ModuleProcess](#12-moduleprocess "ModuleProcess class documentation") base class, and runs on it's own thread or process. The logic of this class can be broken down into 3 stages:

1. **Initialize** :arrow_right: perform any set up needed, either in `__init__()` or in `run()` before you begin the loop.
2. **Loop** :arrow_right: main logic of the module, repeats until a message is read to shutdown.
3. **Close** :arrow_right: clean up anything that won't clean itself.


#### Collection Modules
Used to collect data from a sensor, check if that data means something special has occurred, and send a [Message](#11-message "Message class documentation") if it has.

Example modules: [bluetooth (BTLE) beacon](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/btle_beacon "BTLE module"), [demographic camera](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/demographic_camera "demographic camera module")

1. **Initialize** :arrow_right: initialize the sensor you'll be polling, set event condition, create variables and spawn threads if needed.

2. **Loop** :arrow_right: poll the sensor; if the condition is met, make a [Message](#11-message "Message class documentation") instance and put it on the queue with `put_message()`.

3. **Close** :arrow_right: join threads you spawned, clean up the sensor, and mark the module as `alive=False`.


#### Communication Modules
Used to send `Messages` along a communication channel. 

Examples modules: [MQTT](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/mqtt_client "MQTT client module"), [websocket server](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/websocket_server "websocket server module"), [websocket client](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/websocket_client "websocket client module")

1. **Initialize** :arrow_right: perform logic needed to operate the communication channel and the module, for example, handshakes or opening ports.

2. **Loop** :arrow_right: poll the `inQueue` for messages to send along the communication channel.

3. **Close** :arrow_right: reverse whatever you did in initialize, then mark the module as `alive=False`.

#### Logger
The [`ThreadsafeLogger`](#13-threadsafelogger "ThreadsafeLogger class documentation") is a simple facade to add messages to the logging queue, which is an instance of `multiprocessing.Queue` that is shared among all modules. The logging queue is then consumed by the [`LoggingEngine`](./maxed/simplesensor/loggingEngine.py "Logging engine") which passes those formatted messages to the Python logging module.

The default configuration logs to `stderr`, as well as to a file located in the `<run directory>/logs` directory.

To configure custom logging parameters, change the [logging config file](./simplesensor/config/logging.conf "Logging config file").


## Setup
There are two ways to use SimpleSensor:

#### Manually
1. **Configure base** :arrow_right: `/config/base.conf`

2. **Add modules** :arrow_right: write, download, clone 

3. **Configure modules** :arrow_right: `<some module>/config/module.conf` and, if necessary, `<some module>/config/secrets.conf`

4. **Run** :arrow_right: `python ./simplesensor/main.py`

#### CLI
1. **Install** :arrow_right: `pip install .` from the same directory as `setup.py`

2. **Add/configure modules** :arrow_right: `scly install --type <communication or collection> --name <module branch name>`

3. **Configure base** :arrow_right: `scly config --name base`

4. **Run** :arrow_right: `scly start`

More details on the CLI can be found in the [CLI readme](./simplesensor/cli/README.md "CLI Readme").


## Documentation

### 1. Shared

#### 1.1. Message
Source: [simplesensor/shared/message.py](https://github.com/AdobeAtAdobe/SimpleSensor/blob/maxed/simplesensor/shared/message.py "Message class source code")

_class_ simplesensor.shared.message.**Message**(_topic, sender_id, sender_type, extended_data, recipients, timestamp_)

**Property**|**Required**|**Type**|**Description**
--- | -- | -- | --
`topic`| Yes | String | Message type/topic
`sender_id`| Yes | String | ID property of original sender
`sender_type`| No | String | Type of sender, ie. collection point type, module name, hostname, etc
`extended_data` | No | Dictionary | Payload to deliver to recipient(s)
`recipients` | No | String or list[str] | Module name(s) to which the message will be delivered, ie. "websocket_server". <br> - Use an array of strings to define multiple modules to send to. <br> - Use "all" to send to all available modules. <br> - Use "local_only" to send only to modules with `low_cost` prop set to `True`. <br> - Use "communication_modules" to send only to communication modules. <br> - Use "collection_modules" to send only to collection modules. <br>
`timestamp`| No | ISO 8601 String | Timestamp of when the message was created


#### 1.2. ModuleProcess
Source: [simplesensor/shared/moduleProcess.py](https://github.com/AdobeAtAdobe/SimpleSensor/blob/maxed/simplesensor/shared/moduleProcess.py "ModuleProcess class source code")

_class_ simplesensor.shared.moduleProcess.**ModuleProcess**(_baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue_)

Base class for modules to inherit. Implements functions that are commonly used, defines the correct queue usage and parameter order.

This should not be instantiated itself, instead you should extend it with your own module and can initialize it in the `__init__()` function with `ModuleProcess.__init__(self, baseConfig, pInBoundQueue, pOutBoundQueue, loggingQueue)`.

For an example of how it can be used, see 

#### 1.3. ThreadsafeLogger
Source: [simplesensor/shared/threadsafeLogger.py](https://github.com/AdobeAtAdobe/SimpleSensor/blob/maxed/simplesensor/shared/threadsafeLogger.py "ThreadsafeLogger class source code")

_class_ simplesensor.shared.threadsafeLogger.**ThreadsafeLogger**(_queue, name_)

Docs go here


## Contributing
For contributing modules, please check out our [module contribution repo](https://github.com/AdobeAtAdobe/SimpleSensor_contrib)

All submissions should come in the form of pull requests and will be reviewed by project contributors. Read [GitHub's pull request documentation](https://help.github.com/articles/about-pull-requests/) for more information on sending pull requests.

#### Issues
Issues should either include a proposal for a feature or, in the case of bugs, include the expected behavior, the actual behavior, your environment details, and *ideally* steps to reproduce. They should also *ideally* address actual issues with the code, not issues with setting up the environment. 
Please follow the [issue template](./ISSUE_TEMPLATE.md) for consistency.

#### Pull Requests
Pull requests should include references to the title of the issue, and changes proposed in the pull request.
Please follow the [pull request template](./PULL_REQUEST_TEMPLATE.md) for consistency.

#### Code Of Conduct
This project adheres to the Adobe [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

![AnalyticsImage](https://adobeatadobe.d1.sc.omtrdc.net/b/ss/adbeaaagit/1/H.27.5--NS/0?AQB=1&ndh=1&ce=UTF-8&ns=adobeatadobe&pageName=github%3ASimpleSensor%3Areadme&g=%2FAdobeAtAdobe%2FSimpleSensor&ch=github)

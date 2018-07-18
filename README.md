# SimpleSensor - DOCS WIP
A modular and threaded Python IoT framework to easily integrate sensors into your projects.

## Table of Contents

  * [About](#about "About")
    * [Collection Modules](#collection-modules "About collection modules")
    * [Communication Modules](#communication-modules "About communication modules")
    * [Logger](#logger "About logger")
  * [Setup](#setup "Setup steps")
  * [Add Modules](#add-modules "Module installation steps")
  * [Configure](#configure "Configuration steps")
  * [Documentation](#documentation "Documentation")
    * [Messages](#message-fields "About message structure")
    * [Usage](#usage "Usage")
    * [Contributed Modules](https://github.com/AdobeAtAdobe/SimpleSensor_contrib "contributed modules")
  * [Contributing](#contributing "Contributing")
    * [Issues](#issues "Issues")
    * [Pull requests](#pull-requests "Pull requests")
    * [Code of conduct](#code-of-conduct "Code of conduct")
  * [License](./LICENSE "License")


## About
The goal of this project is to make it dead simple to add sensors to your projects. SimpleSensor is modular, you can pick and choose pieces to use from the [contributed modules repo](https://github.com/AdobeAtAdobe/SimpleSensor_contrib) or build your own modules to custom needs. Feel free to contribute back modules, too.

In a basic use case a collection module can simply send messages along a communication module when a certain state or event is detected in a collection module. You can orchestrate more complicated flows by communicating between modules before sending the message to collection points.

SimpleSensor has the following 3 domains
1. [Collection modules](#collection-modules "About collection modules")
2. [Communication modules](#communication-modules "About communication modules")
3. [Logging](#logger "About logger")

For samples of how to integrate SimpleSensor with clients such as AEM Screens and vanilla Javascript, check out the [samples branch of the contribution repository](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/samples "Contribution repository samples branch").

#### Collection Modules
Collection modules are used to collect data. They extend the [`ModuleProcess`](./simplesensor/shared/moduleProcess.py "Module process base class") base class and have 3 parts:

1. Initialize

Anything that happens before the module's thread is started and it's `run` function is called, as well as any logic inside the `run` function but before starting the main module loop. Here you should initialize the sensor you'll be polling, spawn any additional needed threads, etc.

2. Loop

Poll the sensor, if your condition is met, make a [message](#message-fields "Message fields") instance and put it on the queue with `put_message`.

3. Clean up

Join threads you spawned, clean up the sensor, and mark the module as `alive=False`.


#### Communication Modules
Communication modules are used to send data along one specific communication channel. They extend the same [`ModuleProcess`](./simplesensor/shared/moduleProcess.py "Module process base class") base class as collection modules and also have 3 parts:

1. Initialize

Anything that happens before the module's thread is started and it's `run` function is called, as well as any logic inside the `run` function but before starting the main module loop. Similar to collection modules, you should spawn threads and create instances of classes needed to operate the module and the communication channel. For example, performing handshakes or opening ports.

2. Loop

Poll the `inQueue` for messages to send along the communication channel.

3. Clean up

Close ports, join threads, whatever you need to do to close the communication channel. Then mark the module as `alive=False`.

#### Logger
The [`ThreadsafeLogger`](./simplesensor/shared/threadsafeLogger.py "Threadsafe logger") is a straightforward facade to add messages to the logging queue. The logging queue is then consumed by the [`LoggingEngine`](./maxed/simplesensor/loggingEngine.py "Logging engine") which passes those formatted messages to the Python logging module.

To configure custom logging parameters, change the [logging config file](./simplesensor/config/logging.conf "Logging config file").


## Setup
There are two ways to use SimpleSensor:

#### Manually
1. Configure

Configure `/config/base.conf`.

2. Add modules

Write, download, clone modules. Add them to the correct directory. 

3. Configure modules

Configure `/config/module.conf` and, if necessary, `/config/secrets.conf`.

4. Run

`python ./simplesensor/main.py`

#### CLI
1. Install 

`pip install .` from the same directory as `setup.py`

2. Add modules

`scly install --type <communication or collection> --name <module branch name>`

3. Configure

`scly config --name base`

4. Run

`scly start`

More details on the CLI can be found in the [CLI readme](./simplesensor/cli/README.md "CLI Readme").


## Documentation


#### Message Fields
**Property**|**Required**|**Type**|**Description**
--- | -- | -- | --
`topic`| Yes | String | Message type/topic
`sender_id`| Yes | String | ID property of original sender
`sender_type`| No | String | Type of sender, ie. collection point type, module name, hostname, etc
`extended_data` | No | Dictionary | Payload to deliver to recipient(s)
`recipients` | No | String or list[str] | Module name(s) to which the message will be delivered, ie. "websocket_server". <br> - Use an array of strings to define multiple modules to send to. <br> - Use "all" to send to all available modules. <br> - Use "local_only" to send only to modules with `low_cost` prop set to `True`. <br> - Use "communication_modules" to send only to communication modules. <br> - Use "collection_modules" to send only to collection modules. <br>
`timestamp`| No | ISO 8601 String | Timestamp of when the message was created

See also, the [`Message`](./shared/message.py "Message class") class.


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

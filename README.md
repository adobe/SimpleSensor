# SimpleSensor - DOCS WIP
A modular and threaded Python IoT framework to easily integrate sensors into your projects.

## Table of Contents

  * [About](#about "About")
  * [Install](#install "Installation steps")
  * [Configure](#configure "Configuration steps")
  * [Documentation](#documentation "Documentation")
    * [Collection Modules](#collection-modules "About collection modules")
    * [Communication Modules](#communication-modules "About communication modules")
    * [Logger](#logger "About logger")
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

Modules can communicate to one another in chains, or in the simplest case, a collection module will just send messages along a communication module when a certain state/event/etc is detected.

SimpleSensor has the following 3 domains
1. [Collection modules](#collection-modules "About collection modules")
2. [Communication modules](#communication-modules "About communication modules")
3. [Logging](#logger "About logger")

For samples of how to integrate SimpleSensor with clients such as AEM Screens and vanilla Javascript, check out the [samples branch of the contribution repository](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/samples "Contribution repository samples branch").


## Install


## Configure


## Documentation

#### Collection Modules

#### Communication Modules

#### Logger

#### Message Fields
**Property**|**Required**|**Type**|**Description**
--- | -- | -- | --
`topic`| Yes | String | Message type/topic
`sender_id`| Yes | String | ID property of original sender
`sender_type`| No | String | Type of sender, ie. collection point type, module name, hostname, etc
`extended_data` | No | Dictionary | Payload to deliver to recipient(s)
`recipients` | No | String or list[str] | Module name(s) to which the message will be delivered, ie. "websocket_server". <br> - Use an array of strings to define multiple modules to send to. <br> - Use "all" to send to all available modules. <br> - Use "local_only" to send only to modules with `low_cost` prop set to `True`. <br> - Use "communication_modules" to send only to communication modules. <br> - Use "collection_modules" to send only to collection modules. <br>
`timestamp`| No | ISO 8601 String | Timestamp of when the message was created

#### Usage


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

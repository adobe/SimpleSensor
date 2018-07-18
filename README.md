# SimpleSensor
A modular and threaded Python IoT framework to easily integrate sensors into your projects.

## Table of Contents

  * [About](#about "About")
  * [Install](#install "Installation steps")
  * [Configure](#configure "Configuration steps")
  * [Docs](#documentation "Documentation")
    * [Communication Modules](#communication-modules "About communication modules")
    * [Collection Modules](#collection-modules "About collection modules")
    * [Messages](#message-fields "About message structure")
    * [Usage](#usage "Usage")
  * [Contributing](#contributing "Contributing")
    * [Issues](#issues "Issues")
    * [Pull requests](#pull-requests "Pull requests")
    * [Code of conduct](#code-of-conduct "Code of conduct")
  * [License](./LICENSE "License")


## About
The goal of this project is to make it dead simple to add sensors to your projects. SimpleSensor is a modular structure, where you can pick and choose parts to communicate with each other or along communication channels

So, we've isolated and simplified everything other than data collection.  In SimpleSensor's basic use, just collect data and put it in the queue.  Everything else is handled by the other threads, which we have developed for you.  There may be a bit of configuration that needs to be done to turn on and connect to your communication channels, but that’s it.  You could also extend SimpleSensor and add your own modules and communication channels; we'll gladly take pull requests that follow the [contribution guidelines](#contributing "Contributing").

The application is broken down into the following domains
1. Collecting data from sensors
2. Communicating messages based on collected data
3. Logging to files

See the [Samples](#samples "Samples") section for usage with AEM Screens and sample clients.


## Install


## Configure


## Documentation

#### Communication Modules

#### Communication Modules

#### Message Fields
**Property**|**Required**|**Type**|**Description**
--- | -- | -- | --
`topic`| Yes | String | Message type/topic
`sender_id`| Yes | String | ID property of original sender
`sender_type`| No | String | Type of sender, ie. collection point type, module name, hostname, etc
`extended_data` | No | Dictionary | Payload to deliver to recipient(s)
`recipients` | No | String/list[str] | module name(s) to which the message will be delivered, ie. "websocket_server". 
use an array of strings to define multiple modules to send to.
								use 'all' to send to all available modules.
								use 'local_only' to send only to modules with `low_cost` prop set to True.
								use 'communication_modules' to send only to communication modules.
								use 'collection_modules' to send only to collection modules.
`timestamp`| No | ISO 8601 String | Timestamp of when the message was created

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

#### Code Of Conduct
This project adheres to the Adobe [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to FILLINEMAILHERE.

![AnalyticsImage](https://adobeatadobe.d1.sc.omtrdc.net/b/ss/adbeaaagit/1/H.27.5--NS/0?AQB=1&ndh=1&ce=UTF-8&ns=adobeatadobe&pageName=github%3ASimpleSensor%3Areadme&g=%2FAdobeAtAdobe%2FSimpleSensor&ch=github)

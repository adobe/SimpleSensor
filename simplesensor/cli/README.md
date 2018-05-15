# CLI

### Commands
`scly`
- Main entry point command, prefaces any other command

`scly start`
- Runs SimpleSensor

`scly install`
- Install module from a git repo/branch
- The branch should have a directory called either `collection_modules` or `communication_modules`, under which it should have a folder by the same name as the branch
- For example, refer to these contrib module branches: [websocket-client](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/websocket-client), [demographic-camera](https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/demographic-camera)
- Also runs configuration on the module after installation, by default. To disable, add flag `--config false`

`scly config`
- Configure parameters of the base system (ie. which modules to run)
- Configure parameters of specific module (ie. port or ip address for websocket)
- Configure parameters of logging (ie. format of output)

`scly help`
- List possible commands

### Arguments
| Command       |         Arguments            |  Description |
|---------------|------------------------------|--------------|
| `scly start`  |   `--collection` [optional]  | Collection point modules to run. Must provide them in hyphen-broken/comma-delimited form (ie. `--collection websocket-server,websocket-client,mqtt`)  |
|               | `--communication` [optional] | See above, but for communication modules. |
| `scly install`|    `--source` [optional]     | Git repo containing the module you'd like to install (default is `https://github.com/AdobeAtAdobe/SimpleSensor_contrib.git`)|
|               |     `--name` [required]      | Branch name of module to install, also hyphen-broken (ie. `websocket-client`)|
|               |      `--type` [required]     | Type of module to install, either `communication` or `collection` |
| `scly config` |      `--name` [required]     | Name of module (ie. `websocket-client`), or `base` or `logging` |
|               |      `--type` [optional]     | Type of module, required if not configuring base or logging |


### Troubleshooting

###### Can't install a module?
Make sure your git is working with the `git` command in the terminal


###### Failed to delete error after installing module?
Delete the directory specified in the error message manually.

###### Manually configure settings?
To manually configure the base or module after installing, look inside your environment's site-packages directory.
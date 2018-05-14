""" CLI module configuration controller """

import os

def config(args):
	if args.name is None:
		print("Error: Must provide a module name" +
			"(ie. `--name module-name`)")
	elif str(args.name).lower() == 'base':
		# Configure the base settings
		configure_base()
	elif str(args.name).lower() == 'logging':
		configure_logging()
	elif args.type is None:
		print("Error: Must provide a module type" +
		 "(ie. `--type communication` or `--type collection`)")
	elif str(args.type) != "communication" and str(args.type) != "collection":
		print("Error: Invalid module type `%s`."%args.type +
			"Only `collection` and `communication` supported.")
	else:
		# all good
		MODULE_DIR = os.path.abspath(os.path.join(__file__,'../../%s_modules/%s'%(args.type, to_camel_case(args.name))))
		if not os.path.isdir(MODULE_DIR):
			print("Directory does not exist, module may not exist." +
				"Try installing module first with `scly install --name %s --type %s`."%(args.name, args.type))
			exit()

		configure_module(args.name, args.type, MODULE_DIR)

def configure_module(module_name, module_type, module_dir):
	""" 
	Read [path]/config/module.conf and [path]/config/secrets.conf.
	Have user enter their config values, or default if none chosen.
	"""
	MODULE_CONF = os.path.join(module_dir, 'config', 'module.conf')
	SECRETS_CONF = os.path.join(module_dir, 'config', 'secrets.conf')

	# First, try to configure module
	# if not os.path.isdir(MODULE_DIR):
	try:
		with open(MODULE_CONF, 'r') as f:
			configs = f.readlines()
			configs = [x.strip() for x in configs] 

			print('')
			print('')
			print('###################################################')
			print('############           CONFIG          ############')
			print('###################################################')
			print('Check module README for more details on each param')
			print('https://github.com/AdobeAtAdobe/SimpleSensor_contrib/tree/%s'%module_name)
			print('')
			print('param_name (default): yoursetting')

			new_configs = []
			for config in configs:
				if not config.startswith('#') and not (config.startswith('[') and config.endswith(']')):
					# split line by colon and let user set parameter
					csplit = config.split(':')
					csplit[1] = input('%s (%s):'%(csplit[0], csplit[1])) or csplit[1]
					new_configs.append('%s:%s'%(csplit[0], csplit[1]))
				else:
					new_configs.append(config)
		f.close()

		with open(MODULE_CONF, 'w') as f:
			# write new config values to file
			f.truncate()
			for config in new_configs:
				f.write("%s\n" % config)
	except Exception as e:
		pass

	# Now configure secrets if there are any
	try:
		with open(SECRETS_CONF, 'r') as f:
			configs = f.readlines()
			configs = [x.strip() for x in configs] 

			new_configs = []
			for config in configs:
				if not config.startswith('#') and not (config.startswith('[') and config.endswith(']')):
					# split line by colon and let user set parameter
					csplit = config.split(':')
					csplit[1] = input('%s (%s):'%(csplit[0], csplit[1])) or csplit[1]
					new_configs.append('%s:%s'%(csplit[0], csplit[1]))
				else:
					new_configs.append(config)
		f.close()

		with open(SECRETS_CONF, 'w') as f:
			# write new config values to file
			f.truncate()
			for config in new_configs:
				f.write("%s\n" % config)
	except Exception as e:
		pass

	print('')
	print('Configured.')
	print('To change your configuration settings, run `scly config --type %s --name %s`'%(module_type, module_name))
	print('')

def configure_base():
	pass

def configure_logging():
	pass

def get_configuration():
	pass

def to_camel_case(hyphenated):
	""" Convert hyphen broken string to camel case. """
	components = hyphenated.split('-')
	return components[0] + ''.join(x.title() for x in components[1:])
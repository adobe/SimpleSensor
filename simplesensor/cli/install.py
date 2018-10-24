"""
CLI install controller
"""

import os, shutil, stat, errno
from .config import configure_module
import logging
import pip
import time

def install(args):
	from git import Repo
	CONTRIB_URL = 'https://github.com/AdobeAtAdobe/SimpleSensor_contrib.git'
	logger = logging.getLogger(__name__)

	if args.name is None:
		logger.error("Error: Must provide a module name" +
			"(ie. `--name module-name`)")
	elif args.type is None:
		logger.error("Error: Must provide a module type" +
		 "(ie. `--type communication` or `--type collection`)")
	elif str(args.type) != "communication" and str(args.type) != "collection":
		logger.error("Error: Invalid module type `%s`."%args.type +
			"Only `collection` and `communication` supported.")
	else:
		if args.source is not None:
			logger.error("Source param set, overriding with source `%s`"%args.source)
			CONTRIB_URL = args.source

		DIR_NAME = args.name
		TEMP_DIR_NAME = DIR_NAME + '_temp'
		TEMP_DIR_PATH = os.path.abspath(os.path.join(__file__,'../../%s_modules/%s'%(args.type, TEMP_DIR_NAME)))
		DEST_DIR_PATH = os.path.abspath(os.path.join(__file__,'../../%s_modules/%s'%(args.type, DIR_NAME)))

		logger.info('Installing module "%s" to %s'%(TEMP_DIR_NAME, TEMP_DIR_PATH))

		if os.path.isdir(TEMP_DIR_PATH):
			# shutil.rmtree(TEMP_DIR_NAME)
			logger.warn("Temp install directory exists, may be left over from previous install. " +
				"Try deleting directory manually: `%s`."%TEMP_DIR_PATH)
			exit()

		if os.path.isdir(DEST_DIR_PATH):
			# shutil.rmtree(DIR_NAME)
			logger.warn("Destination directory exists, requirement might already be satisfied. " +
				"If not, try deleting directory `%s`."%DEST_DIR_PATH)
			exit()

		os.mkdir(TEMP_DIR_PATH)

		# Make a repo pointing to the contrib modules, checkout the module name and pull it
		repo = Repo.init(TEMP_DIR_PATH)
		origin = repo.create_remote('origin', CONTRIB_URL)
		assert origin.exists()
		origin.fetch()
		checkout_branch(repo, origin, args.name)
		origin.pull()

		# Move module dir to correct folder
		MODULE_PATH = os.path.abspath(os.path.join(TEMP_DIR_PATH, '../'))
		try:
			shutil.move(
				os.path.join(TEMP_DIR_PATH, '%s_modules'%args.type, args.name),
				MODULE_PATH
				)
		except Exception as e:
			logger.error("Error moving module: %s."%e)
			logger.error(e.__class__.__name__)

		# Delete the repo
		try:
			repo.git.clear_cache()
			repo.close()
			shutil.rmtree(TEMP_DIR_PATH, ignore_errors=False, onerror=remove_readonly)
		except Exception as e:
			logger.error("Error deleting temporary module path `%s`. Try deleting it manually."%TEMP_DIR_PATH)

		MODULE_DIR = os.path.join(MODULE_PATH, args.name)

		# Install requirements
		install_requirements(os.path.join(MODULE_DIR, 'requirements.txt'))

		# Configure module
		configure_module(args.name, args.type, MODULE_DIR)

def checkout_branch(repo, origin, branch_name):
	""" Create a new head and checkout the branch called branch_name (--name argument) """
	logger = logging.getLogger(__name__)
	try:
		repo.create_head(branch_name, origin.refs[branch_name])
		repo.heads[branch_name].set_tracking_branch(origin.refs[branch_name])
		repo.heads[branch_name].checkout()
	except Exception as e:
		logger.error("Error: %s"%e)

def to_camel_case(hyphenated):
	""" Convert hyphen broken string to camel case. """
	components = hyphenated.split('-')
	return components[0] + ''.join(x.title() for x in components[1:])

def remove_readonly(func, path, exc):
	""" Clear the readonly bit and reattempt the removal """
	try:
		os.chmod(path, stat.S_IWRITE)
		func(path)
	except Exception as e:
		print('Error removing readonly: ', e)

def install_requirements(req_file):
	""" Parse `requirements.txt` line by line and install each requirement.
	Confirm with user before installing them. """
	try:
		with open(req_file, 'r') as f:
			requirements = f.readlines()
			requirements = [x.strip() for x in requirements] 

			print('Modules to be installed: ')
			for x in requirements:
				print('%s'%x)
			confirm = ''
			while confirm.lower() != 'yes' and confirm.lower() != 'no':
				if confirm.lower() == 'y' or confirm.lower() == 'n':
					confirm = input('Please type "yes" or "no" to confirm. Is this ok? (yes/no): ')
				else:
					confirm = input('Is this ok? (yes/no): ')

			if confirm.lower() == 'no':
				return

			for x in requirements:
				install_package(x)

		f.close()
	except Exception as e:
		pass

def install_package(name):
	try:
		print('Installing package: %s'%name)
		# Function pip.main() no longer exists in pip module (as of 10.0.1)
		# Use a subprocess in this case.
		if int(pip.__version__.split('.')[0]) >= 10:
			import subprocess, sys
			subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])
		else:
			pip.main(['install', name])

	except Exception as e:
		print('Error installing %s: %s'%(name, e))
		print('Try installing it manually with `pip install %s`.'%name)

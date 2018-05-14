"""
CLI install controller
"""
from git import Repo
import os, shutil, stat, errno

def install(args):
	CONTRIB_URL = 'https://github.com/AdobeAtAdobe/SimpleSensor_contrib.git'

	if args.name is None:
		print("Error: Must provide a module name" +
			"(ie. `--name module-name`)")
	elif args.type is None:
		print("Error: Must provide a module type" +
		 "(ie. `--type communication` or `--type collection`)")
	elif str(args.type) != "communication" and str(args.type) != "collection":
		print("Error: Invalid module type `%s`."%args.type +
			"Only `collection` and `communication` supported.")
	else:
		if args.source is not None:
			print("Source param set, overriding with source `%s`"%args.source)
			CONTRIB_URL = args.source

		DIR_NAME = args.name
		DIR_PATH = os.path.abspath(os.path.join(__file__,'../../%s_modules/%s'%(args.type, args.name)))

		print('Installing module "%s" to %s'%(DIR_NAME, DIR_PATH))

		if os.path.isdir(DIR_PATH):
			# shutil.rmtree(DIR_NAME)
			print("Directory exists, requirement might already be satisfied." +
				"Try deleting `%s` or updating module manually."%DIR_PATH)
			exit()

		os.mkdir(DIR_PATH)

		# Make a repo pointing to the contrib modules, checkout the module name and pull it
		repo = Repo.init(DIR_PATH)
		origin = repo.create_remote('origin', CONTRIB_URL)
		assert origin.exists()
		origin.fetch()
		checkout_branch(repo, origin, args.name)
		origin.pull()

		# Move module dir to correct folder
		camel_name = to_camel_case(args.name)
		shutil.move(
			os.path.join(DIR_PATH, '%s_modules'%args.type, camel_name),
			os.path.abspath(os.path.join(DIR_PATH, '../'))
			)

		# Delete the repo
		try:
			shutil.rmtree(DIR_PATH, ignore_errors=False, onerror=remove_readonly)
		except Exception as e:
			print("Error: Unable to delete temporary module path `%s`. Try deleting it manually."%DIR_PATH)

		# Configure module

def checkout_branch(repo, origin, branch_name):
	try:
		repo.create_head(branch_name, origin.refs[branch_name])
		repo.heads[branch_name].set_tracking_branch(origin.refs[branch_name])
		repo.heads[branch_name].checkout()
	except Exception as e:
		print("Error: %s"%e)

def to_camel_case(hyphenated):
	""" Convert hyphen broken string to camel case. """
	components = hyphenated.split('-')
	return components[0] + ''.join(x.title() for x in components[1:])

def remove_readonly(func, path, exc):
	""" Clear the readonly bit and reattempt the removal """
	excvalue = exc[1]
	if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
		os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
		func(path)
	else:
		raise
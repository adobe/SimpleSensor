cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"modules/uEyeCollectionPoint")))
 if cmd_subfolder not in sys.path:
     sys.path.insert(0, cmd_subfolder)
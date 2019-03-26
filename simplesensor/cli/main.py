"""
CLI main entry point
"""

from .install import install
from .config import config
import argparse

def get_parser():
    parser = argparse.ArgumentParser(description='SimpleSensor CLI')
    subparsers = parser.add_subparsers(help='commands', dest='command')

    start_parser = subparsers.add_parser('start', help='Start SimpleSensor')
    start_parser.set_defaults(func=cli_start)

    install_parser = subparsers.add_parser('install', help='Install extra modules')
    install_parser.set_defaults(func=install)
    install_parser.add_argument('--source', action='store')
    install_parser.add_argument('--name', action='store')
    install_parser.add_argument('--type', action='store')

    help_parser = subparsers.add_parser('help', help='Show help')

    config_parser = subparsers.add_parser('config', help='Configure an installed module')
    config_parser.set_defaults(func=config)
    config_parser.add_argument('--name', action='store')
    config_parser.add_argument('--type', action='store')

    version_parser = subparsers.add_parser('version', help='Show running version number')
    version_parser.set_defaults(func=cli_version)

    return parser

def cli_start(args):
    from .start import start
    start(args)

def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.command == 'help':
        parser.print_help()
    elif args.command == "install" :
        args.func(args)
    elif args.command == 'start':
        args.func(args)
    elif args.command == 'config':
        args.func(args)
    elif args.command == 'version':
        args.func(args)
    else:
        parser.print_help()

def cli_version(args):
    from simplesensor import version
    print('%s'%(version.__version__))
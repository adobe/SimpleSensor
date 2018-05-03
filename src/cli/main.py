"""
CLI Main

"""
from .install import install
from .start import start
import argparse

def get_parser():
    parser = argparse.ArgumentParser(description='SimpleSensor CLI')
    subparsers = parser.add_subparsers(help='Sub-commands')

    start_parser = subparsers.add_parser('start', help='Start SimpleSensor')
    start_parser.set_defaults(func=start)
    start_parser.add_argument('-f', action='store')

    install_parser = subparsers.add_parser('install', help='Install extra modules')
    install_parser.set_defaults(func=install)
    install_parser.add_argument('--src', action='store')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    print("SimpleSensor CLI doesn't do anything yet :(")
    print('args: ', args)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
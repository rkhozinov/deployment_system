import argparse
import os
import logging

from deployment_system.topology import Topology


parser = argparse.ArgumentParser(description="Program for deployment some topology for test needing")
parser.print_help()
parser.add_argument_group()
parser.add_argument('action', help='Topology action (e.g. create, destroy)')
parser.add_argument('rpname', help='Resource pool name')
parser.add_argument('config', help='Topology configuration path')
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

if args.action == 'create':
    print ('Begin creation process...{newline}'
           '{tab}Resource pool: {rpname}{newline}'
           '{tab}Configuration: {config}'
           .format(rpname=args.rpname, newline=os.linesep, config=args.config, tab='\t'))
    try:
        Topology(config_path=args.config, resource_pool=args.rpname).create()
    except Exception as e:
        logger.error(e.message)
        print e.message

elif args.action == 'destroy':
    print ('Begin destroying process...{newline}'
           '{tab}Resource pool: {rpname}{newline}'
           '{tab}Configuration: {config}'
           .format(rpname=args.rpname, newline=os.linesep, config=args.config, tab='\t'))
    try:
        # todo: add option group for destroy with vms
        Topology(config_path=args.config, resource_pool=args.rpname).destroy()
    except Exception as e:
        logger.error(e.message)
        print e.message

else:
    parser.print_help()
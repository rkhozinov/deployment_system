import argparse
import os

parser = argparse.ArgumentParser(description="Program for deployment some topology for test needing")
parser.print_help()
parser.add_argument('action', help='Topology action (e.g. create, destroy)')
parser.add_argument('rpname', help='Resource pool name')
parser.add_argument('config', help='Topology configuration path')

args = parser.parse_args()

# topology = Topology(config_path=args.config, resource_pool=args.rpname)

if args.action == 'create':
    print ('Begin creation process...{newline}'
           '{tab}Resource pool: {rpname}{newline}'
           '{tab}Configuration: {config}'
           .format(rpname=args.rpname, newline=os.linesep, config=args.config, tab='\t'))
elif args.action == 'destroy':
    print ('Begin destroying process...{newline}'
           '{tab}Resource pool: {rpname}{newline}'
           '{tab}Configuration: {config}'
           .format(rpname=args.rpname, newline=os.linesep, config=args.config, tab='\t'))
else:
    parser.print_help()
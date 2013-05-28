import argparse
import os
import logging
import datetime
import cProfile

from deployment_system.topology import Topology


parser = argparse.ArgumentParser(description="Program for deployment some topology for test needing")
parser.add_argument('action', help='Topology action (e.g. create, destroy)')
parser.add_argument('rpname', help='Resource pool name')
parser.add_argument('config', help='Topology configuration path')

args = parser.parse_args()
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='\t%(module)-16s: %(message)-4s')

LOG_FILENAME = '../log/%s_%s_%s.log' % (datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), args.rpname, args.action)
PROFILE_FILE_NAME = '%s.%s' % (LOG_FILENAME.split('.log')[0], 'out')

log_file = logging.FileHandler(filename=LOG_FILENAME, mode='w')
log_file.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log_file.setFormatter(formatter)

logger.addHandler(log_file)

profiler = cProfile.Profile()

if not os.path.exists(args.config):
    logger.error("Configuration with '{path}' is not exist".format(path=args.config))
    exit(1)

if args.action == 'create':
    print ('Begin creating process (%s):' % datetime.datetime.now())
    try:
        profiler.enable()
        Topology(config_path=args.config, resource_pool=args.rpname).create()
        profiler.disable()
        profiler.dump_stats(PROFILE_FILE_NAME)
        profiler.print_stats(sort='time')
    except Exception as e:
        logger.error(e.message)
    finally:
        print('End of creating process (%s).' % datetime.datetime.now())

elif args.action == 'destroy':
    print ('Begin destroying process (%s):' % datetime.datetime.now())
    try:
        profiler.enable()
        Topology(config_path=args.config, resource_pool=args.rpname).destroy(destroy_virtual_machines=True,
                                                                             destroy_networks=True)
        profiler.disable()
        profiler.dump_stats(PROFILE_FILE_NAME)
        profiler.print_stats(sort='time')
    except Exception as e:
        logger.error(e.message)
    finally:
        print('End of destroying process (%s).' % datetime.datetime.now())
else:
    parser.print_help()


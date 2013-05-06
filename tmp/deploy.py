"""
Script for deployment some settings for test needing
"""
import ConfigParser

import logging


MEMORY = 'memory'
CPU = 'cpu'
DISK_SPACE = 'disk_space'
DESCR = 'description'
CONFIG = 'configuration'

log = logging.getLogger("deployment")
logging.basicConfig()
log.setLevel(logging.INFO)

config = ConfigParser.RawConfigParser()
config.read("topology.ini")

def get_list(str):
    return str.replace(' ', '').split(',')

hostname = config.get('settings', 'esx_hostname')
log.info(hostname)
iso_path = config.get('settings', 'iso_path')
log.info(iso_path)
networks = get_list(config.get('settings', 'networks'))
log.info(networks)
hosts = get_list(config.get('settings', 'hosts'))
log.info(hosts)

stack_name = "lab1"

for net in networks:
    switch_name = 'sw_' + stack_name + '_' + net
    num_ports = config.getint(net, 'num_ports')
    promiscuous = config.getboolean(net, 'promiscuous')
    vlan = config.get(net, 'vlan')
    try:
        vlan = int(vlan)
    except ValueError:
        vlan = 4095

for host in hosts:
    vm_networks = get_list(config.get(host, 'networks'))

    for i in range(len(vm_networks)):
        vm_networks[i] = ('sw_%s_%tests') % (stack_name, vm_networks[i])

    vm_description = config.get(host, DESCR)
    log.info(vm_description)

    vm_memorysize = config.getint(host, MEMORY)
    log.info(vm_memorysize)
    vm_cpucount = config.getint(host, CPU)
    log.info(vm_cpucount)
    vm_disksize = config.getint(host, DISK_SPACE)
    log.info(vm_disksize)
    vm_configuration = config.get(host, CONFIG)
    log.info(vm_configuration)

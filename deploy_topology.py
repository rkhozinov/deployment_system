from optparse import OptionParser
import ConfigParser
import json

import lib.pyshpere2 as vm_manager


parser = OptionParser()
parser.add_option("-c", "--create", dest="operation", help="Create topology")
parser.add_option("-d", "--destroy", dest="operation", help="Destroy topology")
parser.add_option("-n", "--name", dest="stack_name", help="Resource pool name")
parser.add_option("-t", "--topology", dest="topology", help="INI file with topology configuration")
parser.add_option("-u", "--user", dest="user", help="ESX server user")
parser.add_option("-p", "--password", dest="password", help="ESX server password")
parser.add_option("-a", "--address", dest="address", help="ESX server address")

(options, args) = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read(options.topology)

hostname = config.get('topology', 'esx_hostname')
iso_path = config.get('topology', 'iso_path')
networks = json.loads(config.get('topology', 'networks'))
hosts = json.loads(config.get('topology', 'hosts'))

manager = vm_manager.Creator(options.address, options.user, options.password)


def create():
    try:
        manager.create_resource_pool(options.stack_name, esx_hostname=hostname)
    except vm_manager.CreatorException:
        pass

    for net in networks:
        sw_name = 'sw_' + options.stack_name + '_' + net
        num_ports = config.getint(net, 'num_ports')
        promiscuous = config.getboolean(net, 'promiscious')
        vlan = config.get(net, 'vlan')
        try:
            vlan = int(vlan)
        except ValueError:
            vlan = 4095

        manager.create_virtual_switch(sw_name, num_ports, hostname)
        manager.add_port_group(sw_name, sw_name,
                               esx_hostname=hostname, vlan_id=vlan,
                               promiscuous=promiscuous)

    for host in hosts:
        vm_networks = json.loads(config.get(host, 'networks'))
        for i in range(len(vm_networks)):
            vm_networks[i] = 'sw_' + options.stack_name + '_' + vm_networks[i]
        vm_description = config.get(host, 'description')
        vm_memorysize = config.getint(host, 'memorysize')
        vm_cpucount = config.getint(host, 'cpucount')
        vm_disksize = config.getint(host, 'disksize')
        vm_configuration = config.get(host, 'configuration')

        name = options.stack_name + '_' + host
        manager.create_vm(name, hostname, iso_path, \
                          resource_pool='/' + options.stack_name, \
                          networks=vm_networks, \
                          annotation=vm_description, \
                          memorysize=vm_memorysize, \
                          cpucount=vm_cpucount, \
                          disksize=vm_disksize)


def destroy():
    manager.destroy_resource_pool_with_vms(options.stack_name, hostname)
    sw_name = 'sw_' + options.stack_name
    manager.destroy_virtual_switch(sw_name, hostname)


if 'create' in options.operation:
    create()
elif 'destroy' in options.operation:
    destroy()

"""
Script for deployment some topology for test needing
"""
from optparse import OptionParser
import ConfigParser

import json
import logging

import lib.pyshpere2 as vm_manager


parser = OptionParser()
parser.add_option("-c", "--create", dest="operation", help="Create topology")
parser.add_option("-d", "--destroy", dest="operation", help="Destroy topology")
parser.add_option("-n", "--name", dest="stack_name", help="Resource pool name")
parser.add_option("-t", "--topology", dest="topology", help="INI file with topology configuration")
parser.add_option("-u", "--user", dest="user", help="ESX server user")
parser.add_option("-p", "--password", dest="password", help="ESX server password")
parser.add_option("-a", "--address", dest="address",
                  help="ESX server address")

(options, args) = parser.parse_args()


class Topology:
    """
    Create a topology from ini file

    """
    manager = None
    log = logging.getLogger(__name__)
    config = ConfigParser.RawConfigParser()

    SETTINGS = 'settings'

    SWITCH_NAME_PREFIX = 'sw'

    # common settings
    ESX_HOST = 'host'
    ESX_NAME = 'name'
    ISO = 'iso_path'
    NETWORKS = 'networks'
    VMS = 'vms'

    VM_MEM = 'memory'
    VM_CPU = 'cpu'
    VM_SIZE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'

    def __init__(self, config_path):
        logging.basicConfig()

        try:
            self.config.read(config_path)
        except ConfigParser.Error as error:
            self.log.critical("Cannot read configuration: " + config_path, error.message)
        # hostname = config.get('topology', 'esx_hostname')
        # iso_path = config.get('topology', 'iso_path')
        # networks = json.loads(config.get('topology', 'networks'))
        # hosts = json.loads(config.get('topology', 'hosts'))

        try:
            self.host = self.config.get(self.SETTINGS, self.ESX_HOST)
            self.name = self.config.get(self.SETTINGS, self.ESX_NAME)
            self.networks = self.str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))

        except ConfigParser.Error as error:
            raise error

        self.manager = vm_manager.Creator(options.address, options.user, options.password)

    def __str_to_list(str):
        """
        Converts string to list without whitespaces

        :param str: some string for converting to list
        :return: list of string values
        """
        return str.replace(' ', '').split(',')


    def create(self):
        try:
            vm_manager.create_resource_pool(name=options.stack_name,
                                            esx_hostname=hostname)
        except vm_manager.CreatorException as e:
            log.warning(e.message)
            pass

        for net in networks:
            switch_name = 'sw_' + options.stack_name + '_' + net
            num_ports = config.getint(net, 'num_ports')
            promiscuous = config.getboolean(net, 'promiscious')
            vlan = config.get(net, 'vlan')
            try:
                vlan = int(vlan)
            except ValueError:
                vlan = 4095

            manager.create_virtual_switch(switch_name, num_ports, hostname)
            manager.add_port_group(vswitch=switch_name,
                                   name=switch_name,
                                   esx_hostname=hostname,
                                   vlan_id=vlan,
                                   promiscuous=promiscuous)

        for host in hosts:
            vm_networks = json.loads(config.get(host, 'networks'))
            for i in range(len(vm_networks)):
                vm_networks[i] = ('sw_%s_%s') % (options.stack_name, vm_networks[i])
            vm_description = config.get(host, 'description')
            vm_memorysize = config.getint(host, 'memorysize')
            vm_cpucount = config.getint(host, 'cpucount')
            vm_disksize = config.getint(host, 'disksize')
            vm_configuration = config.get(host, 'configuration')

            name = options.stack_name + '_' + host
            manager.create_vm(name, hostname, iso_path,
                              resource_pool='/' + options.stack_name,
                              networks=vm_networks,
                              annotation=vm_description,
                              memorysize=vm_memorysize,
                              cpucount=vm_cpucount,
                              disksize=vm_disksize)

            ### TODO: add code with manual reconfiguration of the VM
            ### need to add part with VNC port configuration.
            ### add VNC port parameter to topology file for each VM

            ### TODO: run VM and perform configuration via VNC port.
            ### we should use topology VM part 'configuration'


    def destroy(self):
        """
        Destroy topology by stack_name
        """

        self.manager.destroy_resource_pool_with_vms(options.stack_name, self.hostname)
        sw_name = 'sw_' + options.stack_name
        self.manager.destroy_virtual_switch(sw_name, self.hostname)


    if 'create' in options.operation:
        create()
    elif 'destroy' in options.operation:
    destroy()

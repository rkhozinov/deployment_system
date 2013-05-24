"""
Script for deployment some topology for test needing
"""
from optparse import OptionParser
import ConfigParser

import logging

import lib.hatchery as vm_manager
from lib.console import run_vnc_command as vnc_cmd
from lib.console import get_telnet as telnet
from lib.hatchery import CreatorException


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

    # common settings
    SETTINGS = 'settings'
    SW_PREFIX = 'sw_'
    ESX_HOST = 'host'
    ESX_USER = 'host'
    ESX_PASSWORD = 'host'


    STACK_NAME = 'name'
    ISO_IMAGE = 'iso_path'
    NETWORKS = 'networks'
    VMS = 'vms'

    VM_MEM = 'memory'
    VM_CPU = 'cpu'
    VM_SIZE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'
    VM_VNC_PORT = 'vnc_port'
    VM_LOGIN = 'user'
    VM_PASSWORD = 'password'

    NET_PORTS = 'num_ports'
    NET_PROMISCUOUS = 'promiscuous'

    def __init__(self, config_path):
        """

        :param config_path: topology configuration file
        """
        self.log = logging.getLogger(__name__)
        logging.basicConfig()

        try:
            self.config = ConfigParser.RawConfigParser()
            self.config.read(config_path)
        except ConfigParser.Error as error:
            self.log.critical("Cannot read a configuration: " + config_path, error.message)
            # hostname = config.get('topology', 'esx_hostname')
        # iso_path = config.get('topology', 'iso_path')
        # networks = json.loads(config.get('topology', 'networks'))
        # hosts = json.loads(config.get('topology', 'hosts'))

        try:
            self.esx_host = self.config.get(self.SETTINGS, self.ESX_HOST)

            self.iso = self.config.get(self.SETTINGS, self.ISO_IMAGE)
            self.stack_name = self.config.get(self.SETTINGS, self.STACK_NAME)
            self.networks = self.__str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))
        except ConfigParser.Error as error:
            self.log.critical("Cannot read a option.", error.message)
            raise error

        if options.address == '':
            options.address = self.config.get(self.SETTINGS, self.ESX_HOST)
        if options.user == '':
            options.address = self.config.get(self.SETTINGS, self.ESX_USER)
        if options.user == '':
            options.address = self.config.get(self.SETTINGS, self.ESX_PASSWORD)
        try:
            self.manager = vm_manager.Creator(options.address, options.user, options.password)
        except CreatorException as error:
            self.log.critical(error.message)
            raise error

    def __str_to_list(self, string):
        """
        Converts string to list without whitespaces

        :param string: some string for converting to list
        :return: list of string values
        """
        return string.replace(' ', '').split(',')


    def __create_networks(self):
        """
        Creates virtual switch with some ports and networks

        :raise: CreatorException, ConfigParser.Error
        """
        for net in self.networks:

            # read config
            num_ports, promiscuous, vlan = None
            try:
                num_ports = self.config.getint(net, self.NET_PORTS)
                promiscuous = self.config.getboolean(net, self.NET_PROMISCUOUS)
                vlan = self.config.get(net, 'vlan')
            except ConfigParser.ParsingError as error:
                self.log.debug("Cannot parse option.", error.message)
                raise error
            except ConfigParser.NoOptionError as error:
                self.log.debug("Cannot find option.", error.message)
                raise error
            except ConfigParser.Error as error:
                self.log.debug("Error in the config file.", error.message)
                raise error

            try:
                vlan = int(vlan)
            except ValueError:
                vlan = 4095

            # create switch
            switch_name = None
            try:
                switch_name = self.SW_PREFIX + self.stack_name + '_' + net
                self.manager.create_virtual_switch(switch_name, num_ports, self.esx_host)
                self.log.info("ESXi virtual switch '%tests' was created " % switch_name)
            except CreatorException as error:
                self.log.debug("Cannot create the virtual switch with name " + switch_name, error.message)
                raise error

            # add ports to the created switch
            try:
                self.manager.add_port_group(switch_name=switch_name,
                                            vlan_name=switch_name,
                                            esx_hostname=self.esx_host,
                                            vlan_id=vlan,
                                            promiscuous=promiscuous)
                self.log.info("%tests ports were added to ESXi virtual switch '%tests' successfully" % num_ports, switch_name)
            except CreatorException as error:
                self.log.debug("Cannot add ports to the virtual switch.", error.message)
                raise error

    def __create_vms(self):

        """
         Creates virtual machines

        :type self: Topology object
        :raise: ConfigParser.ParsingError, ConfigParser.NoOptionError, ConfigParser.Error
        """

        for vm in self.vms:
            # get config
            try:
                vm_name = self.stack_name + '_' + vm
                vm_description = self.config.get(vm, self.VM_DESCR)
                vm_mem = self.config.get(vm, self.VM_MEM)
                vm_cpu = self.config.get(vm, self.VM_CPU)
                vm_size = self.config.get(vm, self.VM_SIZE)
                vm_config = self.config.get(vm, self.VM_CONFIG)
                vm_networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
                vm_vnc_port = self.config.getint(vm, self.VM_VNC_PORT)
                vm_login = self.config.get(vm, self.VM_LOGIN)
                vm_password = self.config.get(vm, self.VM_PASSWORD)
            except ConfigParser.ParsingError as error:
                self.log.debug("Cannot parse option.", error.message)
                raise error
            except ConfigParser.NoOptionError as error:
                self.log.debug("Cannot find option.", error.message)
                raise error
            except ConfigParser.Error as error:
                self.log.debug("Error in the config file.", error.message)
                raise error

            # rename networks
            for i in range(len(vm_networks)):
                vm_networks[i] = ('%tests%s_%tests') % (self.SW_PREFIX, self.stack_name, vm_networks[i])

            # get a iso image for the vm
            vm_iso = None
            try:
                vm_iso = self.config.get(vm, self.VM_NETWORKS)
                self.log.info("For vm '%tests' using specific iso image '%tests'" % vm, vm_iso)
            except ConfigParser.Error:
                self.log.debug("For vm '%tests' using default iso image '%tests'" % vm, vm_iso)
                # get a common iso
                vm_iso = self.iso

            try:
                self.manager.create_vm(vm_name, self.esx_host, vm_iso,
                                       resource_pool='/' + self.stack_name,
                                       networks=vm_networks,
                                       annotation=vm_description,
                                       memorysize=vm_mem,
                                       cpucount=vm_cpu,
                                       disksize=vm_size)
            except CreatorException as error:
                raise error

                ### TODO: add code with manual reconfiguration of the VM
                ### need to add part with VNC port configuration.
                ### add VNC port parameter to topology file for each VM
                # Start to work with VM using the VNC console.
                # After the base configuration for net interfaces and
                # telnet daemon switch to the telnet console

            # FIXME: change esx to vm credentials
            # TODO: need to add vm credentials to ini-file
            vnc_cmd(self.esx_host, vm_vnc_port, vm_login)
            vnc_cmd(self.esx_host, vm_vnc_port, vm_password)
            for option in vm_config:
                vnc_cmd(self.esx_host, vm_vnc_port, option)

            # Start to work with telnet console
            session = None
            while session is None:
                session = telnet(vm_ip_address, vm_login, vm_password)
            conf_cmds = config.get(vm_name, 'telnet_commands').split('\n')
            LOG.info(str(conf_cmds))
            session.write('conf\n')
            session.read_until('#', timeout=5)
            for cmd in conf_cmds:
                session.write('%tests\n' % cmd)
                LOG.info("Telnet cmd: %tests" % cmd)
                session.read_until('#', timeout=5)
            session.write('commit\n')
            session.read_until('#', timeout=5)
            session.write('save\n')
            session.read_until('#', timeout=5)
            session.close()

    def create(self):
        try:
            # creates a resource pool for storing virtual machines
            self.manager.create_resource_pool(name=self.stack_name, esx_hostname=self.esx_host)
            # creates a virtual switch and networks
            self.__create_networks()
            # creates and configure virtual machines
            self.__create_vms()
        except CreatorException as creator_error:
            self.log.critical(creator_error.message)
            raise creator_error
        except ConfigParser.Error as config_error:
            self.log.critical("Error in the config file.", config_error.message)
            raise config_error


    def destroy(self):
        """
        Destroy topology by stack_name
        """
        self.manager.destroy_resource_pool_with_vms(options.stack_name, self.esx_host)
        sw_name = self.SW_PREFIX + options.stack_name
        self.manager.destroy_virtual_switch(sw_name, self.esx_host)


if 'create' in options.operation:
    create()
elif 'destroy' in options.operation:
    destroy()

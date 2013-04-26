import logging
import ConfigParser
from test import VirtualMachine


class TopologyReader(object):
    SETTINGS = 'settings'
    SWITCH_NAME_PREFIX = 'sw'

    # common settings
    ESX_HOST = 'esx_host'
    ESX_LOGIN = 'esx_login'
    ESX_PASSWORD = 'esx_password'

    ISO = 'iso'
    NETWORKS = 'networks'
    VMS = 'vms'

    VM_MEM = 'memory'
    VM_CPU = 'cpu'
    VM_SIZE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'
    VM_ISO = 'iso'
    VM_NEIGHBOURS = 'neighbours'
    VM_LOGIN = 'login'
    VM_PASSWORD = 'password'

    def __init__(self, config_path):

        self.log = logging.getLogger(__name__)
        logging.basicConfig()

        # init config
        try:
            self.config = ConfigParser.RawConfigParser()
            self.config.read(config_path)
        except ConfigParser.Error as error:
            self.log.critical(error.message)

        # read config
        try:
            self.esx_host = self.config.get(self.SETTINGS, self.ESX_HOST)
            self.esx_login = self.config.get(self.SETTINGS, self.ESX_LOGIN)
            self.esx_password = self.config.get(self.SETTINGS, self.ESX_PASSWORD)
            self.iso = self.config.get(self.SETTINGS, self.ISO)
            self.networks = self.__str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))
        except ConfigParser.Error as error:
            self.log.critical(error.message)
            raise error

    def __str_to_list(self, str):
        """
        Converts string to list without whitespaces

        :param str: some string for converting to list
        :return: list of string values
        """
        return str.replace(' ', '').split(',')

    def __read_vm(self, vm_name):
        for vm in self.vms:
            try:
                vm_description = self.config.get(vm, self.VM_DESCR)
                vm_mem = self.config.get(vm, self.VM_MEM)
                vm_cpu = self.config.get(vm, self.VM_CPU)
                vm_size = self.config.get(vm, self.VM_SIZE)
                vm_config = self.config.get(vm, self.VM_CONFIG)
                vm_networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
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
            try:

                return VirtualMachine(name, networks, iso, memory, cpu, size, description)
            except Exception as error:
                self.log.critical(error.message)
                raise error

    class Network(object):
        def __init__(self, ports, vlan=4095, promiscuous=False):
            """
            Create network with specific vlan and mode

            """
            self.ports = ports
            self.vlan = vlan
            self.promiscuous = promiscuous





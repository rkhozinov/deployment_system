import logging
import ConfigParser
from test.Network import Network
from test.VirtualMachine import VirtualMachine


class TopologyReader(object):
    SETTINGS = 'settings'
    SWITCH_PREFIX = 'sw'

    # common settings
    ESX_HOST = 'esx_host'
    ESX_LOGIN = 'esx_login'
    ESX_PASSWORD = 'esx_password'

    ISO = 'iso'
    NETWORKS = 'networks'
    VMS = 'vms'

    NET_VLAN = 'vlan'
    NET_PORTS = 'ports'
    NET_PROMISCUOUS = 'promiscuous'
    NET_ISOLATED = 'isolated'

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
    VM_NEIGHBOURS = 'neighbours'

    def __init__(self, config_path):

        self.log = logging.getLogger(__name__)
        logging.basicConfig()

        # init config
        try:
            self.config = ConfigParser.RawConfigParser()
            self.config.read(config_path)
        except ConfigParser.Error as error:
            self.log.critical(error.message)

        # read main config
        try:
            self.esx_host = self.config.get(self.SETTINGS, self.ESX_HOST)
            self.esx_login = self.config.get(self.SETTINGS, self.ESX_LOGIN)
            self.esx_password = self.config.get(self.SETTINGS, self.ESX_PASSWORD)
            self.iso = self.config.get(self.SETTINGS, self.ISO)
            # list of networks
            self.networks = self.__str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            # list of virtual machines
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))
        except ConfigParser.Error as error:
            self.log.critical(error.message)
            raise error

    def __str_to_list(self, string):
        """
        Converts string to list without whitespaces

        :param string: some string for converting to list
        :return: list of string values
        """
        return string.replace(' ', '').split(',')

    def __get_vm(self, vm):

        # Required params
        try:
            password = self.config.get(vm, self.VM_PASSWORD)
            login = self.config.get(vm, self.VM_LOGIN)
        except ConfigParser.Error as error:
            raise error

        try:
            description = self.config.get(vm, self.VM_DESCR)
            memory = self.config.get(vm, self.VM_MEM)
            cpu = self.config.get(vm, self.VM_CPU)
            size = self.config.get(vm, self.VM_SIZE)
            config = self.__str_to_list(self.config.get(vm, self.VM_CONFIG))
            connected_networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
            neighbours = self.__str_to_list(self.config.get(vm, self.VM_NEIGHBOURS))
            iso = self.config.get(vm, self.VM_ISO)

            # if not specific a iso-image for this vm then will be used the common iso-image
            if not iso:
                iso = self.iso

            return VirtualMachine(name=vm,
                                  description=description,
                                  memory=memory,
                                  cpu=cpu,
                                  size=size,
                                  configuration=config,
                                  connected_networks=connected_networks,
                                  login=login,
                                  password=password,
                                  neighbours=neighbours,
                                  iso=iso)

        except ConfigParser.NoSectionError as no_section:
            raise no_section
        except ConfigParser.ParsingError as parsing_error:
            raise parsing_error

    def __get_network(self, net):
        """
        Gets a network by name
        :param net: name of the network
        :return: Network
        :raise:  ConfigParser.ParsingError, ConfigParser.NoOptionError
        :rtype: Network
        """
        try:
            vlan = self.config.get(net, self.NET_VLAN)
        except ConfigParser.Error as error:
            raise error
        try:
            promiscuous = self.config.getboolean(net, self.NET_PROMISCUOUS)
            isolated = self.config.getboolean(net, self.NET_ISOLATED)
        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.ParsingError as error:
            raise error
        return Network(name=net, vlan=vlan, promiscuous=promiscuous, isolated=isolated)

    def get_virtual_machines(self):
        try:
            vm_lst = []
            for vm in self.vms:
                vm_lst.append(self.__get_vm(vm))
            return vm_lst
        except ConfigParser.NoSectionError as no_section:
            raise no_section
        except ConfigParser.ParsingError as parsing_error:
            raise parsing_error
        except ConfigParser.Error as error:
            raise error

    def get_networks(self):
        """


        :return: list of networks
        :raise: ConfigParser.Error, ConfigParser.NoSectionError, ConfigParser.ParsingError
        """
        try:
            networks = []
            for net in self.networks:
                networks.append(self.__get_network(net))
            return networks
        except ConfigParser.NoSectionError as no_section:
            raise no_section
        except ConfigParser.ParsingError as parsing_error:
            raise parsing_error
        except ConfigParser.Error as error:
            raise error










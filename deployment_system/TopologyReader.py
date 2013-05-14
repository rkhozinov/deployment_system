import logging
import ConfigParser
from deployment_system.Network import Network
from deployment_system.VirtualMachine import VirtualMachine


class TopologyReader(object):

    # sections describe
    ESX_MANAGER = 'esx_manager'
    ESX_HOST = 'esx_host_address'
    SETTINGS = 'settings'

    # esx manager settings
    MANAGER_ADDRESS = 'address'
    MANAGER_USER = 'user'
    MANAGER_PASSWORD = 'password'

    SWITCH_PREFIX = 'sw'

    # esx host settings
    ESX_HOST_NAME = 'name'
    ESX_HOST_ADDRESS = 'address'
    ESX_HOST_USER = 'user'
    ESX_HOST_PASSWORD = 'password'

    # common settings
    ISO = 'iso'
    NETWORKS = 'networks'
    VMS = 'vms'

    # network settings
    NET_VLAN = 'vlan'
    NET_PORTS = 'ports'
    NET_PROMISCUOUS = 'promiscuous'
    NET_ISOLATED = 'isolated'

    # virtual machine settings
    VM_MEM = 'memory'
    VM_CPU = 'cpu'
    VM_SIZE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'
    VM_ISO = 'iso'
    VM_NEIGHBOURS = 'neighbours'
    VM_USER = 'user'
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
            # self.logger.critical(error.message)
            raise error


        # read main config
        try:
            # esx manager settings
            self.manager_address = self.config.get(self.ESX_MANAGER, self.MANAGER_ADDRESS)
            self.manager_user = self.config.get(self.ESX_MANAGER, self.MANAGER_USER)
            self.manager_password = self.config.get(self.ESX_MANAGER, self.MANAGER_PASSWORD)

            # esx host settings
            # esx_host_address need for virtual machine configuration
            self.esx_host_address = self.config.get(self.ESX_HOST, self.ESX_HOST_ADDRESS)
            self.esx_host_name = self.config.get(self.ESX_HOST, self.ESX_HOST_NAME)
            self.esx_user = self.config.get(self.ESX_HOST, self.ESX_HOST_USER)
            self.esx_password = self.config.get(self.ESX_HOST, self.ESX_HOST_PASSWORD)

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


    def __str_to_list_strip(self, string):
        return [str.strip(x) for x in string.split(',')]


    def __get_vm(self, vm):

        # Required params
        try:
            password = self.config.get(vm, self.VM_PASSWORD)
            login = self.config.get(vm, self.VM_USER)
        except ConfigParser.NoOptionError as e:
            raise e
        except ConfigParser.ParsingError as e:
            raise e

        try:
            description = self.config.get(vm, self.VM_DESCR)
        except:
            description = None
        try:
            memory = self.config.get(vm, self.VM_MEM)
        except:
            memory = None
        try:
            cpu = self.config.get(vm, self.VM_CPU)
        except:
            cpu = None
        try:
            size = self.config.get(vm, self.VM_SIZE)
        except:
            size = None
        try:
            config = self.__str_to_list_strip(self.config.get(vm, self.VM_CONFIG))
        except:
            config = None
        try:
            connected_networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
        except:
            connected_networks = None
        try:
            neighbours = self.__str_to_list(self.config.get(vm, self.VM_NEIGHBOURS))
        except:
            neighbours = None

        try:
            iso = self.config.get(vm, self.VM_ISO)
        except:
            iso = None

        # if not specific a iso-image for this vm then will be used the common iso-image
        if not iso:
            iso = self.iso

        return VirtualMachine(name=vm,
                              login=login,
                              password=password,
                              memory=memory,
                              cpu=cpu,
                              size=size,
                              connected_networks=connected_networks,
                              iso=iso,
                              description=description,
                              neighbours=neighbours,
                              configuration=config)


    def __get_network(self, net):
        """
        Gets a network by name
        :param net: name of the network
        :return: Network
        :raise:  ConfigParser.ParsingError, ConfigParser.NoOptionError
        :rtype: Network
        """
        vlan = None
        try:
            vlan = self.config.get(net, self.NET_VLAN)
        except ConfigParser.Error as error:
            raise error

        promiscuous = None
        isolated = None
        ports = None
        try:
            promiscuous = self.config.getboolean(net, self.NET_PROMISCUOUS)
            isolated = self.config.getboolean(net, self.NET_ISOLATED)
            ports = self.config.getint(net, self.NET_PORTS)
        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.ParsingError as error:
            raise error

        return Network(name=net, vlan=vlan, ports=ports, promiscuous=promiscuous, isolated=isolated)


    def get_virtual_machines(self):
        """
        Gets the virtual machines list from the configuration file
        :return:  list of virtual machines
        :raise: ConfigParser.NoSectionError, ConfigParser.Error, ConfigParser.ParsingError
        """
        try:
            vm_lst = []
            for vm in self.vms:
                vm_lst.append(self.__get_vm(vm))
            return vm_lst
        except ConfigParser.ParsingError as error:
            raise error
        except ConfigParser.NoSectionError as error:
            raise error


    def get_networks(self):
        """
        Gets networks from the configuration file
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










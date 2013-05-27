import logging
import ConfigParser
from deployment_system.network import Network
from deployment_system.virtual_machine import VirtualMachine


class TopologyReader(object):
    DEFAULT_PORTS_COUNT = 120

    # describe of sections
    MANAGER = 'esx_vcenter'
    HOST = 'esx'
    SETTINGS = 'settings'

    # esx manager settings
    MANAGER_ADDRESS = 'address'
    MANAGER_USER = 'user'
    MANAGER_PASSWORD = 'password'

    SWITCH_PREFIX = 'sw'

    # esx host settings
    HOST_NAME = 'name'
    HOST_ADDRESS = 'address'
    HOST_USER = 'user'
    HOST_PASSWORD = 'password'

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
    VM_DISK_SPACE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'
    VM_ISO = 'iso'
    VM_USER = 'user'
    VM_PASSWORD = 'password'
    # VM_NEIGHBOURS = 'neighbours'
    VM_HARD_DISK = 'hard_disk'

    def __init__(self, config_path):
        """
        Reads and parse config with topology
        :param config_path: topology configuration file
        :raise: ConfigParser.Error
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(message)s', datefmt='%m/%d/%Y %H:%M:%S')

        try:
            # init config
            self.config = ConfigParser.RawConfigParser()
            self.config.read(config_path)
            self.logger.info('Configuration {config} was read successfully'.format(config=config_path))


            # esx manager settings
            self.manager_address = self.config.get(self.MANAGER, self.MANAGER_ADDRESS)
            self.manager_user = self.config.get(self.MANAGER, self.MANAGER_USER)
            self.manager_password = self.config.get(self.MANAGER, self.MANAGER_PASSWORD)
            self.logger.info('ESX vCenter credentials was read successfully')

            # esx host settings
            # need for creating esx entities
            self.host_name = self.config.get(self.HOST, self.HOST_NAME)

            # esx address and credentials need for virtual machine configuration
            self.host_address = self.config.get(self.HOST, self.HOST_ADDRESS)
            self.host_user = self.config.get(self.HOST, self.HOST_USER)
            self.host_password = self.config.get(self.HOST, self.HOST_PASSWORD)
            self.logger.info('ESX host credentials was read successfully')

            try:
                self.iso = self.config.get(self.SETTINGS, self.ISO)
            except ConfigParser.NoOptionError:
                self.logger.info("Common iso image not specified")

            self.networks = self.__str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            self.logger.info("Network list was read successfully: {nets}".format(nets=self.networks))
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))
            self.logger.info("VM list was read successfully: {vms}".format(vms=self.networks))
        except ConfigParser.Error as error:
            self.logger.critical(error.message)
            raise error

    def __str_to_list(self, string):
        """
        Converts string to list without whitespaces

        :param string: some string for converting to list
        :return: list of string values
        """
        return string.replace(' ', '').split(',')


    def __str_to_list_strip(self, string):
        """
         Converts string to list. Each string without whitespaces
        :param string: string for convert
        :return: list of strings
        """
        return [str.strip(x) for x in string.split(',')]


    def __get_vm(self, vm):

        """
        Get vm by name from config and parse it data
        :param vm: virtual machine name
        :return: VirtualMachine instance
        :raise:  ConfigParser.NoOptionError, ConfigParser.ParsingError
        """
        try:
            password = self.config.get(vm, self.VM_PASSWORD)
            login = self.config.get(vm, self.VM_USER)
        except Exception as e:
            self.logger.error(e.message)
            raise
        except ConfigParser.ParsingError:
            raise
        except:
            raise

        try:
            description = self.config.get(vm, self.VM_DESCR)
        except:
            description = None
            self.logger.info("Not specified description for '%s'" % vm)
        try:
            memory = self.config.get(vm, self.VM_MEM)
        except:
            self.logger.info("Not specified memory for '%s'" % vm)
            memory = None
        try:
            cpu = self.config.get(vm, self.VM_CPU)
        except:
            self.logger.info("Not specified cpu count for '%s'" % vm)
            cpu = None
        try:
            hard_disk = self.config.get(vm, self.VM_HARD_DISK)
        except:
            self.logger.info("Not specified hard disk for '%s'" % vm)
            hard_disk = None
        try:
            disk_space = self.config.get(vm, self.VM_DISK_SPACE)
        except:
            self.logger.info("Not specified disk space for '%s'" % vm)
            disk_space = None
        try:
            config = self.__str_to_list_strip(self.config.get(vm, self.VM_CONFIG))
        except:
            self.logger.info("Not specified configuration for '%s'" % vm)
            config = None
        try:
            networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
        except:
            self.logger.info("Not specified networks for '%s'" % vm)
            networks = None
            # try:
            #     neighbours = self.__str_to_list(self.config.get(vm, self.VM_NEIGHBOURS))
            # except:
            #     neighbours = None

        try:
            iso = self.config.get(vm, self.VM_ISO)
        except:
            self.logger.info("Not specified iso image for '%s'" % vm)
            iso = None

        # if not specific a iso-image for this vm then will be used the common iso-image
        if not iso and self.iso:
            iso = self.iso
            self.logger.info("Will be used default iso image %s for '%s'" % (self.iso, vm))

        return VirtualMachine(name=vm,
                              user=login,
                              password=password,
                              memory=memory,
                              cpu=cpu,
                              disk_space=disk_space,
                              connected_networks=networks,
                              iso=iso,
                              description=description,
                              configuration=config,
                              hard_disk=hard_disk)


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
            self.logger.error("Couldn't specify VLAN for '%s'" % net)
            raise error

        promiscuous = None
        isolated = None
        ports = None
        try:
            try:
                promiscuous = self.config.getboolean(net, self.NET_PROMISCUOUS)
            except ConfigParser.NoOptionError:
                pass
            try:
                isolated = self.config.getboolean(net, self.NET_ISOLATED)
            except ConfigParser.NoOptionError:
                pass
            try:
                ports = self.config.getint(net, self.NET_PORTS)
            except ConfigParser.NoOptionError:
                ports = self.DEFAULT_PORTS_COUNT

        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.ParsingError as error:
            raise

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
        except ConfigParser.ParsingError:
            raise
        except ConfigParser.NoSectionError:
            raise
        except:
            raise


    def get_networks(self):
        """
        Gets networks from the configuration file
        :return: list of networks
        :raise: ConfigParser.Error
        """
        try:
            networks = []
            for net in self.networks:
                networks.append(self.__get_network(net))
            return networks
        except ConfigParser.Error as error:
            self.logger.error(error.message)
            raise error










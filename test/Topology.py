import ConfigParser
import logging

__author__ = 'Administrator'


class Topology(object):
    SETTINGS = 'settings'

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

    host, networks, vms, vnc_port, name = None

    log = logging.getLogger(__name__)
    config = ConfigParser.RawConfigParser()

    def __init_log(self, level=logging.INFO):
        logging.basicConfig()
        self.log.setLevel(level)


    def __str_to_list(str):
        """
        Converts string to list without whitespaces

        :param str: some string for converting to list
        :return: list of string values
        """
        return str.replace(' ', '').split(',')


    def __get_config_param(section, option):
        """
        Get config option with some checks

        :param section: section in ini-file
        :param option: option in section
        :return: some value from section.option
        """
        try:
            return config.getint(host, option)
        except ConfigParser.NoOptionError as e:
            log.info("Using default value for %s.%s" % (section, option))
            return None


    def __load(self, config_path):
        """
        Load configuration from a ini-file
        :param config_path:
        :raise: ConfigParser.Error
        """
        try:
            self.config.read(config_path)
            self.host = self.config.get(self.SETTINGS, self.ESX_HOST)
            self.name = self.config.get(self.SETTINGS, self.ESX_NAME)
            self.networks = self.str_to_list(self.config.get(self.SETTINGS, self.NETWORKS))
            self.vms = self.__str_to_list(self.config.get(self.SETTINGS, self.VMS))
        except ConfigParser.Error as error:
            raise error

    def __init__(self, config_path):
        self.__load(config_path)


    def create(self):
        self.__create_networks(self)
        self._create_vms(self)


    def __destroy_switch(self):
        manager.destroy_virtual_switch(sw_name, hostname)


    def destroy(self, stack_name):
        """
        Destroy topology by stack_name
        """
        self._destroy_switch()


    def _destroy_resource_pool(self, resource_pool, hostname=None):
        """
        Destroy a resource pool with vms
        :param resource_pool: name of resource which storing vms for the topology
        :param hostname: ESXi host
        """
        if hostname is None:
            hostname = self.name

        manager.destroy_resource_pool_with_vms(resource_pool, hostname)


    def __create_networks(self):
        pass


    def _create_vms(self):
        pass


    def _create_vm(self, name, networks, iso, memory=512, cpu=2, size=1024, description=None):
        vm = None
        try:
            vm = VM(name, networks, iso, memory, cpu, size, description)
        except:

        vms.append


class Network:
    def __init__(self, name, vlan):
        """
        Create network with specific vlan
        :param name: a network name
        :param vlan: a vlan name
        """
        self.name = name
        self.vlan = vlan


class VM:
    def __init__(self, name, networks, iso, memory=512, cpu=2, size=1024, description=None):
        self.name = name
        self.iso = iso
        self.memory = memory
        self.cpu = cpu
        self.size = size * 1024
        self.description = description

import logging
import ConfigParser


class TopologyConfigReader(object):
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

        try:
            self.manager = vm_manager.Creator(options.address, options.user, options.password)
        except CreatorException as error:
            self.log.critical(error.message)
            raise error

    def __str_to_list(self, str):
        """
        Converts string to list without whitespaces

        :param str: some string for converting to list
        :return: list of string values
        """
        return str.replace(' ', '').split(',')

    def __load_vm(self, name, networks, iso, memory=512, cpu=2, size=1024, description=None):
        try:
            return VM(name, networks, iso, memory, cpu, size, description)
        except Exception as error:
            self.log.critical(error.message)
            raise error

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
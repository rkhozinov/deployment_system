import ConfigParser
import logging

__author__ = 'Administrator'


class Topology(object):
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
    VM_ISO = 'iso'

    host, networks, vms, vnc_port, name = None
    vm_list = []
    networks_list = []
    log = logging.getLogger(__name__)
    config = ConfigParser.RawConfigParser()

    def __init_log(self, level=logging.INFO):
        logging.basicConfig()
        self.log.setLevel(level)





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
        sw_name = self.SWITCH_NAME_PREFIX+'_'+self.name
        manager.destroy_virtual_switch(sw_name, hostname)


    def destroy(self, stack_name):
        """
        Destroy topology by stack_name
        """
        self._destroy_switch(self)
        self.__destroy_resource_pool()


    def __destroy_resource_pool(self, resource_pool, hostname=None):
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


    def __create_vms(self):

        for vm in self.vms:

            try:
                vm_networks = self.__str_to_list(self.__config.get(vm, self.VM_NETWORKS))

                for i in range(len(vm_networks)):
                    vm_networks[i] = ('%s_%s_%s') % (self.SWITCH_NAME_PREFIX, self.name, vm_networks[i])

                vm_description = self.config.get(vm, self.VM_DESCR)

                # VM_MEM, VM_SIZE, VM_CPU, VM_CONFIG - non-default parameter
                vm_mem = self.get_config_param(vm, self.VM_MEM)
                vm_cpu = self.get_config_param(vm, self.VM_CPU)
                vm_disk_space = self.get_config_param(vm, self.VM_SIZE)

                vm_config = self.config.get(vm, self.VM_CONFIG)
                vm_iso = self.config.get(vm, self.VM_ISO)
                vm_name = self.name + '_' + vm

                manager.create_vm(vm_name, self.name, self.iso,
                                      resource_pool='/' + options.stack_name,
                                      networks=vm_networks,
                                      annotation=vm_description,
                                      memorysize=vm_memorysize,
                                      cpucount=vm_cpucount,
                                      disksize=vm_disksize)
            except ConfigParser.Error as error:
                self.log.critical("Cannot read option for " + vm, error.message)
                raise error

    def get_config_param(self, vm, VM_MEM):
        pass


def __create_vm(self, name, networks, iso, memory=512, cpu=2, size=1024, description=None):
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

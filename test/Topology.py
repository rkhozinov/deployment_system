__author__ = 'Administrator'


class Topology(object):
    host, networks, vms, vnc_port = None

    def __init__(self, config_path):
        self._load(self, config_path)

    def _load(self, config_path):


    def create(self):
        self._create_networks(self)
        self._create_vms(self)

    def destroy(self, stack_name):
        """
        Destroy topology by stack_name
        """

        sw_name = 'sw_' + options.stack_name
        manager.destroy_virtual_switch(sw_name, hostname)

    def _destroy_resource_pool(self, resource_pool, hostname=None):
        if hostname is None:
            hostname = self.h
        manager.destroy_resource_pool_with_vms(resource_pool, hostname)

    def _create_networks(self):
        pass

    def _create_vms(self):
        pass


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
    def __init__(self, name, networks, iso, mem=512, cpu=2, size=1024, description=None):
        self.name = name
        self.iso = iso
        self.memory = mem
        self.cpu = cpu
        self.size = size * 1024
        self.description = description


top = Topology()

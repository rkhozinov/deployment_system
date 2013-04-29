from lib.pyshpere2 import Creator as manager
from lib.pyshpere2 import CreatorException as exception


class VirtualMachine(object):
    def __init__(self, name, connected_networks, memory=512, cpu=2, size=1024, iso=None, description=None,
                 neighbours=None,
                 configuration=None):
        """

        :param name: virtual machine name
        :param connected_networks:
        :param iso:
        :param memory:
        :param cpu:
        :param size:
        :param description:
        :param neighbours:
        """
        self.name = name
        self.memory = memory
        self.cpu = cpu
        self.size = size * 1024
        self.description = description
        self.neighbours = neighbours
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso

    def create(self, resource_pool=None, esx_host=None, vm_iso=None):

        if resource_pool is None:
            raise Exception('Resource pool name is not exist')

        try:
            manager.create_vm(self.name, esx_host, self.iso,
                              resource_pool='/' + resource_pool,
                              networks=self.connected_networks,
                              annotation=self.description,
                              memorysize=self.memory,
                              cpucount=self.cpu,
                              disksize=self.size)
        except exception as error:
            raise error

    def destroy(self, name):
        if name is None:
            raise Exception('Virtual machine name is not exist')
        try:
            manager.destroy_vm(self.name)
        except exception as error:
            raise error

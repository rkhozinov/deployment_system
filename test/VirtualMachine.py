from test.Topology import Topology


class VirtualMachine(Topology):
    def __init__(self, name, networks, memory=512, cpu=2, size=1024, iso=None, description=None, neighbours=None,
                 configuration=None):
        """

        :param name:
        :param networks:
        :param iso:
        :param memory:
        :param cpu:
        :param size:
        :param description:
        :param neighbours:
        """
        if iso is None:
            self.iso = self.config.iso

        self.name = name
        self.memory = memory
        self.cpu = cpu
        self.size = size * 1024
        self.description = description
        self.neighbours = neighbours
        self.networks = networks
        self.configuration = configuration

    def create(self, resource_pool=None, esx_host=None, vm_iso=None):
        if esx_host is None:
            esx_host = self.config.esx_host
        if resource_pool is None:
            resource_pool = self.resource_pool

        try:
            self.manager.create_vm(self.name, esx_host, self.iso,
                                   resource_pool='/' + resource_pool,
                                   networks=self.networks,
                                   annotation=self.description,
                                   memorysize=self.memory,
                                   cpucount=self.cpu,
                                   disksize=self.size)
        except Exception as error:
            raise error

    def destroy(self, resource_pool=None):
        try:
            self.manager.destroy_vm(self.name)
        except Exception as error:
            raise error

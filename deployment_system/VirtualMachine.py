from VMController import VMController
from lib.Hatchery import CreatorException as exception


class VirtualMachine(object):
    def __init__(self, name, login, password, resource_pool, manager, esx_host, memory=512, cpu=2, size=1024,
                 connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):

        if name:
            self.name = name
        else:
            raise ValueError('Virtual machine name is not exist')

        if login:
            self.login = login
        else:
            raise ValueError('Virtual machine login is not exist')

        if password:
            self.password = password
        else:
            raise ValueError('Virtual machine password is not exist')

        if resource_pool:
            self.resource_pool = resource_pool
        else:
            raise AttributeError('Resource pool is not exist')

        if esx_host:
            self.esx_host = esx_host
        else:
            raise AttributeError('ESX host address is not exist')

        if manager:
            self.manager = manager
        else:
            raise AttributeError('ESX manager address is not exist')

        self.memory = memory
        self.cpu = cpu
        if size:
            self.size = int(size) * 1024
        else:
            self.size = 1024 * 1024
        self.description = description
        self.neighbours = neighbours
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso
        self.serial_port_path = None

    def create(self):
        try:
            self.manager.create_vm(self.name, self.esx_host, self.iso,
                                   resource_pool='/' + self.resource_pool.name,
                                   networks=self.connected_networks,
                                   annotation=self.description,
                                   memorysize=self.memory,
                                   cpucount=self.cpu,
                                   disksize=self.size)
        except exception as error:
            raise error

    def add_network(self, network):
        if not network:
            raise ValueError('Network is not exist')
        self.connected_networks.append(network)

    def add_serial_port(self):
        pass

    def destroy(self):
        try:
            self.manager.destroy_vm(self.name)
        except exception as error:
            raise error

    def configure(self, esx_host, esx_login, esx_password):
        #TODO: add configure source
        try:
            vm_ctrl = VMController(vm=self,
                                   esx_host=esx_host,
                                   esx_login=esx_login,
                                   esx_password=esx_password)

            for option in self.configuration:
                vm_ctrl.cmd(option)
        except Exception as error:
            raise error
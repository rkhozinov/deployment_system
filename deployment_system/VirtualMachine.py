from VMController import VMController
from lib.Hatchery import CreatorException as exception


class VirtualMachine(object):
    def __init__(self, name, user, password, memory=512, cpu=2, size=1024,
                 connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):

        if name:
            self.name = name
        else:
            raise ValueError('Virtual machine name is not exist')

        if user:
            self.login = user
        else:
            raise ValueError('Virtual machine user is not exist')

        if password:
            self.password = password
        else:
            raise ValueError('Virtual machine password is not exist')

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

    def create(self, manager, host_name, resource_pool_name):

        if not host_name:
            raise AttributeError('ESX host does not exist')

        if not manager:
            raise AttributeError('ESX manager address does not exist')

        if not resource_pool_name:
            raise AttributeError('Resource pool name does not exist')

        try:
            manager.create_vm_old(self.name, host_name, self.iso,
                                  resource_pool='/' + resource_pool_name,
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

    def destroy(self, manager):
        if not manager:
            raise AttributeError('ESX manager address is not exist')
        try:
            manager.destroy_vm(self.name)
        except exception as error:
            raise error

    def configure(self, host_address, host_user, user_password):
        try:
            vm_ctrl = VMController(vm=self,
                                   host_address=host_address,
                                   host_user=host_user,
                                   host_password=user_password)

            for option in self.configuration:
                vm_ctrl.cmd(option)
        except Exception as error:
            raise error
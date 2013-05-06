from VMController import VMController
from lib.Hatchery import Creator as manager
from lib.Hatchery import CreatorException as exception


class VirtualMachine(object):
    def __init__(self, name, login, password,  memory=512, cpu=2, size=1024, connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):
        """
        ESXi virtual machine
        :rtype : VirtualMachine
        :param login:
        :param password: 
        :param configuration: 
        :param name: virtual machine name
        :param connected_networks:
        :param iso:
        :param memory:
        :param cpu:
        :param size:
        :param description:
        :param neighbours:
        """

        if not name:
            raise ValueError('Virtual machine name is not exist')
        if not login:
            raise ValueError('Virtual machine login is not exist')
        if not password:
            raise ValueError('Resource pool name is not exist')

        self.name = name
        self.memory = memory
        self.cpu = cpu
        self.size = size * 1024
        self.description = description
        self.neighbours = neighbours
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso
        self.login = login
        self.password = password
        self.serial_port_path = None

    def create(self, resource_pool, esx_host):
        if not resource_pool:
            raise ValueError('Resource pool name is not exist')
        if not esx_host:
            raise ValueError('Resource pool name is not exist')

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

    def add_network(self, network):
        if not network:
            raise ValueError('Network is not exist')
        self.connected_networks.append(network)

    def add_serial_port(self):
        pass

    def destroy(self):
        try:
            manager.destroy_vm(self.name)
        except exception as error:
            raise error

    def configure(self, esx_host, esx_login, esx_password):
        #TODO: add configure source
        vm_ctrl = VMController(vm=self,
                               esx_host=esx_host,
                               esx_login=esx_login,
                               esx_password=esx_password)


        for option in self.configuration:
            vm_ctrl.cmd(option)

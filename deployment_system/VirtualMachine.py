from VMController import VMController
import lib.Hatchery as Manager
import pexpect


class VirtualMachine(object):
    def __init__(self, name, user, password, memory=512, cpu=2, size=1024,
                 connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):

        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify the virtual machine name")

        if user:
            self.login = user
        else:
            raise AttributeError("Couldn't specify the virtual machine user")

        if password:
            self.password = password
        else:
            raise AttributeError("Couldn't specify the virtual machine password")

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
            raise AttributeError("Couldn't specify the ESX host name")

        if not manager or not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")

        if not resource_pool_name:
            raise AttributeError("Couldn't specify the resource pool name")

        try:
            manager.create_vm_old(self.name, host_name, self.iso,
                                  resource_pool='/' + resource_pool_name,
                                  networks=self.connected_networks,
                                  annotation=self.description,
                                  memorysize=self.memory,
                                  cpucount=self.cpu,
                                  disksize=self.size)

        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error

    def add_serial_port(self, manager, host_address, host_user, host_password,
                serial_file_dir = 'serial_ports'):
        manager._connect_to_esx()
        vm = manager.esx_server.get_vm_by_name(name)
        path = vm.get_property('path')
        manager._disconnect_from_esx()

        path_temp = path.split(' ')
        datastore = path_temp[0][1:-1]
        vm_folder = path_temp[1].split('/')[0]
        way_to_serial_dir = '/vmfs/volumes/' + datastore + '/' + serial_dir
        way_to_serial = way_to_serial_dir + '/' + self.name
        way_to_vmx = '/vmfs/volumes/' + datastore + '/' + path_temp[1]


        commands = []
        commands.append('mrdir -p ' + way_to_serial_dir)
        commands.append('touch ' + way_to_serial)
        commands.append('sed -i \'$ a serial0.present = "TRUE"\' ' + way_to_vmx)
        commands.append('sed -i \'$ a serial0.yieldOnMsrRead = "TRUE" \' ' + way_to_vmx)
        commands.append('sed -i \'$ a serial0.fileType = "pipe" \' ' + way_to_vmx)
        commands.append('sed -i \'$ a serial0.fileName = \"' + way_to_serial + '\" \' ' + way_to_vmx)
        commands.append('sed -i \'$ a serial0.pipe.endPoint = "server" \' ' + way_to_vmx)

        child = pexpect.spawn("ssh root@" + host_address)
        child.expect(".*assword:")
        child.sendline(host_password + "\r")
        child.expect(".*\# ")
        for cmd in commands:
            child.sendline(cmd)


    def is_serial_port_exist(self):
        pass

    def destroy(self, manager):
        if not manager or not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            manager.destroy_vm(self.name)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error

    def configure(self, host_address, host_user, user_password):
        try:
            vm_ctrl = VMController(vm=self,
                                   host_address=host_address,
                                   host_user=host_user,
                                   host_password=user_password)

            for option in self.configuration:
                vm_ctrl.cmd(option)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error
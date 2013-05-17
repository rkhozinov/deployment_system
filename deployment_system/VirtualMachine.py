import pexpect

from VMController import VMController
import lib.Hatchery as Manager


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
                        serial_ports_dir='serial_ports'):

        path = None
        try:
            path = manager.get_vm_path(self.name)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error

        path_temp = path.split(' ')
        datastore = path_temp[0][1:-1]
        serial_ports_dir_path = '/vmfs/volumes/' + datastore + '/' + serial_ports_dir
        serial_port_path = serial_ports_dir_path + '/' + self.name
        vmx_config_path = '/vmfs/volumes/' + datastore + '/' + path_temp[1]

        commands = []
        commands.append('mkdir -p ' + serial_ports_dir_path)
        commands.append('touch ' + serial_port_path)
        commands.append('sed -i \'$ a serial0.present = "TRUE"\' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.yieldOnMsrRead = "TRUE" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.fileType = "pipe" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.fileName = \"' + serial_port_path + '\" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.pipe.endPoint = "server" \' ' + vmx_config_path)

        # TODO: add check for existence
        child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
        child.expect(".*assword:")
        child.sendline(host_password + "\r")
        child.expect(".*\# ")

        # delete existence serial port options from the configuration file
        child.sendline("sed -e '/^serial0/d' %s > tmp && cat tmp > %s && rm tmp"
                       % (vmx_config_path, vmx_config_path))

        for cmd in commands:
            child.sendline(cmd)

    # TODO
    def add_existance_vmdk(self, manager, host_address, host_user, host_password,
                        datastore, vmdk_path, vmdk_name, vmdk_max_size):


        vmdk_max_size = vmdk_max_size * 1024
        vmdk_flat_name = "%s-flat.vmdk"%vmdk_name[:-5]
        vmdk_location = '/vmfs/volumes/%s/%s'%(datastore,vmdk_path)

        vm_path = manager.get_vm_path(self.name)
        path_temp = vm_path.split(' ')
        vm_datastore = path_temp[0][1:-1]
        vm_folder = path_temp[1].split('/')[0]
        final_path = '/vmfs/volumes/%s/%s/'%(vm_datastore,vm_folder)
        final_path_esx_style = "[%s] %s/%s"%(vm_datastore,vm_folder,
                                             vmdk_name)

        commands = []
        commands.append('cp -f "%s/%s" "%s"' % (vmdk_location, vmdk_name, final_path))
        commands.append('cp -f "%s/%s" "%s"' % (vmdk_location, vmdk_flat_name,final_path))

##        child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
##        child.expect(".*assword:")
##        child.sendline(host_password + "\r")
##        child.expect(".*\# ")
##        #child.sendline(command)
##        child.close()
        manager.add_existanse_vmdk(self.name, final_path_esx_style, vmdk_max_size)

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
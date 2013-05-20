import pexpect

from VMController import VMController
import lib.Hatchery as Manager


class VirtualMachine(object):
    DISK_DEFAULT_SPACE = 2048

    def __init__(self, name, user, password, memory=512, cpu=2, disk_space=1024, hard_disk=None,
                 connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):

        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify a virtual machine name")

        if user:
            self.login = user
        else:
            raise AttributeError("Couldn't specify a virtual machine user")

        if password:
            self.password = password
        else:
            raise AttributeError("Couldn't specify a virtual machine password")

        self.memory = memory
        self.cpu = cpu
        self.hard_disk = hard_disk

        if self.hard_disk and not disk_space:
            raise AttributeError("Couldn't specify a disk space for the hard drive")

        if disk_space:
            self.disk_space = int(disk_space) * 1024
        else:
            self.disk_space = self.DISK_DEFAULT_SPACE * 1024

        self.description = description
        self.neighbours = neighbours
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso
        self.serial_port_path = None

    def create(self, manager, resource_pool_name, host_name=None):

        if not host_name:
            raise AttributeError("Couldn't specify the ESX host name")

        if not isinstance(manager, Manager.Creator):
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
                                  disksize=self.disk_space)

        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def add_serial_port(self, manager, host_address, host_user, host_password,
                        serial_ports_dir='serial_ports'):

        path = None
        try:
            path = manager.get_vm_path(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

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
    def add_hard_disk(self, manager, host_address, host_user, host_password):

        vmdk_flat_name = "%s-flat.vmdk" % self.hard_disk[:-5]

        try:
            vm_path = manager.get_vm_path(self.name)
        except Manager.CreatorException:
            raise

        path_tmp = vm_path.split(' ')
        datastore = path_tmp[0][1:-1]
        vm_path = path_tmp[1].split('/')[0]
        vm_path = '/vmfs/volumes/%s/%s/' % (datastore, vm_path)
        disk_name = self.hard_disk.split('/')[-1]
        vm_path_esx_style = "[%s] %s/%s" % (datastore, vm_path, disk_name)

        commands = []
        commands.append('cp -f "%s" "%s"' % (self.hard_disk, vm_path))
        commands.append('cp -f "%s" "%s"' % (vmdk_flat_name, vm_path))

        child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
        child.expect(".*assword:")
        child.sendline(host_password + "\r")
        child.expect(".*\# ")

        for cmd in commands:
            child.sendline(cmd)
        child.close()

        try:
            manager.add_existence_vmdk(disk_name=self.name, vm_path_esx_style, self.disk_space)
        except Manager.CreatorException:
            raise

    def destroy(self, manager):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            manager.destroy_vm(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def configure(self, host_address, host_user, user_password):
        try:
            vm_ctrl = VMController(vm=self,
                                   host_address=host_address,
                                   host_user=host_user,
                                   host_password=user_password)

            for option in self.configuration:
                vm_ctrl.cmd(option)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise
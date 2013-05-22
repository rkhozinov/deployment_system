import pexpect

import lib.Hatchery as Manager


class VirtualMachine(object):
    DISK_DEFAULT_SPACE = 2048
    SERIAL_PORTS_DIR = 'serial_ports'

    def __init__(self, name, user, password, memory=512, cpu=2, disk_space=None, hard_disk=None,
                 connected_networks=None, iso=None,
                 description=None, neighbours=None, configuration=None):

        if not name:
            raise AttributeError("Couldn't specify a virtual machine name")
        if not user:
            raise AttributeError("Couldn't specify a virtual machine user")
        if not password:
            raise AttributeError("Couldn't specify a virtual machine password")
        if hard_disk and not disk_space:
            raise AttributeError("Couldn't specify a disk space for the hard disk '%s'" % hard_disk)

        if disk_space:
            self.disk_space = int(disk_space) * 1024
        else:
            self.disk_space = self.DISK_DEFAULT_SPACE * 1024

        self.name = name
        self.user = user
        self.password = password
        self.memory = memory
        self.cpu = cpu
        self.hard_disk = hard_disk
        self.description = description
        self.neighbours = neighbours
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso
        self.serial_port_path = None

    def create(self, manager, resource_pool_name, host_name=None):
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

    def add_serial_port(self, manager, host_address, host_user, host_password, serial_ports_dir=None):

        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        if not host_address:
            raise AttributeError("Couldn't specify the ESX host address")
        if not host_user:
            raise AttributeError("Couldn't specify the ESX host user")
        if not host_password:
            raise AttributeError("Couldn't specify the ESX host password")
        if not serial_ports_dir:
            serial_ports_dir = self.SERIAL_PORTS_DIR

        try:
            # try to get vm path
            path = manager.get_vm_path(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

        path_temp = path.split(' ')
        datastore = path_temp[0][1:-1]
        serial_ports_dir_path = '/vmfs/volumes/' + datastore + '/' + serial_ports_dir
        self.serial_port_path = serial_ports_dir_path + '/' + self.name
        vmx_config_path = '/vmfs/volumes/' + datastore + '/' + path_temp[1]

        # commands for adding a serial port to the vm configuration file
        commands = []
        commands.append('mkdir -p ' + serial_ports_dir_path)
        commands.append('touch ' + self.serial_port_path)
        commands.append('sed -i \'$ a serial0.present = "TRUE"\' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.yieldOnMsrRead = "TRUE" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.fileType = "pipe" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.fileName = \"' + self.serial_port_path + '\" \' ' + vmx_config_path)
        commands.append('sed -i \'$ a serial0.pipe.endPoint = "server" \' ' + vmx_config_path)

        # connect to ESX host
        child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
        child.expect(".*assword:")
        child.sendline(host_password + "\r")
        child.expect(".*\# ")

        # delete existence serial port options from the configuration file
        child.sendline("sed -e '/^serial0/d' %s > tmp && cat tmp > %s && rm tmp"
                       % (vmx_config_path, vmx_config_path))

        # send commands to ESX host
        for cmd in commands:
            child.sendline(cmd)

    def __connect_to_vm_host(self, host_address, host_password, host_user):
        child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
        child.expect(".*assword:")
        child.sendline(host_password + "\r")
        child.expect(".*\# ")
        return child

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

        child = self.__connect_to_vm_host(host_address, host_password, host_user)

        for cmd in commands:
            child.sendline(cmd)
        child.close()

        try:
            manager.add_existence_vmdk(disk_name=self.name, vm_path_esx_style=vm_path_esx_style, space=self.disk_space)
        except Manager.CreatorException:
            raise

    def destroy(self, manager):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            manager.vm_power_off(self.name)
            manager.destroy_vm(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def configure(self, host_address, host_user, user_password, configuration=None):
        #todo: add add_serial_port
        #todo: add connect to vm
        if not configuration:
            configuration = self.configuration
        try:
            for option in configuration:
                self.cmd(option)

        except pexpect.ExceptionPexpect:
            raise
        pass

    def power_on(self, manager):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            manager.vm_power_on(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def power_off(self, manager):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            manager.vm_power_off(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def __connect_to_host(self, host_address, host_user, host_password):
        """
        Connects to ESX host for configure virtual machine
        :param host_address:
        :param host_user:
        :param host_password:
        :return: :raise:
        """
        try:
            connection_str = 'ssh %s@%s' % (host_user, host_address)

            # session = pexpect.spawn(connection_str)
            # session.expect('.*assword:')
            # self.logger.info(session.after)
            #
            # self.cmd(host_password, expect='.*\#')

            child = pexpect.spawn(connection_str)
            child.expect(".*assword:")
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                             (child.before, '', child.after))

            child.sendline("swordfish")
            child.expect(".*\# ")
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                             (child.before, '', child.after))

            return child
        except pexpect.ExceptionPexpect as error:
            raise error

    def __connect_to_vm(self):
        try:
            #connection_str = 'nc -U ' + os.path.normpath(self.vm.path + self.vm.name)
            connection_str = 'nc -U /vmfs/volumes/datastore1/%s/%s' % ( self.name, self.name)

            self.cmd(connection_str + '\n', expect='.*ogin:')
            self.cmd(self.user, expect='.*assword:')
            self.cmd(self.password, expect='.*:')

        except pexpect.ExceptionPexpect as error:
            raise error

    def cmd(self, command, expect=None):
        try:
            self.esx_session.sendline(command)
            self.esx_session.expect(expect)
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                             (self.esx_session.before, command, self.esx_session.after))
        except pexpect.ExceptionPexpect as error:
            raise error

    def __del__(self):
        self.esx_session.close(force=True)
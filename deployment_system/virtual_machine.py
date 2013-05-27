import pexpect
import time

import lib.hatchery as Manager


class VirtualMachine(object):
    DISK_DEFAULT_SPACE = 2048
    MEMORY_DEFAULT_SIZE = 512
    SERIAL_PORTS_DIR = 'serial_ports'

    def __init__(self, name, user, password, memory=512, cpu=2, disk_space=None, hard_disk=None,
                 connected_networks=None, iso=None,
                 description=None, configuration=None):

        if not name:
            raise AttributeError("Couldn't specify a virtual machine name")
        if not user:
            raise AttributeError("Couldn't specify a virtual machine user")
        if not password:
            raise AttributeError("Couldn't specify a virtual machine password")
        if hard_disk and not disk_space:
            raise AttributeError("Couldn't specify a disk space for the hard disk '%s'" % hard_disk)

        if disk_space:
            try:
                self.disk_space = int(disk_space) * 1024
            except Exception:
                self.disk_space = self.DISK_DEFAULT_SPACE * 1024
        else:
            self.disk_space = self.DISK_DEFAULT_SPACE * 1024

        self.name = name
        self.user = user
        self.password = password
        self.memory = memory
        self.cpu = cpu
        self.hard_disk = hard_disk
        self.description = description
        self.connected_networks = connected_networks
        self.configuration = configuration
        self.iso = iso
        self.serial_port_path = None
        self.path = None

    def create(self, manager, resource_pool_name, host_name=None):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        if not resource_pool_name:
            raise AttributeError("Couldn't specify the resource pool name")

        try:
            manager.create_vm_old(vmname=self.name,
                                  esx_hostname=host_name,
                                  iso=self.iso,
                                  resource_pool='/' + resource_pool_name,
                                  networks=self.connected_networks,
                                  description=self.description,
                                  memorysize=self.memory,
                                  cpucount=self.cpu,
                                  disk_space=self.disk_space)

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
        child = None
        try:
            child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
            child.expect(".*assword:")
            child.sendline(host_password)
            child.expect(".*\# ", timeout=2)
            # delete existence serial port options from the configuration file
            child.sendline("sed -e '/^serial0/d' %s > tmp1 && mv tmp1 %s"
                           % (vmx_config_path, vmx_config_path))

            # send commands to ESX host
            for cmd in commands:
                child.sendline(cmd)
        except Exception as error:
            raise Manager.CreatorException("Can't connect to host via ssh")
        finally:
            child.close()

    def add_hard_disk(self, manager, host_address, host_user, host_password, hard_disk=None):

        if hard_disk:
            self.hard_disk = hard_disk

        try:
            vm_path = manager.get_vm_path(self.name)

            path_tmp = vm_path.split(' ')
            datastore = path_tmp[0][1:-1]
            disk_name = self.hard_disk.split('/')[-1]
            vm_path_esx = path_tmp[1].split('/')[0]
            vm_path_esx_style = "[%s] %s/%s" % (datastore, vm_path_esx, disk_name)

            # special esx file
            vmdk_flat_name = "%s-flat.vmdk" % self.hard_disk[:-5]
            # .vmdk path on ESX
            vm_path = '/vmfs/volumes/%s/%s/' % (datastore, vm_path_esx)

            commands = []
            commands.append('cp -f "%s" "%s"' % (self.hard_disk, vm_path))
            commands.append('cp -f "%s" "%s"' % (vmdk_flat_name, vm_path))

            child = self._connect_to_vm_host(host_address, host_password, host_user)

            for cmd in commands:
                child.sendline(cmd)
            child.close()

            manager.add_existence_vmdk(vm_name=self.name, path=vm_path_esx_style, space=self.disk_space)
        except Manager.CreatorException:
            raise

    def get_path(self, manager):
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        try:
            if not self.path:
                self.path = manager.get_vm_path(self.name)
            return self.path
        except Manager.CreatorException:
            raise
        except Exception:
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

    def destroy_with_files(self, manager, host_address, host_user, host_password):
        path = self.get_path(manager)
        datastore = path.split(" ")[0][1:-1]
        vm_folder = path.split(" ")[1].split("/")[0]
        vm_path = "/vmfs/volumes/%s/%s" % (path, vm_folder)
        self.destroy(manager)

        try:
            child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
            child.expect(".*assword:")
            child.sendline(host_password)
            child.expect(".*\# ", timeout=2)
            child.sendline("rm -r %s" % vm_path)
            child.close()
        except Exception:
            #TODO add checks
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

    def configure(self, host_address, host_user, host_password, configuration=None):
        if not host_address:
            raise AttributeError("Couldn't specify ESX host address")

        if not host_user:
            raise AttributeError("Couldn't specify ESX host user")

        if not host_password:
            raise AttributeError("Couldn't specify ESX host password")

        if not configuration:
            configuration = self.configuration

        # connect to vm host
        try:
            vmctrl = self._connect_to_vm_host(host_address=host_address,
                                              host_user=host_user,
                                              host_password=host_password)
        except Manager.CreatorException:
            raise

        # todo: check 'already login' - not here!
        # # try logout

        # vmctrl.sendline('exit')
        # try:
        #     if vmctrl.expect(".*[\#:\$]", timeout=2) == 0:
        #         vmctrl.sendline('exit')
        # except Exception:
        #     pass

        # configure vm
        # todo: add waiting time
        try:
            # connect to vm via netcat
            # pipe files for netcat are in specific directory on ESX datastore
            connection_str = 'nc -U /vmfs/volumes/datastore1/%s/%s' % ( self.SERIAL_PORTS_DIR, self.name)
            vmctrl.sendline(connection_str)
            time.sleep(1)

            # input credentials - not nessesary, given in configuration
            # vmctrl.sendline(self.user)
            # vmctrl.expect('.*assword:')
            # vmctrl.sendline(self.password)
            # vmctrl.expect('.*[\#:\$]')
            for option in configuration:
                vmctrl.sendline(option)
                time.sleep(1)
            print vmctrl.after
        except Exception:
            raise Manager.CreatorException("Couldn't configure the virtual machine '%s'" % self.name)
        finally:
            vmctrl.close()


    def _connect_to_vm_host(self, host_address, host_user, host_password):
        """
        Connects to ESX host via SSH

        @rtype : pexpect
        @param host_address: ESX host address
        @param host_user: ESX host user
        @param host_password: ESX host password
        @return: pexpect object with open ssh session
        @raise: CreatorException
        """
        child = None
        try:
            child = pexpect.spawn("ssh %s@%s" % (host_user, host_address))
            child.expect(".*assword:")
            child.sendline(host_password)
            child.expect(".*\# ", timeout=2)
            return child
        except Exception:
            child.close()
            raise Manager.CreatorException("Can't connect to host via ssh")

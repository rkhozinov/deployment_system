# coding=utf-8
#
# Copyright ( С ) 2013 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import subprocess
import time

import pexpect

import lib.hatchery as Manager


class VirtualMachine(object):
    DISK_DEFAULT_SPACE = 2048
    MEMORY_DEFAULT_SIZE = 512
    SERIAL_PORTS_DIR = 'serial_ports'
    COPY_TIMEOUT = 900

    def __init__(self, name, memory=512, cpu=2, disk_space=0, hard_disk=None,
                 connected_networks=None, iso=None,
                 description=None, config_type=None, configuration=None, vnc_port=None):

        self.logger = logging.getLogger(self.__module__)
        if not name:
            msg = "Couldn't specify a virtual machine name"
            self.logger.error(msg)
            raise AttributeError(msg)
        if hard_disk and not disk_space:
            msg = "Couldn't specify a disk space for the hard disk '%s'" % hard_disk
            self.logger.error(msg)
            raise AttributeError(msg)

        try:
            self.disk_space = int(disk_space) * 1024
        except Exception:
            self.disk_space = self.DISK_DEFAULT_SPACE * 1024

        self.name = name
        self.memory = memory
        self.cpu = cpu
        self.hard_disk = hard_disk
        self.description = description
        self.connected_networks = connected_networks
        self.config_type = config_type
        self.configuration = configuration
        self.iso = iso
        self.serial_port_path = None
        self.path = None
        self.vnc_port = vnc_port

    def create(self, manager, resource_pool_name, host_name=None):
        if not isinstance(manager, Manager.Creator):
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        if not resource_pool_name:
            msg = "Couldn't specify the resource pool name"
            self.logger.error(msg)
            raise AttributeError(msg)

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
            self.logger.info("Virtual machine '%s' has been created successfully" % self.name)
        except Manager.ExistenceException as e:
            self.logger.error(e.message)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
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
            try:
                child.expect('continue', timeout=5)
                child.send('yes\n')
            except:
                pass
            child.expect(".*assword:")
            child.sendline(host_password)
            child.expect(".*\# ", timeout=2)
            self.logger.info("Successfully connection to virtual machine '%s'" % self.name)
            # delete existence serial port options from the configuration file
            child.sendline("sed -e '/^serial0/d' %s > tmp1 && mv tmp1 %s"
                           % (vmx_config_path, vmx_config_path))
            # send commands to ESX host
            for cmd in commands:
                child.sendline(cmd)

            #get config from .vmx
            self.power_on(manager=manager)
            self.power_off(manager=manager)

            current_vm = manager.get_vm_obj(self.name)
            devices = current_vm._devices
            if self.serial_port_path in str(devices):
                self.logger.info("Serial port for virtual machine '%s' was added successfully and available on '%s'" % (
                    self.name, self.serial_port_path))
            else:
                raise Manager.CreatorException("Couldn't add serial port to vm %s" % self.name)
        except Manager.CreatorException:
            raise
        except Exception:
            msg = "Can't connect to host via ssh"
            self.logger.error(msg)
            raise Manager.CreatorException(msg)
        finally:
            child.close()

    def add_hard_disk(self, manager, host_address, host_user, host_password, hard_disk=None):

        if hard_disk:
            self.hard_disk = hard_disk

        rctrl = None
        try:
            vm_path = manager.get_vm_path(self.name)

            # prepare path for ESX
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
            # commands for copying ESX hard disk files
            commands.append('cp -f "%s" "%s"' % (self.hard_disk, vm_path))
            commands.append('cp -f "%s" "%s"' % (vmdk_flat_name, vm_path))

            # connect to ESX
            rctrl = self._connect_to_vm_host(host_address, host_user, host_password)

            for cmd in commands:
                rctrl.sendline(cmd)
                rctrl.expect(".*\# ", timeout=self.COPY_TIMEOUT)
                if 'No such' in rctrl.after:
                    raise NameError("Couldn't find %s for %s" % (self.hard_disk, self.name))

            manager.add_existence_vmdk(vm_name=self.name, path=vm_path_esx_style)
            self.logger.info(
                "Hard disk '%s' for virtual machine '%s' has been added successfully" % (self.hard_disk, self.name))
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise
        finally:
            rctrl.close()

    def add_vnc_access(self, manager, host_address, host_user, host_password):

        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the ESX manager")
        if not host_address:
            raise AttributeError("Couldn't specify the ESX host address")
        if not host_user:
            raise AttributeError("Couldn't specify the ESX host user")
        if not host_password:
            raise AttributeError("Couldn't specify the ESX host password")

        try:
            # try to get vm path
            path = manager.get_vm_path(self.name)
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise

        path_temp = path.split(' ')
        datastore = path_temp[0][1:-1]
        vmx_config_path = '/vmfs/volumes/' + datastore + '/' + path_temp[1]

        # commands for adding a vnc access to the vm configuration file
        commands = []
        commands.append('sed -i \'$ a RemoteDisplay.vnc.enabled = "TRUE"\' ' + vmx_config_path)
        commands.append('sed -i \'$ a RemoteDisplay.vnc.port = "%s" \' ' % self.vnc_port + vmx_config_path)

        # connect to ESX host
        rctrl = None
        try:
            rctrl = self._connect_to_vm_host(host_address, host_user, host_password)
            self.logger.info("VM '%s' has been connected successfully" % self.name)

            # delete existence vnc options from the configuration file
            rctrl.sendline("sed -e '/^RemoteDisplay/d' %s > tmp1 && mv tmp1 %s"
                           % (vmx_config_path, vmx_config_path))

            # send commands to ESX host
            for cmd in commands:
                rctrl.sendline(cmd)

            self.power_on(manager=manager)
            self.power_off(manager=manager)

            self.logger.info("VNC access for virtual machine '%s' has been added successfully and available on '%s'" % (
                self.name, self.vnc_port))

        except Exception:
            msg = "Can't connect to host via ssh"
            self.logger.error(msg)
            raise Manager.CreatorException(msg)
        finally:
            rctrl.close()

    def get_path(self, manager):
        if not isinstance(manager, Manager.Creator):
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            if not self.path:
                self.path = manager.get_vm_path(self.name)
            return self.path
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise

    def destroy(self, manager):
        if not isinstance(manager, Manager.Creator):
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            self.power_off(manager)
            manager.destroy_vm(self.name)
            self.logger.info("Virtual machine '%s' has been destroyed successfully" % self.name)
        except Manager.ExistenceException as e:
            self.logger.error(e.message)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise

    def destroy_with_files(self, manager, host_address, host_user, host_password):
        # TODO: add 'force' mode: if forced - execute 'rm -r' even if vm does not exist
        rctrl = None
        try:
            path = self.get_path(manager)

            # converting virtual machine path
            datastore = path.split(" ")[0][1:-1]
            vm_folder = path.split(" ")[1].split("/")[0]
            vm_path = "/vmfs/volumes/%s/%s" % (datastore, vm_folder)
            serial_port_path = "/vmfs/volumes/%s/%s/%s" % (datastore, self.SERIAL_PORTS_DIR, self.name)

            # destroy vm
            self.destroy(manager)
            rctrl = self._connect_to_vm_host(host_address, host_user, host_password)
            # remove all vm files
            rctrl.sendline("rm -rf %s" % vm_path)
            # remove vm serial port
            rctrl.sendline("rm %s" % serial_port_path)
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise
        finally:
            rctrl.close()

    def power_on(self, manager):
        if not isinstance(manager, Manager.Creator):
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            manager.vm_power_on(self.name)
            self.logger.info("Virtual machine's '%s' power is turned on" % self.name)
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise

    def power_off(self, manager):
        if not isinstance(manager, Manager.Creator):
            msg = "Couldn't specify the ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            manager.vm_power_off(self.name)
            self.logger.info("Virtual machine's '%s' power is turned off" % self.name)
        except Manager.ExistenceException as e:
            self.logger.error(e.message)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise

    def configure_via_com(self, host_address, host_user, host_password, configuration=None):
        if not host_address:
            msg = "VM '%s' is connected successfully" % self.name
            self.logger.error(msg)
            raise AttributeError(msg)

        if not host_user:
            msg = "Couldn't specify ESX host user"
            self.logger.error(msg)
            raise AttributeError(msg)

        if not host_password:
            msg = "Couldn't specify ESX host password"
            self.logger.error(msg)
            raise AttributeError(msg)

        if not configuration:
            configuration = self.configuration

            # configure vm
            # todo: check existence of vm
            vmctrl = None
            try:
                vmctrl = self._connect_to_vm_host(host_address=host_address,
                                                  host_user=host_user,
                                                  host_password=host_password)

                # connect to vm via netcat
                # pipe files for netcat are in specific directory on ESX datastore
                connection_str = 'nc -U /vmfs/volumes/datastore1/%s/%s' % ( self.SERIAL_PORTS_DIR, self.name)
                vmctrl.send(connection_str + '\n')
                time.sleep(1)
                self.logger.info("VM '%s' has been connected successfully" % self.name)

                for option in configuration:
                    output_start = option.find('@exp')
                    if not output_start == -1:
                        send = option[:output_start - 1]
                        expected = option[output_start + 5:]
                        if expected == '#':
                            expected = ".*\# "
                        elif expected == '$':
                            expected = ".*\$ "
                    else:
                        send = option
                        expected = None
                    vmctrl.send(send + '\n')
                    if expected:
                        vmctrl.expect(expected)

                    self.logger.info("Option '%s' to VM '%s' has been sent successfully" % (send, self.name))
                    time.sleep(1)
                self.logger.info("Virtual machine '%s' has been configured successfully" % self.name)
            except Manager.CreatorException as e:
                self.logger.error(e.message)
                raise
            except Exception:
                msg = "Couldn't configure the virtual machine '%s'" % self.name
                self.logger.error(msg)
                raise Manager.CreatorException(msg)
            finally:
                vmctrl.close()

    def configure_via_vnc(self, host_address, vnc_port=None, configuration=None):
        if not configuration:
            configuration = self.configuration
        if not vnc_port:
            vnc_port = self.vnc_port

        def run_vnc_command(vm_host, port, command, timeout):
            # This function allow to use VNC util
            # to send keys to the VNC console
            # of the virtual machine
            vncdotool = False
            path = os.environ['PATH']
            for dir_ in path.split(os.pathsep):
                bin_path = os.path.join(dir_, 'vncdotool')
                if os.path.exists(bin_path):
                    vncdotool = True
            if not vncdotool:
                raise Exception("You want working with VNC, but vncdotool not found !")
            cmd = ['vncdotool', '-s', vm_host + '::' + str(port)]
            for i in str(command):
                if i == '@':
                    new_cmd = ['key', 'shift-2']
                    subprocess.check_output(cmd + new_cmd)
                elif i == ' ':
                    new_cmd = ['type', ' ']
                    subprocess.check_output(cmd + new_cmd)
                elif i == ':':
                    new_cmd = ['key', 'shift-']
                    subprocess.check_output(cmd + new_cmd)
                else:
                    new_cmd = ['type', i]
                    subprocess.check_output(cmd + new_cmd)
                    if i == i.upper() and i != i.lower():
                        time.sleep(0.5)
                        new_cmd = ['key', 'caplk']
                        subprocess.check_output(cmd + new_cmd)
                time.sleep(0.1)
            new_cmd2 = ['key', 'enter']
            subprocess.check_output(cmd + new_cmd2)
            time.sleep(timeout)


        for option in configuration:
            output_start = option.find('@exp')
            if not output_start == -1:
                send = option[:output_start - 1]
                try:
                    timeout = int(option[output_start + 5:])
                except:
                    #TODO: add checking timeout
                    timeout = 10
            else:
                send = option
                timeout = 1
            run_vnc_command(host_address, vnc_port, configuration)


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
            try:
                child.expect('continue', timeout=5)
                child.send('yes\n')
            except:
                pass
            child.expect(".*assword:")
            child.sendline(host_password)
            child.expect(".*\# ", timeout=2)
            self.logger.info("ESX host '%s' has been connected successfully" % host_address)
            return child
        except Exception:
            child.close()
            msg = "Couldn't connect to ESX host %s via ssh" % host_address
            self.logger.error(msg)
            raise Manager.CreatorException(msg)

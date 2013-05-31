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
from lib.hatchery import ExistenceException

__author__ = 'rkhozinov'

import unittest
import logging
from deployment_system.virtual_machine import VirtualMachine
import lib.hatchery as Manager


__author__ = 'rkhozinov'


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.rpname = 'test_pool2'
        self.vmname = 'test_VM'
        self.vmuser = 'vyatta'
        self.vmpassword = 'vyatta'
        self.host_name = '172.18.93.30'
        self.host_address = '172.18.93.30'
        self.host_user = 'root'
        self.host_password = 'swordfish'
        self.vmiso = '[datastore1] vyatta_multicast.iso'
        self.manager_address = '172.18.93.40'
        self.manager_user = 'root'
        self.manager_password = 'vmware'
        self.manager = Manager.Creator(self.manager_address,
                                       self.manager_user,
                                       self.manager_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            vm = VirtualMachine(name=self.vmname)
            self.assertIsInstance(vm, VirtualMachine)
            self.assertEqual(vm.name, self.vmname)
        except AttributeError as error:
            self.assertTrue(False, error.message)

    def test_create_instance_with_invalid_name(self):
        try:
            invalid_vm_name = None
            vm = VirtualMachine(name=invalid_vm_name)
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_create_instance_with_invalid_credentials(self):
        try:
            invalid_vm_password = None
            vm = VirtualMachine(name=self.vmname)
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

        try:
            invalid_vm_user = None
            vm = VirtualMachine(name=self.vmname)
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_create_instance_with_hard_disk(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            disk_space = 1024
            vm = VirtualMachine(name=self.vmname, hard_disk=hard_disk,
                                disk_space=disk_space)
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_try_create_instance_with_hard_disk_without_space(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            vm = VirtualMachine(name=self.vmname, hard_disk=hard_disk)
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_try_create_instance_with_all_parameters(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            vm = VirtualMachine(name=self.vmname,
                                hard_disk=hard_disk,
                                memory=512,
                                cpu=2,
                                disk_space=2048,
                                connected_networks=[],
                                iso='/vfms/volumes/datastore1/image.iso',
                                description='VM descr',
                                configuration=[])
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy(self):
        # create resource pool
        try:
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass

            # create vm
            vm = None
            try:
                vm = VirtualMachine(name='net witn space', connected_networks=[''])
                vm.create(manager=self.manager,
                          host_name=self.host_name,
                          resource_pool_name=self.rpname)
            except Manager.ExistenceException:
                pass

                # # destroy vm
                # try:
                #     vm.destroy(self.manager)
                # except Manager.ExistenceException as error:
                #     pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            pass
            #self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_create_power_on_power_off_and_destroy(self):
        try:

            # create resource pool
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass

            # create vm
            vm = None
            try:
                vm = VirtualMachine(name=self.vmname)
                vm.create(manager=self.manager, host_name=self.host_name, resource_pool_name=self.rpname)
            except Manager.ExistenceException:
                pass

            # turn vm power on
            vm.power_on(self.manager)

            # turn vm power off
            vm.power_off(self.manager)

            # destroy vm
            try:
                vm.destroy(self.manager)
            except Manager.ExistenceException:
                pass

        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_add_serial_port(self):
        try:
            # create resource pool
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass

            # create vm
            vm = None
            try:
                vm = VirtualMachine(name=self.vmname)
                vm.create(manager=self.manager, host_name=self.host_name, resource_pool_name=self.rpname)
            except Manager.ExistenceException:
                pass

            # add serial port to vm
            try:
                vm.add_serial_port(self.manager, self.host_address, self.host_user, self.host_password)
            except Manager.ExistenceException:
                pass

            # turn vm power on
            vm.power_on(self.manager)

            #turn vm power off
            vm.power_off(self.manager)

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_create_and_get_path(self):
        try:
            vm = VirtualMachine(self.vmname, self.vmuser, self.vmpassword)
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass
            try:
                vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
            except Manager.ExistenceException:
                pass

            vm_path = vm.get_path(self.manager)
            self.assertIn(vm.name, vm_path)
            self.assertEqual(vm_path, vm.path)

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_try_to_get_path_with_invalid_manager(self):
        try:
            vm = VirtualMachine(self.vmname, self.vmuser, self.vmpassword)
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass
            try:
                vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
            try:
                manager = None
                vm.get_path(manager)
            except AttributeError as error:
                self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_add_hard_disk(self):
        clear_vm_name = self.vmname + '_clear'
        donor_vm_name = self.vmname + '_donor'
        clear_vm = VirtualMachine(clear_vm_name, self.vmuser, self.vmpassword)
        donor_vm = VirtualMachine(donor_vm_name, self.vmuser, self.vmpassword)
        try:
            # create resource pool
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass

            # create
            try:
                clear_vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
            try:
                donor_vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
            except Manager.ExistenceException:
                pass

            vm_path = None
            vm_path = donor_vm.get_path(manager=self.manager)

            vm_path_spilt = vm_path.split(" ")
            vmdk_donor = "/vmfs/volumes/%s/%s.vmdk" % (vm_path_spilt[0][1:-1], vm_path_spilt[1][:-4] )

            try:
                clear_vm.add_hard_disk(self.manager, self.host_name, self.host_user, self.host_password,
                                       hard_disk=vmdk_donor)
            except ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_connect_to_vm_host(self):
        virtual_machine = VirtualMachine(self.vmname, self.vmuser, self.vmpassword)
        rctrl = None
        try:
            rctrl = virtual_machine._connect_to_vm_host(self.host_address,
                                                        self.host_user,
                                                        self.host_password)
            output = rctrl.sendline('ls')
            self.assertIsNotNone(output)

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            rctrl.close()

    def test_add_hard_drive_temp(self):
        virtual_machine = VirtualMachine('t123')

        try:
            virtual_machine.disk_space = 0
            virtual_machine.create(self.manager, resource_pool_name='test_RP', host_name='172.18.93.30')
            virtual_machine.add_hard_disk(self.manager, self.host_address, self.host_user,
                                          self.host_password, hard_disk='vmfs/volumes/datastore1/tmp01/tmp01.vmdk')
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    if __name__ == "__main__":
        unittest.main()

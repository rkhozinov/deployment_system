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
            vm = VirtualMachine(name=self.vmname, user='user', password='password')
            self.assertIsInstance(vm, VirtualMachine)
            self.assertEqual(vm.name, self.vmname)
        except AttributeError as error:
            self.assertTrue(False, error.message)

    def test_create_instance_with_invalid_name(self):
        try:
            invalid_vm_name = None
            vm = VirtualMachine(name=invalid_vm_name, user='user', password='password')
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_create_instance_with_invalid_credentials(self):
        try:
            invalid_vm_password = None
            vm = VirtualMachine(name=self.vmname, user='user', password=invalid_vm_password)
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

        try:
            invalid_vm_user = None
            vm = VirtualMachine(name=self.vmname, user='user', password=invalid_vm_user)
            self.assertNotIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)


    def test_create_instance_with_hard_disk(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            disk_space = 1024
            vm = VirtualMachine(name=self.vmname, user='user', password='password', hard_disk=hard_disk,
                                disk_space=disk_space)
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)


    def test_try_create_instance_with_hard_disk_without_space(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            vm = VirtualMachine(name=self.vmname, user='user', password='password', hard_disk=hard_disk)
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_try_create_instance_with_all_parameters(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            vm = VirtualMachine(name=self.vmname,
                                user='user',
                                password='password',
                                hard_disk=hard_disk,
                                memory=512,
                                cpu=2,
                                disk_space=2048,
                                connected_networks=[],
                                iso='/vfms/volumes/datastore1/image.iso',
                                description='VM descr',
                                neighbours=[],
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
                vm = VirtualMachine(name=self.vmname, user=self.vmuser, password=self.vmpassword)
                vm.create(manager=self.manager,
                          host_name=self.host_name,
                          resource_pool_name=self.rpname)
            except Manager.ExistenceException:
                pass

            # destroy vm
            try:
                vm.destroy(self.manager)
            except Manager.ExistenceException as error:
                pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

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
                vm = VirtualMachine(name=self.vmname, user=self.vmuser, password=self.vmpassword)
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
                vm = VirtualMachine(name=self.vmname, user=self.vmuser, password=self.vmpassword)
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

            try:
                vm_path = vm.get_path(self.manager)
                self.assertIn(vm.name, vm_path)
                self.assertEqual(vm_path, vm.path)
            except ExistenceException:
                pass
        except Manager.CreatorException as error:
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
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_add_hard_disk(self):
        # todo: end test
        clear_vm_name = self.vmname + '_clear'
        donor_vm_name = self.vmname + '_donor'
        clear_vm = VirtualMachine(clear_vm_name, self.vmuser, self.vmpassword)
        donor_vm = VirtualMachine(donor_vm_name, self.vmuser, self.vmpassword)
        vmdk_donor = None
        try:
            # create resource pool
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass
            try:
                clear_vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
            try:
                donor_vm.create(manager=self.manager, resource_pool_name=self.rpname, host_name=self.host_name)
                vm_path = donor_vm.get_path(self.manager)
                vm_path_spilt = vm_path.split(" ")
                vmdk_donor = "/vmfs/volumes/%s/%s.vmdk" % (vm_path_spilt[0][1:-1], vm_path_spilt[1][:-4] )
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        try:
            clear_vm.hard_disk = vmdk_donor
            clear_vm.add_hard_disk(self.manager, self.host_name,self.host_user,self.host_password)
        except ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            pass
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)


    if __name__ == "__main__":
        unittest.main()

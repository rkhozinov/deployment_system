from lib.Hatchery import ExistenceException

__author__ = 'rkhozinov'

import unittest
import logging
from deployment_system.VirtualMachine import VirtualMachine
import lib.Hatchery as Manager


__author__ = 'rkhozinov'


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        # self.config_path = '/home/automator/Repos/deplyment_system/tests/etc/topology.ini'
        # self.treader = TopologyReader(self.config_path)

        self.rpname = 'test_pool2'
        self.vmname = 'pipe_client3'
        self.vmuser = 'vyatta'
        self.vmpassword = 'vyatta'
        self.host_name = '172.18.93.30'
        self.host_address = '172.18.30.30'
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


    def test_try_create_instance_with_hard_disk_without_space(self):
        try:
            hard_disk = '/vfms/volumes/datastore1/disk.vmdk'
            vm = VirtualMachine(name=self.vmname, user='user', password='password', hard_disk=hard_disk)
            self.assertIsInstance(vm, VirtualMachine)
        except AttributeError as error:
            self.assertTrue(True, error.message)

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

            # turn vm power off
            vm.power_off(self.manager)

        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    def test_add_hard_disk(self):

        iso = '[datastore1] vyatta_multicast.iso'
        networks = ['VLAN1002']
        esx_host = 'vaytta-dell-1'
        clear_vm = VirtualMachine(self.vmname, self.vmuser, self.vmpassword)
        donor_vm = VirtualMachine(self.vmname, self.vmuser, self.vmpassword)
        clear_vm_name = self.vmname
        donor_vm_name = self.vmname + '_donor'
        vm_path = None
        try:
            # create resource pool
            try:
                self.manager.create_resource_pool(name=self.rpname)
            except Manager.ExistenceException:
                pass

            try:
                clear_vm.create(self.manager, esx_host, self.rpname)
            except Manager.ExistenceException:
                pass
            try:
                donor_vm.create(self.manager, esx_host, self.rpname)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        disk_path = None
        try:
            vm_path = self.manager.get_vm_path(donor_vm)
            path_temp = vm_path.split(' ')
            vm_datastore = path_temp[0][1:-1]
            vm_folder = path_temp[1].split('/')[0]
            disk_path = '/vmfs/volumes/%s/%s/%s.vmdk' % (vm_datastore, vm_folder, vm_folder)
        except ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)

    if __name__ == "__main__":
        unittest.main()

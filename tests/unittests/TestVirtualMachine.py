from lib.Hatchery import ExistenceException

__author__ = 'rkhozinov'

import unittest
import logging
from deployment_system.VirtualMachine import VirtualMachine
import lib.Hatchery as Manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.treader = TopologyReader(self.config_path)

        self.rpname = 'test_pool2'
        self.vmname = 'pipe_client3'
        self.vmuser = 'vyatta'
        self.vmpassword = 'vyatta'
        self.host_name = self.treader.host_name
        self.host_address = self.treader.host_address
        self.host_user = self.treader.host_user
        self.host_password = self.treader.host_password
        self.vmiso = '[datastore1] vyatta_multicast.iso'
        self.manager = Manager.Creator(self.treader.manager_address,
                                       self.treader.manager_user,
                                       self.treader.manager_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            vm = VirtualMachine(self.vmname, user='login', password='password')
            self.assertIsInstance(vm, VirtualMachine)
            self.assertEqual(vm.name, self.vmname)
        except AttributeError as e:
            self.logger.critical(e.message)
            self.fail(e.message)


    def test_create_virtual_machine_on_esx(self):
        networks = ['VLAN1002']
        # create resource pool
        # if rp already exist, then nothing to do
        try:
            self.manager.create_resource_pool(self.rpname)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        # create virtual machine
        try:
            vm = VirtualMachine(name=self.vmname,
                                user=self.vmuser,
                                password=self.vmpassword,
                                iso=self.vmiso,
                                connected_networks=networks)
            vm.create(manager=self.manager,
                      host_name=self.host_name,
                      resource_pool_name=self.rpname)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_virtual_machine(self):
        try:
            vm = VirtualMachine(self.vmname, self.rpname, 'login', 'password')
            vm.destroy(self.manager)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_serial_port(self):
        try:
            vm = VirtualMachine('pipe_client', user='login', password='password')
            vm.add_serial_port(self.manager, self.host_address, self.host_user, self.host_password)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_turn_on_vm(self):
        self.test_create_virtual_machine_on_esx()
        try:
            self.manager.vm_power_on(self.vmname)
        except ExistenceException as error:
            self.assertTrue(True, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_turn_off_vm(self):
        self.test_create_virtual_machine_on_esx()
        try:
            self.manager.vm_power_off(self.vmname)
        except ExistenceException as error:
            self.assertTrue(True, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

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
            clear_vm.create(self.manager, esx_host, self.rpname)
            donor_vm.create(self.manager, esx_host, self.rpname)
            vm_path = self.manager.get_vm_path(donor_vm)
            # TODO: add hard drive
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
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


    if __name__ == "__main__":
        unittest.main()

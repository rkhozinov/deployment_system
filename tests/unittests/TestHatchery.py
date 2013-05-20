import logging

import unittest2

import lib.Hatchery as Manager


class TestHatchery(unittest2.TestCase):
    def setUp(self):
        self.host_name = '172.18.93.30'
        self.manager_address = '172.18.93.40'
        self.manager_user = 'root'
        self.manager_password = 'vmware'
        self.rpname = 'test_pool2'
        self.vmname = 'test_vm'
        self.switch_name = 'test_switch'
        self.vlan_name = 'test_net'
        self.vlan_id = 1515

        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            manager = Manager.Creator(self.manager_address,
                                      self.manager_user,
                                      self.manager_password)
            self.assertIsInstance(manager, Manager.Creator)
            self.assertFalse(manager.is_connected())
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_connect_to_esx(self):
        try:
            manager = self.__get_manager()
            manager._connect_to_esx()
            self.assertTrue(manager.is_connected())
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_resource_pool(self):
        try:
            manager = self.__get_manager()
            manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.logger.warning(error.message)
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_resource_pool_only_by_name(self):
        try:
            manager = self.__get_manager()
            manager.create_resource_pool("some_rp")
        except Manager.ExistenceException as error:
            self.logger.warning(error.message)
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool(self):
        try:
            manager = self.__get_manager()
            manager.destroy_resource_pool(self.rpname, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
            self.logger.warning(error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool_with_vms(self):
        self.test_create_resource_pool()
        try:
            manager = self.__get_manager()
            manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_virtual_machine(self):
        self.test_create_resource_pool()
        try:
            manager = self.__get_manager()
            manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_virtual_machine(self):
        try:
            manager = self.__get_manager()
            manager.destroy_vm(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_switch(self):
        try:
            switch_ports = 8
            switch_name = 'test_switch'
            manager = self.__get_manager()
            manager.create_virtual_switch(name=switch_name, num_ports=switch_ports, esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_network_to_switch(self):
        manager = self.__get_manager()
        try:
            switch_ports = 8
            manager.create_virtual_switch(name=self.switch_name, num_ports=switch_ports, esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        try:
            manager.add_port_group(switch_name=self.switch_name,
                                   vlan_name=self.vlan_name,
                                   vlan_id=self.vlan_id,
                                   esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_switch(self):
        self.test_create_switch()
        try:
            manager = self.__get_manager()
            manager.destroy_virtual_switch(self.switch_name, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_get_existing_network(self):
        self.test_create_switch()
        self.test_add_network_to_switch()
        try:
            manager = self.__get_manager()
            vlan_name = manager._get_portgroup_name(name=self.vlan_name, esx_hostname=self.host_name)
            self.assertEqual(vlan_name, self.vlan_name)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_try_to_get_not_existing_network(self):
        self.test_destroy_switch()
        try:
            manager = self.__get_manager()
            vlan_name = manager._get_portgroup_name(name=self.vlan_name, esx_hostname=self.host_name)
            self.assertEqual(vlan_name, None)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_get_vm_path(self):
        self.test_create_virtual_machine()
        try:
            manager = self.__get_manager()
            manager.get_vm_path(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.test_destroy_virtual_machine()
            self.assertTrue(False, error.message)
        self.test_destroy_virtual_machine()

    def test_vm_power_on(self):
        self.test_create_virtual_machine()
        try:
            manager = self.__get_manager()
            manager.vm_power_on(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.test_destroy_virtual_machine()
            self.assertTrue(False, error.message)
        self.test_destroy_virtual_machine()

    def test_add_hard_disk(self):
        #self.test_create_resource_pool()
        manager = self.__get_manager()

        clear_vm = self.vmname
        donor_vm = self.vmname + '_donor'
        vm_path = None
        try:
            manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name, create_hard_drive=False)
        except Manager.ExistenceException as error:
            self.test_destroy_virtual_machine()
            manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name, create_hard_drive=False)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        try:
            manager.create_vm_old(vmname=donor_vm, esx_hostname=self.host_name)
            vm_path = manager.get_vm_path(donor_vm)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        disk_path = None
        try:
            vm_path = manager.get_vm_path(donor_vm)
            path_temp = vm_path.split('/')

            vm_folder = path_temp[0]
            disk_path = "%s/%s.vmdk" % (vm_folder, donor_vm)
            manager.add_existence_vmdk(clear_vm, disk_path, 2048 * 1024)

        except Exception as error:
            self.assertTrue(False, error.message)

    def __get_manager(self):
        try:
            manager = Manager.Creator(self.manager_address,
                                      self.manager_user,
                                      self.manager_password)
            return manager
        except Manager.CreatorException as e:
            raise e


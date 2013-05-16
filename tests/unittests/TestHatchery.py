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
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool(self):
        try:
            manager = self.__get_manager()
            manager.destroy_resource_pool(self.rpname, self.host_name)

        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool_with_vms(self):
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
        self.test_create_switch()
        try:

            manager = self.__get_manager()
            manager.add_port_group(switch_name=self.switch_name,
                                   vlan_name=self.vlan_name,
                                   vlan_id=self.vlan_id,
                                   esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_switch(self):
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

    def test_get_not_existing_network(self):
        self.test_destroy_switch()
        try:
            manager = self.__get_manager()
            vlan_name = manager._get_portgroup_name(name=self.vlan_name, esx_hostname=self.host_name)
            self.assertEqual(vlan_name, None)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)


    def test_get_vm_path(self):
        try:
            manager = self.__get_manager()
            manager.get_vm_path(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(False, error.message)
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


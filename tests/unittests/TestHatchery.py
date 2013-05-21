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
        self.switch_name = 'test_switch'
        self.switch_ports = 8
        self.manager = Manager.Creator(self.manager_address,
                                       self.manager_user,
                                       self.manager_password)

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
            self.manager._connect_to_esx()
            self.assertTrue(self.manager.is_connected())
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_resource_pool(self):
        try:

            self.manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool(self.rpname, esx_hostname=self.host_name)

    def test_create_resource_pool_only_by_name(self):
        try:
            self.manager.create_resource_pool("some_rp")
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool("some_rp")

    def test_destroy_resource_pool(self):
        try:
            self.manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
        except Manager.ExistenceException:
            pass
        except Manager.CreatorException as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)

        try:
            self.manager.destroy_resource_pool(self.rpname, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
            self.logger.warning(error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool_with_vms(self):
        try:
            self.manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
            self.manager.create_vm_old('for_destroy_1', esx_hostname=self.host_name, resource_pool=self.rpname)
            self.manager.create_vm_old('for_destroy_2', esx_hostname=self.host_name, resource_pool=self.rpname)
        except Manager.ExistenceException:
            pass
        except Manager.CreatorException as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)

        try:
            self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_virtual_machine(self):
        try:
            self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_vm(self.vmname)

    def test_destroy_virtual_machine(self):
        try:
            self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
        except Manager.ExistenceException:
            pass
        except Manager.CreatorException as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)
        try:
            self.manager.destroy_vm(self.vmname)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_create_switch(self):
        try:
            switch_ports = 8
            self.manager.create_virtual_switch(name=self.switch_name, num_ports=switch_ports,
                                               esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_virtual_switch(name=self.switch_name, esx_hostname=self.host_name)

    def test_add_network_to_switch(self):
        try:
            switch_ports = 8
            self.manager.create_virtual_switch(name=self.switch_name, num_ports=switch_ports,
                                               esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        try:
            self.manager.add_port_group(switch_name=self.switch_name,
                                        vlan_name=self.vlan_name,
                                        vlan_id=self.vlan_id,
                                        esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_virtual_switch(name=self.switch_name, esx_hostname=self.host_name)

    def test_destroy_switch(self):
        # Create switch
        try:
            switch_ports = 8
            self.manager.create_virtual_switch(name=self.switch_name, num_ports=switch_ports,
                                               esx_hostname=self.host_name)
        except Manager.ExistenceException:
            pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        # Add network to switch
        try:
            self.manager.add_port_group(switch_name=self.switch_name,
                                        vlan_name=self.vlan_name,
                                        vlan_id=self.vlan_id,
                                        esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

        # Destroy created switch with network
        try:
            self.manager.destroy_virtual_switch(self.switch_name, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_get_existing_network(self):
        try:
            self.manager.create_virtual_switch(name=self.switch_name, num_ports=self.switch_ports,
                                               esx_hostname=self.host_name)
            self.manager.add_port_group(switch_name=self.switch_name,
                                        vlan_name=self.vlan_name,
                                        vlan_id=self.vlan_id,
                                        esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        try:
            vlan_name = self.manager._get_portgroup_name(name=self.vlan_name, esx_hostname=self.host_name)
            self.assertEqual(vlan_name, self.vlan_name)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_virtual_switch(name=self.switch_name, esx_hostname=self.host_name)

    def test_try_to_get_not_existing_network(self):
        try:
            vlan_name = self.manager._get_portgroup_name(name=self.vlan_name, esx_hostname=self.host_name)
            self.assertEqual(vlan_name, None)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_get_vm_path(self):
        self.test_create_virtual_machine()
        try:
            self.manager.get_vm_path(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.test_destroy_virtual_machine()

    def test_vm_power_on(self):

        try:
            self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
            self.manager.vm_power_on(self.vmname)
        except Manager.ExistenceException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        self.test_destroy_virtual_machine()

    def test_add_hard_disk(self):

        clear_vm = self.vmname + 'clear'
        donor_vm = self.vmname + '_donor'
        resource_pool = 'hd_test_rp'
        vm_path = None
        try:
            self.manager.create_resource_pool(resource_pool, esx_hostname=self.host_name)
        except Manager.ExistenceException:
            pass
        except Exception as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)

        try:
            self.manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name,
                                       create_hard_drive=False, resource_pool=resource_pool)
        except Manager.ExistenceException as error:
            # if vm exist recreate it
            self.manager.destroy_vm(vmname=clear_vm)
            self.manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name,
                                       create_hard_drive=False, resource_pool=resource_pool)
        except Manager.CreatorException as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)
            self.manager.destroy_resource_pool_with_vms(resource_pool, self.host_name)

        try:
            self.manager.create_vm_old(vmname=donor_vm, esx_hostname=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)
            self.manager.destroy_resource_pool_with_vms(resource_pool, self.host_name)

        disk_path = None
        # get virtual machine path
        try:
            vm_path = self.manager.get_vm_path(donor_vm)
        except Exception as error:
            self.assertTrue(False, error.message)

        # add hard drive to vm
        try:
            path_temp = vm_path.split('/')

            vm_folder = path_temp[0]
            disk_path = "%s/%s.vmdk" % (vm_folder, donor_vm)
            self.manager.add_existence_vmdk(clear_vm, disk_path, 2048 * 1024)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(resource_pool, self.host_name)


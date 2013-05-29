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

import cProfile

import unittest2

import lib.hatchery as Manager


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
        self.profiler = cProfile.Profile()


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
        finally:
            self.manager._disconnect_from_esx()

    def test_create_and_destroy_empty_resource_pool_on_specific_host(self):
        try:
            # create rp
            try:
                self.manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
            except Manager.ExistenceException as error:
                pass

            # destroy rp
            try:
                self.manager.destroy_resource_pool(self.rpname, self.host_name)
            except Manager.ExistenceException as error:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_empty_resource_pool_by_name(self):
        rp = 'some_rp'
        try:
            # create rp
            try:
                self.manager.create_resource_pool(rp)
            except Manager.ExistenceException:
                pass

            # destroy rp
            try:
                self.manager.destroy_resource_pool(rp)
            except Manager.ExistenceException:
                pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_resource_pool_with_vms(self):
        # create rp
        try:
            try:
                self.manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            # create vms
            try:
                vmname1 = 'for_destroy_1'
                vmname2 = 'for_destroy_2'
                self.manager.create_vm_old(vmname=vmname1, esx_hostname=self.host_name, resource_pool=self.rpname)
                self.manager.create_vm_old(vmname2, esx_hostname=self.host_name, resource_pool=self.rpname)
            except Manager.ExistenceException:
                pass

            # destroy all vms and rp
            try:
                self.manager.destroy_resource_pool_with_vms(self.rpname, self.host_name)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_virtual_machine(self):
        # create vm
        try:
            try:
                self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            # destroy vm
            try:
                self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
            except Manager.ExistenceException as error:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_network_to_switch(self):
        try:
            try:
                self.manager.create_virtual_switch(name=self.switch_name, num_ports=self.switch_ports,
                                                   esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            try:
                self.manager.add_port_group(switch_name=self.switch_name,
                                            vlan_name=self.vlan_name,
                                            vlan_id=self.vlan_id,
                                            esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            self.manager.destroy_virtual_switch(name=self.switch_name, esx_hostname=self.host_name)

    def test_create_and_destroy_switch(self):
        # Create switch
        try:
            try:
                self.manager.create_virtual_switch(name=self.switch_name, num_ports=self.switch_ports,
                                                   esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            # Add network to switch
            try:
                self.manager.add_port_group(switch_name=self.switch_name,
                                            vlan_name=self.vlan_name,
                                            vlan_id=self.vlan_id,
                                            esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            # Destroy created switch with network
            try:
                self.manager.destroy_virtual_switch(self.switch_name, self.host_name)
            except Manager.ExistenceException as error:
                pass
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
            try:
                # create vm
                try:
                    self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
                except Manager.ExistenceException:
                    pass

                # get path of created virtual machine
                try:
                    vmname = self.manager.get_vm_path(self.vmname)
                    self.assertIsInstance(vmname, str)
                except Manager.ExistenceException as error:
                    pass

                # destroy vm
                try:
                    self.manager.destroy_vm(vmname=self.vmname)
                except Manager.ExistenceException as error:
                    pass
            except Exception as error:
                self.assertTrue(False, error.message)

        def test_create_power_on_power_off_and_destroy_vm(self):
            try:
                # create vm
                try:
                    self.manager.create_vm_old(vmname=self.vmname, esx_hostname=self.host_name)
                except Manager.ExistenceException:
                    pass

                # turn power on
                try:
                    self.manager.vm_power_on(self.vmname)
                except Manager.ExistenceException:
                    pass

                # turn power off
                try:
                    self.manager.vm_power_off(self.vmname)
                except Manager.ExistenceException:
                    pass

                # destroy vm
                try:
                    self.manager.destroy_vm(vmname=self.vmname)
                except Manager.ExistenceException as error:
                    pass
            except Manager.CreatorException as error:
                self.assertTrue(False, error.message)

    def test_add_hard_disk(self):
        clear_vm = self.vmname + 'clear'
        donor_vm = self.vmname + '_donor'
        resource_pool = 'hd_test_rp'

        try:
            # create a new resource pool
            try:
                self.manager.create_resource_pool(resource_pool, esx_hostname=self.host_name)
            except Manager.ExistenceException:
                pass

            # create vm without hard drive
            try:
                self.manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name,
                                           create_hard_drive=False, resource_pool=resource_pool)
            except Manager.ExistenceException as error:
                # if vm exist recreate it
                self.manager.destroy_vm(vmname=clear_vm)
                self.manager.create_vm_old(vmname=clear_vm, esx_hostname=self.host_name,
                                           create_hard_drive=False, resource_pool=resource_pool)

            # create vm with hard drive
            try:
                self.manager.create_vm_old(vmname=donor_vm, esx_hostname=self.host_name)
            except Manager.ExistenceException as error:
                pass

            # add hard drive to vm
            vm_path = self.manager.get_vm_path(donor_vm)
            path_temp = vm_path.split('/')
            vm_folder = path_temp[0]
            disk_path = "%s/%s.vmdk" % (vm_folder, donor_vm)
            disk_space = 2048 * 1024
            self.manager.add_existence_vmdk(clear_vm, disk_path, disk_space)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, "Couldn't prepare for testing: " + error.message)
        finally:
            self.manager.destroy_resource_pool_with_vms(resource_pool, self.host_name)


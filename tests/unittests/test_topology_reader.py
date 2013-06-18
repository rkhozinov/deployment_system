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

import ConfigParser
import unittest
import time

from deployment_system.resource_pool import ResourcePool
from deployment_system.switch import Switch
from deployment_system.topology_reader import TopologyReader
from deployment_system.virtual_machine import VirtualMachine
from deployment_system.network import Network
import lib.hatchery as Manager


__author__ = 'rkhozinov'


class TestTopologyReader(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'test_RP'

    def test_config_read(self):
        try:
            treader = TopologyReader(self.config_path)
            self.assertIsInstance(treader.config, ConfigParser.RawConfigParser)
        except Exception as error:
            self.assertFalse(False, error.message)

    def test_get_networks(self):
        config = TopologyReader(self.config_path)
        try:
            networks = config.get_networks()
            self.assertEqual(len(networks), len(config.networks))
            for net in config.get_networks():
                self.assertIsInstance(net, Network)
        except ConfigParser.Error as error:
            self.assertFalse(False, error.message)
        except Exception as error:
            self.assertFalse(False, error.message)

    def test_manager_options(self):
        config = TopologyReader(self.config_path)
        manager = None
        try:
            manager = Manager.Creator(manager_address=config.manager_address,
                                      manager_user=config.manager_user,
                                      manager_password=config.manager_password)
            manager._connect_to_esx()
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertFalse(False, error.message)
        finally:
            manager._disconnect_from_esx()

    def test_get_vms_from_config(self):
        config = TopologyReader(self.config_path)
        try:
            vms = config.get_virtual_machines()
            self.assertEqual(len(vms), len(config.vms))
            for vm in vms:
                self.assertIsInstance(vm, VirtualMachine)
        # except ConfigParser.Error as error:
        #     self.assertTrue(False, error.message)
        # except Exception as error:
        #     self.assertFalse(False, error.message)
        except:
            raise

    def test_create_vms_from_config(self):
        manager = None
        config = None
        sw_name = 'test_switch'

        try:
            config = TopologyReader(self.config_path)
            manager = Manager.Creator(manager_address=config.manager_address,
                                      manager_user=config.manager_user,
                                      manager_password=config.manager_password)

            for net in config.get_networks():
                try:
                    if net.isolated:
                        Switch(net.name).create(manager, config.host_name).add_network(net, manager, config.host_name)
                    else:
                        Switch(sw_name).create(manager, config.host_name).add_network(net, manager, config.host_name)
                except Manager.ExistenceException:
                    pass
            try:
                ResourcePool(name=self.rpname).create(manager=manager)
            except Manager.ExistenceException:
                pass

            vms = config.get_virtual_machines()

            for vm in vms:
                try:
                    vm.create(manager=manager, resource_pool_name=self.rpname, host_name=config.host_name)
                except Manager.ExistenceException:
                    pass
                try:
                    vm.add_serial_port(manager=manager, host_address=config.host_address,
                                       host_user=config.host_user, host_password=config.host_password)
                except Manager.ExistenceException:
                    pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            ResourcePool(self.rpname).destroy(manager, with_vms=True)

    def test_create_networks_from_config(self):
        manager = None
        config = None
        sw_name = self.rpname
        try:
            config = TopologyReader(self.config_path)
            manager = Manager.Creator(manager_address=config.manager_address,
                                      manager_user=config.manager_user,
                                      manager_password=config.manager_password)

            shared_switch = Switch(self.rpname)
            networks = config.get_networks()

            #destroy isolated networks
            if shared_switch:
                shared_switch.destroy(manager, config.host_name)

            for net in networks:
                if net.isolated:
                    Switch(self.rpname + '_' + net.name).destroy(manager, config.host_name)

            shared_switch.create(manager, config.host_name)

            for net in networks:
                if net.isolated:
                    sw_name = self.rpname + '_' + net.name
                    Switch(sw_name).create(manager, config.host_name).add_network(net, manager, config.host_name)
                else:
                    shared_switch.add_network(net, manager, config.host_name)

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

    def test_create_and_configure_some_vm_and_networks(self):
        # DO NOT TOUCH!
        manager = None
        try:
            config = TopologyReader(self.config_path)
            manager = Manager.Creator(manager_address=config.manager_address,
                                      manager_user=config.manager_user,
                                      manager_password=config.manager_password)

            # DESTROY VIRTUAL MACHINES
            vms = config.get_virtual_machines()
            for vm in vms:
                try:
                    vm.destroy_with_files(manager, host_address=config.host_address,
                                          host_user=config.host_user, host_password=config.host_password)
                except:
                    pass


            # # DESTROY NETWORKS
            # shared_switch = Switch(self.rpname)
            # networks = config.get_networks()
            #
            # # destroy shared switch with connected networks
            # try:
            #     shared_switch.destroy(manager, config.host_name)
            # except:
            #     pass
            #
            # # destroy isolated networks
            # for net in networks:
            #     if net.isolated:
            #         try:
            #             Switch(self.rpname + '_' + net.name).destroy(manager, config.host_name)
            #         except:
            #             pass
            #
            # # CREATE NETWORKS
            # try:
            #     shared_switch.create(manager, config.host_name)
            # except:
            #     pass
            #
            #
            # for net in networks:
            #     # create isolated networks
            #     if net.isolated:
            #         sw_name = self.rpname + '_' + net.name
            #         Switch(sw_name).create(manager, config.host_name).add_network(net, manager, config.host_name)
            #     else:
            #         # create simple networks on shared switch
            #         shared_switch.add_network(net, manager, config.host_name)
            #
            # # CREATE VIRTUAL MACHINES
            # try:
            #     ResourcePool(name=self.rpname).create(manager=manager)
            # except:
            #     pass

            # dublicate?
            vms = config.get_virtual_machines()

            for vm in vms:
                try:
                    vm.create(manager=manager, resource_pool_name=self.rpname, host_name=config.host_name)
                except Manager.ExistenceException:
                    pass
                try:
                    vm.add_serial_port(manager=manager, host_address=config.host_address,
                                       host_user=config.host_user, host_password=config.host_password)
                except Manager.ExistenceException:
                    pass

                if vm.hard_disk:
                    vm.add_hard_disk(manager=manager, host_address=config.host_address,
                                     host_user=config.host_user, host_password=config.host_password,
                                     hard_disk=vm.hard_disk)
                if vm.vnc_port:
                    vm.add_vnc_access(manager=manager, host_address=config.host_address,
                                      host_user=config.host_user, host_password=config.host_password)
                try:
                    vm.power_on(manager)
                except Manager.ExistenceException:
                    pass

            #todo: add boot-time
            if len(vms) < 2:
                time.sleep(30)

            for vm in vms:
                if 'com' in vm.config_type:
                    vm.configure_via_com(host_address=config.host_address, host_user=config.host_user,
                                         host_password=config.host_password)
                elif 'vnc' in vm.config_type:
                    vm.configure_via_vnc(host_address=config.host_address)
                    pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            pass
            #ResourcePool(self.rpname).destroy(manager, with_vms=True)


if __name__ == "__main__":
    unittest.main()
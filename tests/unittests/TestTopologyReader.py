import ConfigParser
import unittest
from deployment_system.ResourcePool import ResourcePool
from deployment_system.Switch import Switch

from deployment_system.TopologyReader import TopologyReader
from deployment_system.VirtualMachine import VirtualMachine
from deployment_system.Network import Network
import lib.Hatchery as Manager

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
        except ConfigParser.Error as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertFalse(False, error.message)


    def test_create_vms_from_config(self):
        manager = None
        config = None
        try:
            config = TopologyReader(self.config_path)
            manager = Manager.Creator(manager_address=config.manager_address,
                                      manager_user=config.manager_user,
                                      manager_password=config.manager_password)
            try:
                ResourcePool(name=self.rpname).create(manager=manager)
            except Manager.ExistenceException:
                pass

            vms = config.get_virtual_machines()
            try:
                for vm in vms:
                    vm.create(manager=manager, resource_pool_name=self.rpname, host_name=config.host_name)
            except Manager.ExistenceException:
                pass
        except ConfigParser.Error as error:
            self.assertTrue(False, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)
        finally:
            ResourcePool(self.rpname).destroy(manager, with_vms=True)

    def test_create_networks_from_config(self):
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

            # destroy isolated networks
            for net in config.get_networks():
                try:
                    if net.isolated:
                        Switch(net.name).destroy(manager, config.host_name)
                    else:
                        Switch(sw_name).destroy(manager, config.host_name)
                except Manager.ExistenceException:
                    pass
        except ConfigParser.Error as error:
            self.assertTrue(False, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)

if __name__ == "__main__":
    unittest.main()
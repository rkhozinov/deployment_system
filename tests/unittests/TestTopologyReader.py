import ConfigParser
import unittest

from deployment_system.TopologyReader import TopologyReader
from deployment_system.VirtualMachine import VirtualMachine
from deployment_system.VMController import VMController
from deployment_system.Network import Network
import lib.Hatchery as Manager

__author__ = 'rkhozinov'


class TestTopologyReader(unittest.TestCase):
    def setUp(self):
        self.config_path = '/home/automator/Repos/deplyment_system/tests/etc/topology.ini'

    def test_config_read(self):
        try:
            treader = TopologyReader(self.config_path)
            self.assertIsInstance(treader.config, ConfigParser.RawConfigParser)
        except Exception as e:
            self.failureException(e)

    def test_get_networks(self):
        treader = TopologyReader(self.config_path)
        networks = treader.get_networks()
        self.assertEqual(len(networks), len(treader.networks))
        for net in treader.get_networks():
            self.assertIsInstance(net, Network)

    def test_get_virtual_machines(self):
        treader = TopologyReader(self.config_path)
        vms = treader.get_virtual_machines()
        self.assertEqual(len(vms), len(treader.vms))
        for vm in vms:
            self.assertIsInstance(vm, VirtualMachine)

    def test_manager_options(self):
        treader = TopologyReader(self.config_path)
        try:
            Manager.Creator(manager_address=treader.manager_address,
                            manager_user=treader.manager_user,
                            manager_password=treader.manager_password)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_host_options(self):
        treader = TopologyReader(self.config_path)

        vm = VirtualMachine(name='pipe_client', user='vyatta', password='vyatta')
        try:
            vm_ctrl = VMController(vm, treader.host_address, treader.host_user, treader.host_password)
            self.assertIsInstance(vm_ctrl, VMController)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        except Exception as error:
            self.assertTrue(False, error.message)


if __name__ == "__main__":
    unittest.main()
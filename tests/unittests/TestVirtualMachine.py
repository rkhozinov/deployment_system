__author__ = 'rkhozinov'

import unittest
import logging
from deployment_system.ResourcePool import ResourcePool
from deployment_system.VirtualMachine import VirtualMachine
import lib.Hatchery as vm_manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'test_pool'
        self.vmname = 'test_vm'
        self.treader = TopologyReader(self.config_path)
        self.manager = vm_manager.Creator(self.treader.esx_host,
                                          self.treader.esx_login,
                                          self.treader.esx_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            vm = VirtualMachine(self.vmname, 'login', 'password')
            self.assertIsInstance(vm, VirtualMachine)
            self.assertEqual(vm.name, self.vmname)
        except AttributeError as e:
            self.logger.critical(e.message)
            self.assertTrue(False)

    def test_create_virtual_machine_on_esx(self):
        try:
            vm = VirtualMachine(self.vmname, 'login', 'password')
            rpool = ResourcePool(self.rpname, self.manager)
            vm.create()
        except Exception as e:
            self.logger.critical(e.message)
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()

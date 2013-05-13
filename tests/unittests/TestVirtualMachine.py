__author__ = 'rkhozinov'

import unittest
import logging
from deployment_system.VirtualMachine import VirtualMachine
import lib.Hatchery as vm_manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'rkhozinov'
        self.vmname = 'pipe_client3'
        self.vmlogin = 'vyatta'
        self.vmpassword = 'vyatta'
        self.treader = TopologyReader(self.config_path)
        self.manager = vm_manager.Creator(self.treader.esx_host,
                                          self.treader.esx_login,
                                          self.treader.esx_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            vm = VirtualMachine(self.vmname, login='login', password='password')
            self.assertIsInstance(vm, VirtualMachine)
            self.assertEqual(vm.name, self.vmname)
        except AttributeError as e:
            self.logger.critical(e.message)
            self.fail(e.message)


    def test_create_virtual_machine_on_esx(self):
        try:
            iso = '[datastore1] vyatta_multicast.iso'
            networks = ['VLAN1002']
            esx_host = 'vaytta-dell-1'

            vm = VirtualMachine(name=self.vmname,
                                login=self.vmlogin,
                                password=self.vmpassword,
                                iso=iso,
                                connected_networks=networks)
            vm.create(self.manager, esx_host, self.rpname)
        except Exception as e:
            self.logger.critical(e.message)
            self.fail(e.message)

    def test_destroy_virtual_machine(self):
        try:
            vm = VirtualMachine(self.vmname, self.rpname, 'login', 'password')
            vm.destroy(self.manager, self.treader.esx_host)
        except Exception as e:
            self.logger.critical(e.message)
            self.fail(e.message)


if __name__ == "__main__":
    unittest.main()

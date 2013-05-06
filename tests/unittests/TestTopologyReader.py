import ConfigParser
import unittest

from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestTopologyReader(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'

    def testReadConfig(self):
        try:
            treader = TopologyReader(self.config_path)
            self.assertIsInstance(treader.config, ConfigParser.RawConfigParser)
        except Exception as e:
            assert False

    def testGetNetworks(self):
        treader = TopologyReader(self.config_path)
        networks = treader.get_networks()
        self.assertEqual(len(networks), len(treader.networks))

    def testGetVirtualMachines(self):
        treader = TopologyReader(self.config_path)
        vms = treader.get_virtual_machines()
        self.assertEqual(len(vms), len(treader.vms))

if __name__ == "__main__":
    unittest.main()
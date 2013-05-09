import unittest
import logging
from deployment_system.ResourcePool import ResourcePool
import lib.Hatchery as vm_manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestResoursePool(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.name = 'topology'

        self.log = logging.getLogger(__name__)
        logging.basicConfig()

    def testCreateInstance(self):
        try:
            treader = TopologyReader(self.config_path)
            rpool = ResourcePool(self.name, treader.esx_host)
            self.assertIsInstance(rpool, ResourcePool)
            self.assertEqual(rpool.name, self.name)
        except:
            self.assertTrue(False)

    def testCreateRespourcePool(self):
        treader = TopologyReader(self.config_path)

        rpool = None
        try:
            manager = vm_manager.Creator(treader.esx_host, treader.esx_login, treader.esx_password)
            rpool = ResourcePool(manager, self.name)
        except Exception as e:
            self.log.critical(e.message)
            self.assertTrue(False)

        try:
            rpool.create()
        except Exception as e:
            self.log.critical(e.message)
            self.assertTrue(False)

    def testCreateResourcePoolManually(self):
        treader = TopologyReader(self.config_path)

        manager = None
        try:
            manager = vm_manager.Creator(treader.esx_host, treader.esx_login, treader.esx_password)
            self.assertIsInstance(manager,vm_manager.Creator)
        except:
            self.assertTrue(False)

        try:
            manager.create_resource_pool("topology")
            self.assertFalse(False)
        except:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
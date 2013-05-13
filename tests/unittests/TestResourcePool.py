import unittest
import logging
from deployment_system.ResourcePool import ResourcePool
import lib.Hatchery as vm_manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestResoursePool(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'topology'
        self.treader = TopologyReader(self.config_path)
        self.manager = vm_manager.Creator(self.treader.esx_host,
                                         self.treader.esx_login,
                                         self.treader.esx_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def testCreateInstance(self):
        try:

            rpool = ResourcePool(self.rpname)
            self.assertIsInstance(rpool, ResourcePool)
            self.assertEqual(rpool.name, self.rpname)
        except:
            self.assertTrue(False)

    def testCreateResourcePool(self):
        try:
            rpool = ResourcePool(name=self.rpname)
            rpool.create(self.manager)
        except Exception as e:
            self.logger.critical(e.message)
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
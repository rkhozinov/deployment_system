import unittest
import logging
from deployment_system.ResourcePool import ResourcePool
import lib.Hatchery as vm_manager
from deployment_system.TopologyReader import TopologyReader


__author__ = 'rkhozinov'


class TestResoursePool(unittest.TestCase):
    def setUp(self):
        self.config_path = '../etc/topology.ini'
        self.rpname = 'test_pool'
        self.treader = TopologyReader(self.config_path)
        self.manager = vm_manager.Creator(self.treader.esx_host,
                                          self.treader.esx_login,
                                          self.treader.esx_password)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def test_create_instance(self):
        try:
            rpool = ResourcePool(self.rpname)
            self.assertIsInstance(rpool, ResourcePool)
            self.assertEqual(rpool.name, self.rpname)
        except AttributeError as e:
            self.fail(e.message)

    def test_create_resource_pool(self):
        try:
            ResourcePool(self.rpname).create(self.manager)
        except Exception as e:
            self.fail(e.message)

    def test_destroy_only_resource_pool(self):
        try:
            ResourcePool(self.rpname).destroy(self.manager)
        except Exception as e:
            self.fail(e.message)

    def test_destroy_resource_pool_with_vms(self):
        try:
            ResourcePool(self.rpname).destroy(self.manager, with_vms=True)
        except Exception as e:
            self.fail(e.message)


if __name__ == "__main__":
    unittest.main()
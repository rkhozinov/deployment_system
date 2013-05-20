import unittest
from deployment_system.ResourcePool import ResourcePool
import lib.Hatchery as Manager


__author__ = 'rkhozinov'


class TestResoursePool(unittest.TestCase):
    def setUp(self):
        self.rpname = 'test_pool'
        self.host_name = '172.18.93.30'
        self.manager = Manager.Creator('172.18.93.40',
                                       'root',
                                       'vmware')

    def test_create_instance(self):
        try:
            rpool = ResourcePool(self.rpname)
            self.assertIsInstance(rpool, ResourcePool)
            self.assertEqual(rpool.name, self.rpname)
        except AttributeError as error:
            self.assertTrue(False, error.message)

    def test_create_resource_pool(self):
        try:
            ResourcePool(self.rpname).create(self.manager)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_only_resource_pool(self):
        try:
            ResourcePool(self.rpname).destroy(self.manager)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_resource_pool_with_vms(self):
        self.test_create_resource_pool()
        try:
            #todo: add some virtual machines
            ResourcePool(self.rpname).destroy(self.manager, with_vms=True)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_invalid_instance(self):
        try:
            ResourcePool(None)
        except AttributeError as error:
            self.assertTrue(True, error.message)


if __name__ == "__main__":
    unittest.main()
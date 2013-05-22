import unittest
from deployment_system import VirtualMachine
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

    def test_try_create_invalid_instance(self):
        try:
            rpool = ResourcePool(None)
            self.assertNotIsInstance(rpool, ResourcePool)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_create_and_destroy_empty_resource_pool_on_specific_host(self):
        try:
            # create rp
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException as error:
                pass

            # destroy rp
            try:
                ResourcePool(self.rpname).destroy(self.manager)
            except Manager.ExistenceException as error:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_resource_pool_with_vms(self):
        try:

            # create resource pool
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # create vm
            try:
                vmname = self.rpname + 'vm'
                password = 'vyatta'
                user = 'vyatta'
                vm = VirtualMachine.VirtualMachine(vmname, user, password)
                vm.create(self.manager, self.rpname, self.host_name)
            except Manager.ExistenceException:
                pass

            # destroy resource pool with vm
            try:
                ResourcePool(self.rpname).destroy(self.manager, with_vms=True)
            except Manager.ExistenceException:
                pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_try_to_create_resource_pools_with_same_name(self):
        try:
            # create first rp
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # create second rp with same name
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException:
                self.assertTrue(True)

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        finally:
            ResourcePool(self.rpname).destroy(self.manager)

    def test_create_invalid_instance(self):
        try:
            ResourcePool(None)
        except AttributeError as error:
            self.assertTrue(True, error.message)


if __name__ == "__main__":
    unittest.main()
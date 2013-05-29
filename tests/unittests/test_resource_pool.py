# coding=utf-8
#
# Copyright ( С ) 2013 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from deployment_system import virtual_machine
from deployment_system.resource_pool import ResourcePool
import lib.hatchery as Manager


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

    def test_try_to_create_with_invalid_params(self):
        try:
            ResourcePool(self.rpname).create(None, None)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_try_to_destroy_with_invalid_params(self):
        try:
            ResourcePool(self.rpname).destroy(None)
        except AttributeError as error:
            self.assertTrue(True, error.message)

    def test_try_to_create_with_invalid_manager(self):
        try:
            manager_address = 'invalid_address'
            manager_user = 'root'
            manager_password = 'vmware'
            manager = Manager.Creator(manager_address, manager_user, manager_password)
            ResourcePool(self.rpname).create(manager=manager)
        except Manager.CreatorException as error:
            self.assertTrue(True, error.message)

    def test_try_to_destroy_with_invalid_manager(self):
        try:
            manager_address = 'invalid_address'
            manager_user = 'root'
            manager_password = 'vmware'
            manager = Manager.Creator(manager_address, manager_user, manager_password)
            ResourcePool(self.rpname).destroy(manager=manager)
        except Manager.CreatorException as error:
            self.assertTrue(True, error.message)

    def test_try_to_create_with_same_name(self):
        try:
            # destroy rp
            try:
                ResourcePool(self.rpname).destroy(self.manager)
            except Manager.ExistenceException as error:
                pass

            # create rp
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # create rp
            try:
                ResourcePool(self.rpname).create(self.manager, self.host_name)
            except Manager.ExistenceException as error:
                self.assertTrue(True, error.message)

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
                vm = virtual_machine.VirtualMachine(vmname, user, password)
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
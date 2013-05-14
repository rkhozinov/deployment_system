import unittest2
import lib.Hatchery as Manager


class TestHatchery(unittest2.TestCase):
    def setUp(self):
        self.host_name = '172.18.93.30'
        self.manager_address = '172.18.93.40'
        self.manager_user = 'root'
        self.manager_password = 'vmware'
        self.rpname = 'test_pool2'
        self.vmname = 'test_vm'

    def test_create_instance(self):
        try:
            manager = Manager.Creator(self.manager_address,
                                      self.manager_user,
                                      self.manager_password)
            self.assertIsInstance(manager, Manager.Creator)
            self.assertFalse(manager.is_connected())
        except Manager.CreatorException as error:
            self.fail(error.message)

    def test_connect_to_esx(self):
        try:
            manager = self.__get_manager()
            manager._connect_to_esx()
            self.assertTrue(manager.is_connected())
        except Exception as error:
            self.fail(error.message)

    def test_create_resource_pool(self):
        try:
            manager = self.__get_manager()
            manager.create_resource_pool(self.rpname, parent_rp='/', esx_hostname=self.host_name)
        except Manager.ResourcePoolExistanceException:
            pass
        except Manager.CreatorException as error:
            self.fail(error.message)

    def test_destroy_resource_pool(self):
        try:
            manager = self.__get_manager()
            manager.destroy_resource_pool(self.rpname, self.host_name)

        except Exception as error:
            self.fail(error.message)


    def test_create_virtual_machine_old_method(self):

        self.test_create_resource_pool()

        try:
            manager = self.__get_manager()
            manager.create_vm_old(self.vmname, self.host_name)
        except Exception as error:
            self.fail(error.message)

    def test_create_virtual_machine_new_method(self):

        self.test_create_resource_pool()

        try:
            manager = self.__get_manager()
            manager.create_vm_old(self.vmname, self.host_name)
        except Exception as error:
            self.fail(error.message)

    def __get_manager(self):
        try:
            manager = Manager.Creator(self.manager_address,
                                      self.manager_user,
                                      self.manager_password)
            return manager
        except Manager.CreatorException as e:
            raise e

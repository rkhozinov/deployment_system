from lib.Hatchery import CreatorException as exception


class ResourcePool(object):
    def __init__(self, manager, name):
        """
        ESXi resource pool instance
        :param name: ESXi name of a resource pool
        :param esx_host: ESXi host address
        :raise:
        """
        if not name:
            raise Exception('Do not specify the name of the resource pool')
        self.name = name
        self.manager= manager

    def create(self):
        """
        Creates a ESXi resource pool
        :raise: CreationException
        """
        try:
            self.manager.create_resource_pool(self.name)
        except exception as error:
            raise error

    def destroy(self, with_vms=False):
        """
        Destroys the resource pool
        :param with_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        try:
            if with_vms:
                self.manager.destroy_resource_pool_with_vms(self.name)
            else:
                self.manager.destroy_resource_pool(self.name)
        except exception as error:
            raise error

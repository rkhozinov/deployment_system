import lib.Hatchery as Manager


class ResourcePool(object):
    def __init__(self, name):
        """
        ESXi resource pool instance
        :param manager: ESXi manager
        :param name: ESXi name of a resource pool
        :raise: AttributeException
        """
        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify the name of the resource pool")

    def create(self, manager, host_name=None):
        """
        Creates a ESXi resource pool
        :raise: AttributeException, CreatorException
        """
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the esx manager")

        try:

            manager.create_resource_pool(name=self.name, esx_hostname=host_name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def destroy(self, manager, with_vms=False):
        """
        Destroys the resource pool
        :param with_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        if not isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the esx manager")

        try:
            if with_vms:
                manager.destroy_resource_pool_with_vms(self.name)
            else:
                manager.destroy_resource_pool(self.name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

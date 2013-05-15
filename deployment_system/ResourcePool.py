import lib.Hatchery as Manager


class ResourcePool(object):
    def __init__(self, name):
        """
        ESXi resource pool instance
        :param manager: ESXi manager
        :param name: ESXi name of a resource pool
        :raise: AttributeException
        """
        if name and isinstance(name, str):
            self.name = name
        else:
            raise AttributeError("Couldn't specify the name of the resource pool")


    def create(self, manager):
        """
        Creates a ESXi resource pool
        :raise: AttributeException, CreatorException
        """
        if not manager:
            raise AttributeError("Couldn't specify the esx manager")
        try:

            manager.create_resource_pool(self.name)
        except Manager.CreatorException as error:
            raise error

    def destroy(self, manager, with_vms=False):
        """
        Destroys the resource pool
        :param with_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        if not manager or isinstance(manager, Manager.Creator):
            raise AttributeError("Couldn't specify the esx manager")

        try:
            if with_vms:
                manager.destroy_resource_pool_with_vms(self.name)
            else:
                manager.destroy_resource_pool(self.name)
        except Manager.CreatorException as error:
            raise error

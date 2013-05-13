from lib.Hatchery import CreatorException as exception


class ResourcePool(object):
    def __init__(self, name):
        """
        ESXi resource pool instance
        :param manager: ESXi manager
        :param name: ESXi name of a resource pool
        :raise:
        """
        if name and isinstance(name, str):
            self.name = name
        else:
            raise AttributeError('Do not specify the name of the resource pool')


    def create(self, manager):
        """
        Creates a ESXi resource pool
        :raise: AttributeExcpetion, CreatorExcpetion
        """
        if not manager:
            raise AttributeError('Do not specify the ESX manager')
        try:

            manager.create_resource_pool(self.name)
        except exception as error:
            raise error

    def destroy(self, manager, with_vms=False):
        """
        Destroys the resource pool
        :param with_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        if not manager:
            raise AttributeError('Do not specify the ESX manager')

        try:
            if with_vms:
                manager.destroy_resource_pool_with_vms(self.name)
            else:
                manager.destroy_resource_pool(self.name)
        except exception as error:
            raise error

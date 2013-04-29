from lib.pyshpere2 import Creator as manager
from lib.pyshpere2 import CreatorException as exception


class ResourcePool(object):
    def __init__(self, name, esx_host):
        """
        ESXi resource pool instance
        :param name: ESXi name of a resource pool
        :param esx_host: ESXi host address
        :raise:
        """
        if name is None:
            raise Exception('Do not specify the name of the resource pool')
        if esx_host is None:
            raise Exception('Do not specify the esx host of the resource pool')
        self.name = name
        self.esx_host = esx_host

    def create(self):
        """
        Creates a ESXi resource pool
        :raise: CreationException
        """
        try:
            manager.create_resource_pool(name=self.name,
                                         esx_hostname=self.esx_host)
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
                manager.destroy_resource_pool_with_vms(self.name, self.config.esx_host)
            else:
                manager.destroy_resource_pool(self.name, self.config.esx_host)
        except exception as error:
            raise error

from test.Topology import Topology

__author__ = 'Administrator'


class ResourcePool(Topology):
    def __init__(self, name):
        if name is None:
            raise Exception('Do not specify the name of the resource pool')
        else:
            self.name = name

    def create(self):
        try:
            self.manager.create_resource_pool(name=self.name,
                                              esx_hostname=self.esx_host)
        except self.exception as error:
            raise error

    def destroy(self, save_vms=False):
        """
        Destroys the resource pool
        :param save_vms: if True  - deletes all vms in this resource pool
                         if False - save vms and move its to the up resource pool
        :raise: CreatorException
        """
        try:
            if save_vms is True:
                self.manager.destroy_resource_pool(self.name, self.config.esx_host)
            else:
                self.manager.destroy_resource_pool_with_vms(self.name, self.config.esx_host)
        except self.exception as error:
            raise error

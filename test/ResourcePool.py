from test.Topology import Topology

__author__ = 'Administrator'


class ResourcePool(Topology):
    def __init__(self, name):
        self.name = name

    def destroy(self, name=None, save_vms=False):
        if name is None:
            name = self.name
        try:
            if save_vms is True:
                self.manager.destroy_resource_pool(name, self.config.esx_host)
            else:
                self.manager.destroy_resource_pool_with_vms(name, self.config.esx_host)
        except Exception as error:
            raise error

import ConfigParser
from resource_pool import ResourcePool
from switch import Switch
from topology_reader import TopologyReader
import lib.hatchery as Manager
from lib.hatchery import CreatorException


class Topology(object):
    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology
        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        if not config_path:
            raise AttributeError("Couldn't specify configuration file name")
        if not resource_pool:
            raise AttributeError("Couldn't specify resource pool name")

        try:
            self.config = TopologyReader(config_path)
            self.resource_pool = resource_pool
            self.vm_lst = self.config.get_virtual_machines()
            self.networks_lst = self.config.get_networks()
            self.host_name = self.config.host_name
            self.manager = Manager.Creator(self.resource_pool,
                                              self.config.host_user,
                                              self.config.host_password)
        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error

    def create(self):
        try:
            # creates a resource pool for store virtual machines
            ResourcePool(self.resource_pool).create(self.manager)

            # creates networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, net.ports)
                switch.create(self.manager, self.config.host_name)
                switch.add_network(network=net, manager=self.manager, host_name=self.config.host_name)

            # creates virtual machines
            for vm in self.vm_lst:
                vm.create(resource_pool=self.resource_pool,
                          host_name=self.config.host_address)

        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error

    def destroy(self, destroy_virtual_machines=False):
        try:
            # destroys resource pool
            ResourcePool(self.resource_pool).destroy(destroy_virtual_machines)

            # destroys networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, self.config.host_address)
                switch.destroy(self.manager, self.host_name)

            # destroys virtual machines
            for vm in self.vm_lst:
                vm.destroy()

        except CreatorException as error:
            raise error


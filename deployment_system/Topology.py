import ConfigParser
from ResourcePool import ResourcePool
from Switch import Switch
from TopologyReader import TopologyReader
import lib.Hatchery as vm_manager
from lib.Hatchery import CreatorException
from VirtualMachine import VirtualMachine


class Topology(object):
    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology
        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        try:
            self.config = TopologyReader(config_path)
            self.resource_pool = resource_pool
            self.vm_lst = self.config.get_virtual_machines()
            self.networks_lst = self.config.get_networks()
            self.manager = vm_manager.Creator(self.resource_pool,
                                              self.config.esx_login,
                                              self.config.esx_password)
        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error


    def create(self):
        try:
            # creates a resource pool for store virtual machines
            ResourcePool(self.resource_pool, self.config.esx_host).create()

            # creates networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, self.config.esx_host, net.ports)
                switch.create()
                switch.add_network(net)

            # creates virtual machines
            for vm in self.vm_lst:
                vm.create(resource_pool=self.resource_pool,
                          esx_host=self.config.esx_host)

        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error

    def destroy(self, destroy_virtual_machines=False):
        try:
            # destroys resource pool
            ResourcePool(self.resource_pool, self.config.esx_host).destroy(destroy_virtual_machines)

            # destroys networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, self.config.esx_host)
                switch.destroy()

            # destroys virtual machines
            for vm in self.vm_lst:
                vm.destroy()

        except CreatorException as error:
            raise error


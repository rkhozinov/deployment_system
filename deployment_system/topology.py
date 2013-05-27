import logging

from resource_pool import ResourcePool
from switch import Switch
from topology_reader import TopologyReader
import lib.hatchery as Manager


class Topology(object):
    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology

        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

        if not config_path:
            ae = AttributeError("Couldn't specify configuration file name")
            self.logger.error(ae.message)
            raise ae
        if not resource_pool:
            ae = AttributeError("Couldn't specify resource pool name")
            self.logger.error(ae.message)
            raise ae

        try:
            self.config = TopologyReader(config_path)
            self.resource_pool = resource_pool
            self.vm_lst = self.config.get_virtual_machines()
            self.networks_lst = self.config.get_networks()
            self.host_name = self.config.host_name
            self.manager = Manager.Creator(self.resource_pool,
                                           self.config.host_user,
                                           self.config.host_password)
        except Exception as e:
            self.logger.error(e.message)
            raise e

    def create(self):
        try:
            # creates a resource pool for store virtual machines
            ResourcePool(self.resource_pool).create(self.manager)

            # creates networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    sw_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    sw_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(sw_name, net.ports)
                switch.create(self.manager, self.config.host_name)
                self.logger.info("Virtual switch '{}' was successfully created".format(switch.name))
                switch.add_network(network=net, manager=self.manager, host_name=self.config.host_name)
                self.logger.info(
                    "Network '{net}' was successfully added to switch {sw_name}".format(net=net, sw_name=switch.name))

            # creates virtual machines
            vm_name = None
            for vm in self.vm_lst:
                vm_name = self.resource_pool + '_' + vm_name
                vm.create(vm_name, host_name=self.config.host_address)
                self.logger.info("Virtual machine '{vn_name} was successfully created'".format(vm_name))
        except Exception as e:
            self.logger.error(e.message)
            raise e

    def destroy(self, destroy_virtual_machines=False):
        try:
            # destroys resource pool with vms
            ResourcePool(self.resource_pool).destroy(destroy_virtual_machines, with_vms=True)
        except Manager.ExistenceException as e:
            self.logger.warning(e.message)


        # destroys shared switch with connected networks
        try:
            sw_name = self.resource_pool
            Switch(sw_name).destroy(self.manager, self.config.host_name)
            self.logger.info("Shared switch '{sw_name}' was successfully deleted".format(sw_name))
        except Exception as e:
            self.logger.warning(e.message)

        # destroys switch with isolated networks
        for net in self.networks_lst:
            if net.isolated:
                try:
                    sw_name = self.resource_pool + '_' + net.name
                    Switch(sw_name).destroy(self.manager, self.config.host_name)
                    self.logger.info("Isolated switch '{sw_name}' was successfully deleted".format(sw_name))
                except Exception as e:
                    self.logger.warning(e.message)


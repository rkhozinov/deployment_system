import logging

import lib.Hatchery as Manager


class Switch(object):
    def __init__(self, name, ports=8):

        """
        ESXi virtual switch instance
        :param name  switch name
        :param ports: number of ports
        :param host_name: esx host address
        """
        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify a switch name")

        if ports:
            self.ports = int(ports)
        else:
            raise AttributeError("Couldn't specify a switch ports count")

        self.logger = logging.getLogger(__name__)
        logging.basicConfig()

    def add_network(self, network, manager, host_name):
        """
        Adds a network to the switch
        :raise: CreatorException, AttributeError
        """
        if not network and isinstance(network, Network):
            raise AttributeError("No network for adding")
        if not manager and isinstance(manager, Manager):
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")

        try:
            manager.add_port_group(switch_name=self.name,
                                   vlan_name=network.name,
                                   esx_hostname=host_name,
                                   vlan_id=network.vlan,
                                   promiscuous=network.promiscuous)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error

    def create(self, manager, host_name):
        """
        Creates a ESXi virtual switch
        :raise: ManagerException
        """
        if not manager and isinstance(manager, Manager):
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")
        try:
            manager.create_virtual_switch(self.name, self.ports, host_name)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error

    def destroy(self, manager, host_name):
        """
        Destroys switch by name on ESXi host
        :raise:
        """
        if not manager and isinstance(manager, Manager):
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")
        try:
            manager.destroy_virtual_switch(self.name, host_name)
        except Manager.ExistenceException as error:
            raise error
        except Manager.CreatorException as error:
            raise error
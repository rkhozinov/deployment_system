import lib.hatchery as Manager


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

    def add_network(self, network, manager, host_name):
        """
         Adds a network to the switch
        :param network: Network instance
        :param host_name: ESXi host name
        :param manager: ESXi manager instance
        :raise: CreatorException, AttributeError, ExistenceException
        """
        if not network:
            raise AttributeError("Couldn't specify network")
        if not manager:
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")

        try:
            manager.add_port_group(switch_name=self.name,
                                   vlan_name=network.name,
                                   esx_hostname=host_name,
                                   vlan_id=network.vlan,
                                   promiscuous=network.promiscuous)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def create(self, manager, host_name):
        """
        Creates a ESXi virtual switch
        :param manager: ESXi manager instance
        :param host_name: ESXi host name
        :raise: ManagerException, AttributeError, ExistenceException
        """
        if not manager:
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")
        try:
            manager.create_virtual_switch(self.name, self.ports, host_name)
            return self
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise

    def destroy(self, manager, host_name):
        """
        Destroys switch by name on ESXi host
        :param manager: ESXi manager instance
        :param host_name: ESXi host name
        :raise: AttributeError, ExistenceException, CreatorException
        """
        if not manager:
            raise AttributeError("Couldn't specify ESX manager")
        if not host_name:
            raise AttributeError("Couldn't specify ESX host name")
        try:
            manager.destroy_virtual_switch(self.name, host_name)
        except Manager.ExistenceException:
            raise
        except Manager.CreatorException:
            raise
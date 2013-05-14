from lib.Hatchery import Creator
from lib.Hatchery import CreatorException as exception


class Switch(object):
    def __init__(self, name, esx_host_name, ports=8):

        """
        ESXi virtual switch instance
        :param name  switch name
        :param ports: number of ports
        :param esx_host_name: esx host address
        """
        self.name = name
        self.ports = ports
        self.esx_host_name = esx_host_name

    def add_network(self, network, manager, esx_host_name):
        """
        Adds a network to the switch
        :raise: CreatorException
        """
        if not network and isinstance(network, Network):
            raise Exception("No network for adding")
        if not manager and isinstance(manager, Creator):
            raise Exception("Can't access to esx manager")
        if not esx_host_name:
            raise Exception("Can't specify esx hostname")

        try:
            manager.add_port_group(vswitch=self.name,
                                   name=network.name,
                                   esx_hostname=self.esx_host_name,
                                   vlan_id=network.vlan,
                                   promiscuous=network.promiscuous)
        except exception as error:
            raise error

    def create(self, manager, esx_host_name):
        """
        Creates a ESXi virtual switch
        :raise: CreatorException
        """
        if not manager and isinstance(manager, Creator):
            raise Exception("Can't access to esx manager")
        if not esx_host_name:
            raise Exception("Can't specify esx hostname")
        try:
            manager.create_virtual_switch(self.name, self.ports, self.esx_host_name)
        except exception as error:
            raise error

    def destroy(self, manager, esx_host_name):
        """
        Destroys switch by name on ESXi host
        :raise:
        """
        if not manager and isinstance(manager, Creator):
            raise Exception("Can't access to esx manager")
        if not esx_host_name:
            raise Exception("Can't specify esx hostname")
        try:
            manager.destroy_virtual_switch(self.name, self.esx_host_name)
        except exception as error:
            raise error
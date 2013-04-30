from lib.Hatchery import Creator as manager
from lib.Hatchery import CreatorException as exception


class Switch(object):
    def __init__(self, name, esx_host, ports=8):

        """
        ESXi virtual switch instance
        :param name  switch name
        :param ports: number of ports
        :param esx_host: esx host address
        """
        self.name = name
        self.ports = ports
        self.esx_host = esx_host

    def add_network(self, network):
        """
        Adds the network to the switch
        :raise: CreatorException
        """

        if network is None:
            raise Exception("No network for adding")

        try:
            manager.add_port_group(vswitch=self.name,
                                   name=network.name,
                                   esx_hostname=self.esx_host,
                                   vlan_id=network.vlan,
                                   promiscuous=network.promiscuous)
        except exception as error:
            raise error

    def create(self):
        """
        Creates a ESXi virtual switch
        :raise: CreatorException
        """
        try:
            manager.create_virtual_switch(self.name, self.ports, self.esx_host)
        except exception as error:
            raise error

    def destroy(self):
        """
        Destroys switch by name on ESXi host
        :raise:
        """
        try:
            manager.destroy_virtual_switch(self.name, self.esx_host)
        except exception as error:
            raise error
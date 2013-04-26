from test.Topology import Topology


class Switch(Topology):
    def __init__(self, prefix, name, ports, networks=None):
        self.prefix = prefix
        self.name = self.prefix + '_' + name
        self.ports = ports
        self.networks = networks

    def add_network(self, network):
        self.networks.append(network)

    def create(self, esx_host=None):
        if esx_host is None:
            esx_host = self.config.esx_host
        try:
            self.manager.create_virtual_switch(self.name, self.ports, esx_host)
            for net in self.networks:
                self.manager.add_port_group(vswitch=self.name,
                                            name=self.name,
                                            esx_hostname=self.esx_host,
                                            vlan_id=net.vlan,
                                            promiscuous=net.promiscuous)
        except Exception as exception:
            raise exception

    def create_isolated(self, network, esx_host=None):
        if esx_host is None:
            esx_host = self.config.esx_host

        try:
            self.manager.create_virtual_switch(self.name, self.ports, esx_host)
            self.manager.add_port_group(vswitch=self.name,
                                        name=self.name,
                                        esx_hostname=self.esx_host,
                                        vlan_id=network.vlan,
                                        promiscuous=network.promiscuous)
        except Exception as exception:
            raise exception

    def destroy(self, esx_host=None):
        if esx_host is None:
            esx_host = self.config.esx_host
        try:
            self.manager.destroy_virtual_switch(self.name, esx_host)
        except Exception as error:
            raise error
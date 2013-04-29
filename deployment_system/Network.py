class Network(object):
    def __init__(self, name, vlan, ports, isolated,  promiscuous=False,):
        """
        Create network with specific vlan and mode

        :param name: network name
        :param vlan: vlan number
        :param ports: numbers of ports
        :param promiscuous: promiscuous mode
        """
        self.name = name
        self.promiscuous = promiscuous
        self.ports = ports
        self.isolated = isolated
        try:
            self.vlan = int(vlan)
        except ValueError:
            self.vlan = 4095
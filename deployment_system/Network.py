class Network(object):
    def __init__(self, name, vlan, ports=8, isolated=False, promiscuous=False, ):
        """
        Create network with specific vlan and mode

        :param name: network name
        :param vlan: vlan number
        :param ports: numbers of ports
        :param promiscuous: promiscuous mode
        """
        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify network name")
        self.promiscuous = promiscuous
        self.isolated = isolated
        self.ports = ports

        if vlan:
            try:
                self.vlan = int(vlan)
            except ValueError:
                self.vlan = 4095
        else:
            raise AttributeError("Couldn't specify VLAN number")
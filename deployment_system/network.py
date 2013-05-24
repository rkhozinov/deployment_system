class Network(object):
    def __init__(self, name, vlan, ports=8, isolated=False, promiscuous=False):
        """
        Create network with specific VLAN and mode

        :param isolated: if True, then it network will be created on separate switch
        :param name: network name
        :param vlan: VLAN number
        :param ports: numbers of ports
        :param promiscuous: promiscuous mode
        :raise: AttributeError
        """
        if name:
            self.name = name
        else:
            raise AttributeError("Couldn't specify network name")
        if vlan:
            try:
                self.vlan = int(vlan)
            except ValueError:
                self.vlan = 4095
        else:
            raise AttributeError("Couldn't specify VLAN number")

        self.promiscuous = promiscuous
        self.isolated = isolated
        self.ports = ports


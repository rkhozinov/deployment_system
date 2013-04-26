class VirtualMachine(object):
    def __init__(self, name, networks, iso, memory=512, cpu=2, size=1024, description=None, neighbours=None):
        """

        :param name:
        :param networks:
        :param iso:
        :param memory:
        :param cpu:
        :param size:
        :param description:
        :param neighbours:
        """
        self.name = name
        self.iso = iso
        self.memory = memory
        self.cpu = cpu
        self.size = size * 1024
        self.description = description
        self.neighbours = neighbours
        self.networks = networks
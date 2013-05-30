import ConfigParser
import unittest
import time

from deployment_system.resource_pool import ResourcePool
from deployment_system.switch import Switch
from deployment_system.topology_reader import TopologyReader
from deployment_system.virtual_machine import VirtualMachine
from deployment_system.network import Network
from deployment_system.topology import Topology
import lib.hatchery as Manager


__author__ = 'rkhozinov'


class TestTopologyReader(unittest.TestCase):
    def test_topology_create(self):
        tplg = Topology('../etc/topology.ini','rp1')
        tplg.create()
        pass
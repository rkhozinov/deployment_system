from deployment_system.Network import Network

__author__ = 'rkhozinov'
import logging

import unittest2

from deployment_system.Switch import Switch
import lib.Hatchery as Manager


class TestSwitch(unittest2.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()
        self.host_name = '172.18.93.30'
        self.manager = Manager.Creator('172.18.93.40',
                                       'root',
                                       'vmware')

        self.switch_name = 'test_switch2'
        self.switch_ports = 8
        self.network_name = 'test_net2'
        self.vlan = 1515

        self.isolated_networks = []
        self.isolated_networks.append(Network(name=self.network_name + '1', vlan=self.vlan, isolated=True))
        self.isolated_networks.append(Network(name=self.network_name + '2', vlan=self.vlan, isolated=True))
        self.isolated_networks.append(Network(name=self.network_name + '3', vlan=self.vlan, isolated=True))
        self.networks = []
        self.networks.append(Network(name=self.network_name + '1', vlan=self.vlan, promiscuous=False))
        self.networks.append(Network(name=self.network_name + '2', vlan=self.vlan, promiscuous=False))
        self.networks.append(Network(name=self.network_name + '3', vlan=self.vlan, promiscuous=False))


    def test_create_instance(self):
        switch = Switch(name=self.switch_name, ports=self.switch_ports)
        self.assertIsInstance(switch, Switch)
        self.assertEqual(switch.name, self.switch_name)
        self.assertEqual(switch.ports, self.switch_ports)

    def test_create_switch(self):
        switch = Switch(self.switch_name, self.switch_ports)
        try:
            switch.create(self.manager, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
        return switch

    def test_add_promiscuous_network(self):
        switch = self.test_create_switch()
        try:
            network = Network(name=self.network_name, vlan=self.vlan, promiscuous=True)
            switch.add_network(network=network, manager=self.manager, host_name=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_network(self):
        self.test_destroy_switch()
        switch = self.test_create_switch()
        try:
            network = Network(name=self.network_name, vlan=self.vlan, promiscuous=False)
            switch.add_network(network=network, manager=self.manager, host_name=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)


    def test_add_some_networks(self):
        self.test_destroy_switch()
        switch = self.test_create_switch()
        try:
            for net in self.networks:
                switch.add_network(network=net, manager=self.manager, host_name=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_some_isolated_networks(self):
        self.test_destroy_switch()
        try:
            for net in self.isolated_networks:
                if net.isolated:
                    isolated_switch = Switch(net.name)
                    isolated_switch.create(self.manager, self.host_name)
                    isolated_switch.add_network(network=net, manager=self.manager, host_name=self.host_name)
                else:
                    switch = Switch(self.switch_name, self.switch_ports)
                    switch.create(self.manager, self.host_name)
                    switch.add_network(network=net, manager=self.manager, host_name=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_isolated_networks(self):
        switch = Switch(self.switch_name)
        try:
            for net in self.isolated_networks:
                if net.isolated:
                    switch.name = net.name
                elif switch.name != self.switch_name:
                    switch.name = self.switch_name
                switch.destroy(self.manager, self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_destroy_switch(self):
        try:
            switch = Switch(self.switch_name)
            switch.destroy(manager=self.manager, host_name=self.host_name)
        except Manager.ExistenceException as error:
            self.assertTrue(True, error.message)
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)
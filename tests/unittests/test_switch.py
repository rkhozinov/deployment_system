# coding=utf-8
#
# Copyright ( С ) 2013 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from deployment_system.network import Network

__author__ = 'rkhozinov'
import logging

import unittest2

from deployment_system.switch import Switch
import lib.hatchery as Manager


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

    def test_create_instance(self):
        switch = Switch(name=self.switch_name, ports=self.switch_ports)
        self.assertIsInstance(switch, Switch)
        self.assertEqual(switch.name, self.switch_name)
        self.assertEqual(switch.ports, self.switch_ports)

    def test_create_and_destroy_switch(self):
        switch = Switch(self.switch_name, self.switch_ports)
        try:
            try:
                switch.create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass
            try:
                switch.destroy(manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_promiscuous_network(self):
        switch = Switch(self.switch_name, self.switch_ports)
        try:
            # create switch
            try:
                switch.create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # add promiscuous network
            try:
                network = Network(name=self.network_name, vlan=self.vlan, promiscuous=True)
                switch.add_network(network=network, manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException as error:
                self.assertTrue(True, error.message)

            # destroy switch
            try:
                switch.destroy(manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_add_network(self):
        switch = Switch(self.switch_name, self.switch_ports)
        try:
            # create switch
            try:
                switch.create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # add network
            try:
                network = Network(name=self.network_name, vlan=self.vlan, promiscuous=False)
                switch.add_network(network=network, manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException as error:
                self.assertTrue(True, error.message)

            # destroy switch
            try:
                switch.destroy(manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException:
                pass
        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_some_networks(self):
        switch = Switch(self.switch_name, self.switch_ports)
        try:
            # create switch
            try:
                switch.create(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass

            # create networks
            networks = []
            networks.append(Network(name=self.network_name + '1', vlan=self.vlan, promiscuous=False))
            networks.append(Network(name=self.network_name + '2', vlan=self.vlan, promiscuous=False))
            networks.append(Network(name=self.network_name + '3', vlan=self.vlan, promiscuous=False))

            # add networks
            for net in networks:
                try:
                    switch.add_network(network=net, manager=self.manager, host_name=self.host_name)
                except Manager.ExistenceException:
                    pass

            # destroy switch
            try:
                switch.destroy(manager=self.manager, host_name=self.host_name)
            except Manager.ExistenceException:
                pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)

    def test_create_and_destroy_some_isolated_networks(self):
        try:

            # create isolated networks
            isolated_networks = []
            isolated_networks.append(Network(name=self.network_name + '1', vlan=self.vlan, isolated=True))
            isolated_networks.append(Network(name=self.network_name + '2', vlan=self.vlan, isolated=True))
            isolated_networks.append(Network(name=self.network_name + '3', vlan=self.vlan, isolated=True))

            # add isolated networks
            for net in isolated_networks:
                try:
                    if net.isolated:
                        Switch(net.name).create(self.manager, self.host_name).add_network(net, self.manager,
                                                                                          self.host_name)
                    else:
                        Switch(self.switch_name, self.switch_ports).create(self.manager, self.host_name).add_network(
                            net, self.manager, self.host_name)

                except Manager.ExistenceException as error:
                    pass

            # destroy isolated networks
            for net in isolated_networks:
                try:
                    if net.isolated:
                        Switch(net.name).destroy(self.manager, self.host_name)
                    else:
                        Switch(self.switch_name).destroy(self.manager, self.host_name)
                except Manager.ExistenceException:
                    pass

        except Manager.CreatorException as error:
            self.assertTrue(False, error.message)


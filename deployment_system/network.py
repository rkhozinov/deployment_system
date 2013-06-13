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

class Network(object):
    def __init__(self, name, vlan, ports=8, isolated=False, promiscuous=False):
        """
        Creates network with specific VLAN and mode

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


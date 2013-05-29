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

import logging
import lib.hatchery as Manager


class Switch(object):
    def __init__(self, name, ports=8):

        """
        ESXi virtual switch instance
        :param name  switch name
        :param ports: number of ports
        :param host_name: esx host address
        """
        self.logger = logging.getLogger(self.__module__)
        if name:
            self.name = name
        else:
            msg = "Couldn't specify a switch name"
            self.logger.error(msg)
            raise AttributeError(msg)

        if ports:
            self.ports = int(ports)
        else:
            msg = "Couldn't specify a switch ports"
            self.logger.error(msg)
            raise AttributeError(msg)

    def add_network(self, network, manager, host_name):
        """
         Adds a network to the switch
        :param network: Network instance
        :param host_name: ESXi host name
        :param manager: ESXi manager instance
        :raise: CreatorException, AttributeError, ExistenceException
        """
        if not network:
            msg = "Couldn't specify network"
            self.logger.error(msg)
            raise AttributeError(msg)
        if not manager:
            msg = "Couldn't specify ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        if not host_name:
            msg = "Couldn't specify ESX host name"
            self.logger.error(msg)
            raise AttributeError(msg)

        try:
            manager.add_port_group(switch_name=self.name,
                                   vlan_name=network.name,
                                   esx_hostname=host_name,
                                   vlan_id=network.vlan,
                                   promiscuous=network.promiscuous)
            self.logger.info("Network '{net}' successfully added to virtual switch '{switch}'".format(net=network.name,
                                                                                                      switch=self.name))
        except Manager.ExistenceException as e:
            self.logger.error(e.message)
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise Manager.CreatorException(e)

    def create(self, manager, host_name):
        """
        Creates a ESXi virtual switch
        :param manager: ESXi manager instance
        :param host_name: ESXi host name
        :raise: ManagerException, AttributeError, ExistenceException
        """
        if not manager:
            msg = "Couldn't specify ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        if not host_name:
            msg = "Couldn't specify ESX host name"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            manager.create_virtual_switch(self.name, self.ports, host_name)
            self.logger.info("Virtual switch '{}' successfully created".format(self.name))
            return self
        except Manager.ExistenceException as e:
            self.logger.error(e.message)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise

    def destroy(self, manager, host_name):
        """
        Destroys switch by name on ESXi host
        :param manager: ESXi manager instance
        :param host_name: ESXi host name
        :raise: AttributeError, ExistenceException, CreatorException
        """
        if not manager:
            msg = "Couldn't specify ESX manager"
            self.logger.error(msg)
            raise AttributeError(msg)
        if not host_name:
            msg = "Couldn't specify ESX host name"
            self.logger.error(msg)
            raise AttributeError(msg)
        try:
            manager.destroy_virtual_switch(self.name, host_name)
            self.logger.info("Virtual switch '{}' successfully destroyed".format(self.name))
        except Manager.ExistenceException as e:
            msg = '%s. %s' % (e.message, 'Nothing could be destroyed')
            self.logger.warning(msg)
            raise
        except Manager.CreatorException as e:
            self.logger.error(e.message)
            raise
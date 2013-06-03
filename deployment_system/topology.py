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

import ConfigParser
import logging
import time

from .resource_pool import ResourcePool
from .switch import Switch
from .topology_reader import TopologyReader
from lib import hatchery as Manager


class Topology(object):
    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology

        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        self.logger = logging.getLogger(self.__module__)

        if not config_path:
            ae = AttributeError("Couldn't specify configuration file name")
            self.logger.error(ae.message)
            raise ae
        if not resource_pool:
            ae = AttributeError("Couldn't specify resource pool name")
            self.logger.error(ae.message)
            raise ae

        try:
            self.config = TopologyReader(config_path)
            self.resource_pool = resource_pool
            self.vms = self.config.get_virtual_machines()
            self.networks = self.config.get_networks()
            self.host_name = self.config.host_name
            self.host_password = self.config.host_password
            self.host_user = self.config.host_user
            self.host_address = self.config.host_address
        except ConfigParser.Error as e:
            self.logger.error(e.message)
            raise e

        try:
            self.manager = Manager.Creator(self.config.manager_address,
                                           self.config.manager_user,
                                           self.config.manager_password)
        except Exception as e:
            self.logger.error(e.message)
            raise e

    def create(self):

        try:
            # creates a resource pool for store virtual machines
            ResourcePool(self.resource_pool).create(self.manager)
            # self.logger.info('Resource pool {} successfully created'.format(self.resource_pool))

            # creates networks and switches

            # CREATE NETWORKS
            shared_sw_name = '%s_%s' % (self.config.SWITCH_PREFIX, self.resource_pool)
            shared_switch = Switch(shared_sw_name)
            shared_switch.create(self.manager, self.host_name)

            for net in self.networks:
                # create isolated networks
                if net.isolated:
                    sw_name = "%s_%s_%s" % (self.config.SWITCH_PREFIX, self.resource_pool, net.name)
                    Switch(sw_name).create(self.manager, self.host_name).add_network(net, self.manager, self.host_name)
                else:
                    # create simple networks on shared switch
                    net.name = "%s_%s" % (self.resource_pool, net.name)
                    shared_switch.add_network(net, self.manager, self.host_name)

            # creates virtual machines
            for vm in self.vms:
                vm.name = "{}_{}".format(self.resource_pool, vm.name)

                for i in range(len(vm.connected_networks)):
                    for j in xrange(len(self.networks)):
                        tmp1 = self.networks[j].name.find(vm.connected_networks[i])
                        if tmp1 > 0:
                            vm.connected_networks[i] = "%s_%s" % (self.resource_pool, vm.connected_networks[i])

                vm.create(self.manager, self.resource_pool, self.host_name)
                vm.add_serial_port(manager=self.manager, host_address=self.host_address,
                                   host_user=self.host_user, host_password=self.host_password)
                if vm.hard_disk:
                    try:
                        vm.add_hard_disk(manager=self.manager, host_address=self.host_address,
                                         host_user=self.host_user, host_password=self.host_password,
                                         hard_disk=vm.hard_disk)
                    except NameError as e:
                        raise NameError()
                if vm.vnc_port != '0':
                    vm.add_vnc_access(manager=self.manager, host_address=self.host_address,
                                      host_user=self.host_user, host_password=self.host_password)
                vm.power_on(self.manager)

            #todo: add boot-time
            if len(self.vms) < 2:
                time.sleep(30)

            for vm in self.vms:
                if 'com' in vm.conf_type:
                    #TODO add configuration via VNC
                    vm.configure_via_com(host_address=self.host_address, host_user=self.host_user,
                                         host_password=self.host_password)

        except Exception as e:
            self.logger.error(e.message)
            raise e

    def destroy(self, destroy_virtual_machines=False, destroy_networks=False):

        try:
            # destroys resource pool with vms
            ResourcePool(self.resource_pool).destroy(self.manager, with_vms=destroy_virtual_machines)
            # self.logger.debug("Resource pool '{} successfully created".format(self.resource_pool))
        except Manager.ExistenceException:
            pass
        except Manager.CreatorException:
            raise
        except Exception as e:
            self.logger.error(e.message)
            raise e


        # destroys shared switch with connected networks
        if destroy_networks:
            try:
                sw_name = '{prefix}_{rpname}'.format(prefix=self.config.SWITCH_PREFIX, rpname=self.resource_pool)
                Switch(sw_name).destroy(self.manager, self.config.host_name)
            except Manager.ExistenceException:
                pass
            except Manager.CreatorException:
                pass
                # self.logger.error(e.message)

            # destroys switch with isolated networks
            for net in self.networks:
                if net.isolated:
                    try:
                        sw_name = '{}_{}_{}'.format(self.config.SWITCH_PREFIX, self.resource_pool, net.name)
                        Switch(sw_name).destroy(self.manager, self.config.host_name)
                        # self.logger.info("Isolated switch '{}' was successfully destroyed".format(sw_name))
                    except Manager.CreatorException:
                        pass
                        # self.logger.error(e.message)


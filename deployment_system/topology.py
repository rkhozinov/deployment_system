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
        rollback = []
        try:
            # creates a resource pool for store virtual machines
            resource_pool = ResourcePool(self.resource_pool)
            resource_pool.create(self.manager)
            rollback.append(resource_pool)
            # self.logger.info('Resource pool {} successfully created'.format(self.resource_pool))

            # creates networks and switches

            # CREATE NETWORKS
            shared_sw_name = '%s_%s' % (self.config.SWITCH_PREFIX, self.resource_pool)
            shared_switch = Switch(shared_sw_name)
            shared_switch.create(self.manager, self.host_name)
            rollback.append(shared_switch)

            for net in self.networks:
                # create isolated networks
                if net.isolated:
                    sw_name = "%s_%s_%s" % (self.config.SWITCH_PREFIX, self.resource_pool, net.name)
                    switch = Switch(sw_name).create(self.manager, self.host_name)
                    rollback.append(switch)
                    switch.add_network(net, self.manager, self.host_name)
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
                rollback.append(vm)
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
            if len(self.vms) < 3:
                time.sleep(120)

            for vm in self.vms:
                if 'com' in vm.config_type:
                    vm.configure_via_com(host_address=self.host_address, host_user=self.host_user,
                                         host_password=self.host_password)
                elif 'vnc' in vm.config_type:
                    vm.configure_via_vnc(host_address=self.host_address)

        except Exception as e:
            self.logger.error(e.message)
            try:
                while rollback:
                    unit = rollback.pop()
                    if 'VirtualMachine' in str(unit.__class__):
                        unit.destroy_with_files(manager=self.manager, host_address=self.host_address,
                                                host_user=self.host_user,
                                                host_password=self.host_password)
                    elif 'Switch' in str(unit.__class__):
                        unit.destroy(self.manager, self.config.host_name)
                    elif 'ResourcePool' in str(unit.__class__):
                        unit.destroy(manager=self.manager)
            except:
                self.logger.error("Couldn't revert changes; need to destroy manually:")
                for unit in rollback:
                    if 'VirtualMachine' in str(unit.__class__):
                        self.logger.error('VM %s' % unit.name)

                    elif 'Switch' in str(unit.__class__):
                        self.logger.error('Switch %s' % unit.name)
                    elif 'ResourcePool' in str(unit.__class__):
                        self.logger.error('Resource pool %s' % unit.name)
                raise
            raise e

    def destroy(self):

        for vm in self.vms:
            try:
                vm.name = "%s_%s" % (self.resource_pool, vm.name)
                vm.destroy_with_files(manager=self.manager, host_address=self.host_address,
                                      host_user=self.host_user,
                                      host_password=self.host_password)
            except Manager.ExistenceException:
                self.logger.info("Couldn't find '%s' - probably it already removed" % vm.name)
            except:
                self.logger.error("Error with destroying VM '%s'" % vm.name)

        sw_name = None
        for net in self.networks:
            try:
                if net.isolated:
                    sw_name = "%s_%s_%s" % (self.config.SWITCH_PREFIX, self.resource_pool, net.name)
                    switch = Switch(sw_name)
                    switch.destroy(self.manager, self.host_name)
            except Manager.ExistenceException:
                pass
            except:
                self.logger.error("Error with destroying switch '%s'" % sw_name)

        try:
            shared_sw_name = '%s_%s' % (self.config.SWITCH_PREFIX, self.resource_pool)
            switch = Switch(shared_sw_name)
            switch.destroy(self.manager, self.host_name)
        except Manager.ExistenceException:
            pass

        try:
            ResourcePool(self.resource_pool).destroy(self.manager)
        except Manager.ExistenceException:
            pass
        except Exception as e:
            self.logger.error(e.message)
            raise e

    def power_on(self):
        for vm in self.vms:
            try:
                vm.name = "%s_%s" % (self.resource_pool, vm.name)
                vm.power_on(manager=self.manager)
            except:
                self.logger.error("Error with VM '%s'" % vm.name)
                raise

    def power_off(self):
        for vm in self.vms:
            try:
                vm.name = "%s_%s" % (self.resource_pool, vm.name)
                vm.power_off(manager=self.manager)
            except:
                self.logger.error("Error with VM '%s'" % vm.name)
                raise
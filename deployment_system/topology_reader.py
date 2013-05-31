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
import ConfigParser
from .network import Network
from .virtual_machine import VirtualMachine


class TopologyReader(object):
    DEFAULT_PORTS_COUNT = 120

    # describe of sections
    MANAGER = 'esx_vcenter'
    HOST = 'esx'
    SETTINGS = 'settings'

    # esx manager settings
    MANAGER_ADDRESS = 'address'
    MANAGER_USER = 'user'
    MANAGER_PASSWORD = 'password'

    SWITCH_PREFIX = 'sw'

    # esx host settings
    HOST_NAME = 'name'
    HOST_ADDRESS = 'address'
    HOST_USER = 'user'
    HOST_PASSWORD = 'password'

    # common settings
    ISO = 'default_iso'
    NETWORKS = 'networks'
    VMS = 'vms'

    # network settings
    NET_VLAN = 'vlan'
    NET_PORTS = 'ports'
    NET_PROMISCUOUS = 'promiscuous'
    NET_ISOLATED = 'isolated'

    # virtual machine settings
    VM_MEM = 'memory'
    VM_CPU = 'cpu'
    VM_DISK_SPACE = 'disk_space'
    VM_DESCR = 'description'
    VM_CONFIG = 'configuration'
    VM_NETWORKS = 'networks'
    VM_ISO = 'iso'
    VM_CONFIG_TYPE = 'config_type'
    VM_HARD_DISK = 'hard_disk'
    VM_VNC_PORT = 'vnc_port'

    def __init__(self, config_path):
        """
        Reads and parse config with topology
        :param config_path: topology configuration file
        :raise: ConfigParser.Error
        """
        self.logger = logging.getLogger(self.__module__)

        # init config
        try:
            self.config = ConfigParser.RawConfigParser()
            if not self.config.read(config_path):
                raise ConfigParser.Error
            self.logger.info('Configuration found on path: %s ' % config_path)
        except ConfigParser.Error:
            self.logger.error('Configuration not found on path: %s', config_path)
            raise

        # ESX manager (vCenter) settings
        try:
            self.manager_address = self.config.get(self.MANAGER, self.MANAGER_ADDRESS)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.MANAGER, self.MANAGER_ADDRESS))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.MANAGER, self.MANAGER_ADDRESS))
            raise
        try:
            self.manager_user = self.config.get(self.MANAGER, self.MANAGER_USER)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.MANAGER, self.MANAGER_USER))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.MANAGER, self.MANAGER_USER))
            raise
        try:
            self.manager_password = self.config.get(self.MANAGER, self.MANAGER_PASSWORD)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.MANAGER, self.MANAGER_PASSWORD))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.MANAGER, self.MANAGER_PASSWORD))
            raise

        self.logger.info('ESX vCenter settings has been read successfully')

        # ESX host settings
        try:
            self.host_name = self.config.get(self.HOST, self.HOST_NAME)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.HOST, self.HOST_NAME))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.HOST, self.HOST_NAME))
            raise
        try:
            self.host_address = self.config.get(self.HOST, self.HOST_ADDRESS)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.HOST, self.HOST_ADDRESS))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.HOST, self.HOST_ADDRESS))
            raise
        try:
            self.host_user = self.config.get(self.HOST, self.HOST_USER)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.HOST, self.HOST_USER))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.HOST, self.HOST_USER))
            raise
        try:
            self.host_password = self.config.get(self.HOST, self.HOST_PASSWORD)
            self.logger.debug(
                "Option '%s' in section '%s' has been read successfully" % (self.HOST, self.HOST_PASSWORD))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.HOST, self.HOST_PASSWORD))
            raise

        self.logger.info('ESX host settings has been read successfully')

        # Default ISO image
        try:
            self.iso = self.config.get(self.SETTINGS, self.ISO)
            self.logger.debug("Default iso image is specified to '%s'" % self.iso)
        except ConfigParser.NoOptionError:
            self.logger.debug("Default iso image is not specified")
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.SETTINGS, self.ISO))
            raise

        # Topology networks list
        try:
            self.networks = self.__str_to_list_strip(self.config.get(self.SETTINGS, self.NETWORKS))
            self.logger.debug("Network list has been read successfully: {nets}".format(nets=self.networks))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.SETTINGS, self.NETWORKS))
            raise

        # Topology Virtual Machines list
        try:
            self.vms = self.__str_to_list_strip(self.config.get(self.SETTINGS, self.VMS))
            self.logger.debug("VM list has been read successfully: {vms}".format(vms=self.vms))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (self.SETTINGS, self.NETWORKS))
            raise

    def __str_to_list(self, string):
        """
        Converts string to list without whitespaces

        :param string: some string for converting to list
        :return: list of string values
        """
        return string.replace(' ', '').split(',')

    def __str_to_list_strip(self, string):
        """
         Converts string to list. Each string without whitespaces
        :param string: string for convert
        :return: list of strings
        """
        return [str.strip(x) for x in string.split(',')]

    def __get_vm(self, vm_name):

        """
        Get vm_name by name from config and parse it data
        :param vm_name: virtual machine name
        :return: VirtualMachine instance
        :raise:  ConfigParser.Error
        """

        try:
            description = self.config.get(vm_name, self.VM_DESCR)
        except ConfigParser.NoOptionError:
            description = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_DESCR, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_DESCR))
            raise
        try:
            memory = self.config.get(vm_name, self.VM_MEM)
        except ConfigParser.NoOptionError:
            memory = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_MEM, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_MEM))
            raise
        try:
            cpu = self.config.get(vm_name, self.VM_CPU)
        except ConfigParser.NoOptionError:
            cpu = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_CPU, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_CPU))
            raise
        try:
            hard_disk = self.config.get(vm_name, self.VM_HARD_DISK)
            if 'False' in hard_disk:
                # todo : review False or None option
                hard_disk = False
        except ConfigParser.NoOptionError:
            hard_disk = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_HARD_DISK, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_HARD_DISK))
            raise
        try:
            disk_space = self.config.get(vm_name, self.VM_DISK_SPACE)
        except ConfigParser.NoOptionError:
            disk_space = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_DISK_SPACE, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_DISK_SPACE))
            raise
        try:
            config = self.__str_to_list_strip(self.config.get(vm_name, self.VM_CONFIG))
            # TODO: review False or None option
            if False in config:
                config = False
        except ConfigParser.NoOptionError:
            config = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_CONFIG, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_CONFIG))
            raise

        try:
            networks = self.__str_to_list_strip(self.config.get(vm_name, self.VM_NETWORKS))
        except ConfigParser.NoOptionError:
            networks = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_NETWORKS, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_NETWORKS))
            raise

        try:
            config_type = self.config.get(vm_name, self.VM_CONFIG_TYPE)
        except ConfigParser.NoOptionError:
            config_type = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_CONFIG_TYPE, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_CONFIG_TYPE))
            raise

        try:
            vnc_port = self.config.get(vm_name, self.VM_VNC_PORT)
            if vnc_port == 0:
                vnc_port = None
        except ConfigParser.NoOptionError:
            vnc_port = None
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_VNC_PORT, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_VNC_PORT))
            raise

        try:
            iso = self.config.get(vm_name, self.VM_ISO)
            # TODO: review this
            if iso == 'False':
                raise ConfigParser.NoOptionError
        except ConfigParser.NoOptionError:
            # if not specific a iso-image for this vm_name then will be used the common iso-image
            if self.iso:
                iso = self.iso
                self.logger.debug("Not specified option '%s' in section '%s'. Will be used default iso image (%s)" % (
                    self.VM_ISO, vm_name, self.iso))
            else:
                iso = None
                self.logger.debug("Not specified option '%s' in section '%s'" % (self.VM_ISO, vm_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (vm_name, self.VM_ISO))
            raise

        return VirtualMachine(name=vm_name,
                              memory=memory,
                              cpu=cpu,
                              disk_space=disk_space,
                              connected_networks=networks,
                              iso=iso,
                              description=description,
                              config_type=config_type,
                              configuration=config,
                              hard_disk=hard_disk,
                              vnc_port=vnc_port)

    def __get_network(self, net_name):
        """
        Gets a network by name
        :param net_name: name of the network
        :return: Network instance
        :raise: ConfigParser.Error
        :rtype: Network
        """
        try:
            vlan = self.config.get(net_name, self.NET_VLAN)
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (net_name, self.NET_VLAN))
            raise
        try:
            promiscuous = self.config.getboolean(net_name, self.NET_PROMISCUOUS)
        except ConfigParser.NoOptionError:
            promiscuous = False
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.NET_PROMISCUOUS, net_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (net_name, self.NET_PROMISCUOUS))
            raise

        try:
            isolated = self.config.getboolean(net_name, self.NET_ISOLATED)
        except ConfigParser.NoOptionError:
            isolated = False
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.NET_ISOLATED, net_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (net_name, self.NET_ISOLATED))
            raise

        try:
            ports = self.config.getint(net_name, self.NET_PORTS)
        except ConfigParser.NoOptionError:
            ports = self.DEFAULT_PORTS_COUNT
            self.logger.debug("Not specified option '%s' in section '%s'" % (self.NET_PORTS, net_name))
        except ConfigParser.Error:
            self.logger.error(
                "Configuration error in section '%s' with option '%s'" % (net_name, self.NET_PORTS))
            raise

        return Network(name=net_name, vlan=vlan, ports=ports, promiscuous=promiscuous, isolated=isolated)

    def get_virtual_machines(self):
        """
        Gets the virtual machines list from the configuration file
        :return:  list of virtual machines
        :raise: ConfigParser.Error
        """
        try:
            return [self.__get_vm(vm) for vm in self.vms]
        except ConfigParser.Error:
            raise

    def get_networks(self):
        """
        Gets networks from the configuration file
        :return: list of networks
        :raise: ConfigParser.Error
        """
        try:
            return [self.__get_network(net) for net in self.networks]
        except ConfigParser.Error:
            raise


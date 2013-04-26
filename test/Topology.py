import ConfigParser
from test.TopologyReader import TopologyReader
import lib.pyshpere2 as vm_manager
from lib.pyshpere2 import CreatorException


class Topology(object):
    # TODO: create VM class in ConfigParserReader then create list of vms

    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology
        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        self.config = TopologyReader(config_path)
        self.resource_pool = resource_pool
        self.vms = None
        self.networks = None

        try:
            self.manager = vm_manager.Creator(self.esx_host, self.esx_login, self.esx_password)
        except CreatorException as error:
            self.log.critical(error.message)
            raise error

    def create(self):
        try:
            # creates a resource pool for storing virtual machines
            self.manager.create_resource_pool(name=self.stack_name, esx_hostname=self.esx_host)
            # creates a virtual switch and networks
            self.__create_networks()
            # creates and configure virtual machines
            self.__create_vms()
        except CreatorException as creator_error:
            self.log.critical(creator_error.message)
            raise creator_error
        except ConfigParser.Error as config_error:
            self.log.critical("Error in the config file.", config_error.message)
            raise config_error

    def destroy(self, resource_pool=None):
        """
        Destroy topology by stack_name
        :param resource_pool: name of a ESXi resource pool
        """
        if resource_pool is None:
            resource_pool = self.resource_pool

        self.__destroy_switch()
        self.__destroy_resource_pool(resource_pool)

    def __destroy_switch(self, switch):
        try:
            self.manager.destroy_virtual_switch(switch.name, self.config.esx_host)
        except CreatorException as error:
            raise error

    def __destroy_resource_pool(self, resource_pool, esx_host=None):
        """
        Destroy a resource pool with created vms
        :param resource_pool: name of resource which storing vms for the topology
        :param esx_host: ESXi host
        """
        if esx_host is None:
            esx_host = self.name

        manager.destroy_resource_pool_with_vms(resource_pool, esx_host)


    def __create_networks(self):
        """
        Creates virtual switch with some ports and networks

        :raise: CreatorException, ConfigParser.Error
        """
        for net in self.networks:

            # read config
            num_ports, promiscuous, vlan = None
            try:
                num_ports = self.config.getint(net, self.NET_PORTS)
                promiscuous = self.config.getboolean(net, self.NET_PROMISCUOUS)
                vlan = self.config.get(net, 'vlan')
            except ConfigParser.ParsingError as error:
                self.log.debug("Cannot parse option.", error.message)
                raise error
            except ConfigParser.NoOptionError as error:
                self.log.debug("Cannot find option.", error.message)
                raise error
            except ConfigParser.Error as error:
                self.log.debug("Error in the config file.", error.message)
                raise error

            try:
                vlan = int(vlan)
            except ValueError:
                vlan = 4095

            # create switch
            switch_name = None
            try:
                switch_name = self.SW_PREFIX + self.stack_name + '_' + net
                self.manager.create_virtual_switch(switch_name, num_ports, self.esx_host)
                self.log.info("ESXi virtual switch '%s' was created " % switch_name)
            except CreatorException as error:
                self.log.debug("Cannot create the virtual switch with name " + switch_name, error.message)
                raise error

            # add ports to the created switch
            try:
                self.manager.add_port_group(vswitch=switch_name,
                                            name=switch_name,
                                            esx_hostname=self.esx_host,
                                            vlan_id=vlan,
                                            promiscuous=promiscuous)
                self.log.info("%s ports were added to ESXi virtual switch '%s' successfully" % num_ports, switch_name)
            except CreatorException as error:
                self.log.debug("Cannot add ports to the virtual switch.", error.message)
                raise error

    def __create_vms(self):

        """
         Creates virtual machines

        :type self: Topology object
        :raise: ConfigParser.ParsingError, ConfigParser.NoOptionError, ConfigParser.Error
        """

        vm_name, vm_description, vm_mem, vm_cpu, vm_size, vm_config = None
        vm_login, vm_password, vm_vnc_port = None
        for vm in self.vms:
            # get config
            try:
                vm_name = self.stack_name + '_' + vm
                vm_description = self.config.get(vm, self.VM_DESCR)
                vm_mem = self.config.get(vm, self.VM_MEM)
                vm_cpu = self.config.get(vm, self.VM_CPU)
                vm_size = self.config.get(vm, self.VM_SIZE)
                vm_config = self.config.get(vm, self.VM_CONFIG)
                vm_networks = self.__str_to_list(self.config.get(vm, self.VM_NETWORKS))
                vm_vnc_port = self.config.getint(vm, self.VM_VNC_PORT)
                vm_login = self.config.get(vm, self.VM_LOGIN)
                vm_password = self.config.get(vm, self.VM_PASSWORD)
            except ConfigParser.ParsingError as error:
                self.log.debug("Cannot parse option.", error.message)
                raise error
            except ConfigParser.NoOptionError as error:
                self.log.debug("Cannot find option.", error.message)
                raise error
            except ConfigParser.Error as error:
                self.log.debug("Error in the config file.", error.message)
                raise error

            # rename networks
            for i in range(len(vm_networks)):
                vm_networks[i] = ('%s%s_%s') % (self.SW_PREFIX, self.stack_name, vm_networks[i])

            # get a iso image for the vm
            vm_iso = None
            try:
                vm_iso = self.config.get(vm, self.VM_NETWORKS)
                self.log.info("For vm '%s' using specific iso image '%s'" % vm, vm_iso)
            except ConfigParser.Error:
                self.log.debug("For vm '%s' using default iso image '%s'" % vm, vm_iso)
                # get a common iso
                vm_iso = self.iso

            try:
                self.manager.create_vm(vm_name, self.esx_host, vm_iso,
                                       resource_pool='/' + self.stack_name,
                                       networks=vm_networks,
                                       annotation=vm_description,
                                       memorysize=vm_mem,
                                       cpucount=vm_cpu,
                                       disksize=vm_size)
            except CreatorException as error:
                raise error

                ### TODO: add code with manual reconfiguration of the VM
                ### need to add part with VNC port configuration.
                ### add VNC port parameter to topology file for each VM
                # Start to work with VM using the VNC console.
                # After the base configuration for net interfaces and
                # telnet daemon switch to the telnet console

            # FIXME: change esx to vm credentials
            # TODO: need to add vm credentials to ini-file
            vnc_cmd(self.esx_host, vm_vnc_port, vm_login)
            vnc_cmd(self.esx_host, vm_vnc_port, vm_password)
            for option in vm_config:
                vnc_cmd(self.esx_host, vm_vnc_port, option)

            # Start to work with telnet console
            session = None
            while session is None:
                session = telnet(vm_ip_address, vm_login, vm_password)
            conf_cmds = config.get(vm_name, 'telnet_commands').split('\n')
            LOG.info(str(conf_cmds))
            session.write('conf\n')
            session.read_until('#', timeout=5)
            for cmd in conf_cmds:
                session.write('%s\n' % cmd)
                LOG.info("Telnet cmd: %s" % cmd)
                session.read_until('#', timeout=5)
            session.write('commit\n')
            session.read_until('#', timeout=5)
            session.write('save\n')
            session.read_until('#', timeout=5)
            session.close()

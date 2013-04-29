import ConfigParser
from test.ResourcePool import ResourcePool
from test.Switch import Switch
from test.TopologyReader import TopologyReader
import lib.pyshpere2 as vm_manager
from lib.pyshpere2 import CreatorException
from test.VirtualMachine import VirtualMachine


class Topology(object):
    def __init__(self, config_path, resource_pool):
        """
        Initialize a topology
        :param config_path: configuration file
        :param resource_pool: stack name for topology
        """
        try:
            self.config = TopologyReader(config_path)
            self.resource_pool = resource_pool
            self.vm_lst = self.config.get_virtual_machines()
            self.networks_lst = self.config.get_networks()
            self.manager = vm_manager.Creator(self.resource_pool,
                                              self.config.esx_login,
                                              self.config.esx_password)
        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error


    def create(self):
        try:
            # creates a resource pool for store virtual machines
            ResourcePool(self.resource_pool, self.config.esx_host).create()

            # creates networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, self.config.esx_host, net.ports)
                switch.create()
                switch.add_network(net)

            # creates virtual machines
            for vm in self.vm_lst:
                vm.create(resource_pool=self.resource_pool,
                          esx_host=self.config.esx_host)

        except CreatorException as error:
            raise error
        except ConfigParser.Error as error:
            raise error

    def destroy(self, destroy_virtual_machines=False):
        try:
            # destroys resource pool
            ResourcePool(self.resource_pool, self.config.esx_host).destroy(destroy_virtual_machines)

            # destroys networks and switches
            for net in self.networks_lst:
                if net.isolated:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool + '_' + net.name
                else:
                    switch_name = self.config.SWITCH_PREFIX + '_' + self.resource_pool

                switch = Switch(switch_name, self.config.esx_host)
                switch.destroy()

            # destroys virtual machines
            for vm in self.vm_lst:
                vm.destroy()

        except CreatorException as error:
            raise error



            ### TODO: add code with manual reconfiguration of the VM
            ### need to add part with VNC port configuration.
            ### add VNC port parameter to topology file for each VM
            # Start to work with VM using the VNC console.
            # After the base configuration for net interfaces and
            # telnet daemon switch to the telnet console
            #
            # # FIXME: change esx to vm credentials
            # # TODO: need to add vm credentials to ini-file
            # vnc_cmd(self.esx_host, vm_vnc_port, vm_login)
            # vnc_cmd(self.esx_host, vm_vnc_port, vm_password)
            # for option in vm_config:
            #     vnc_cmd(self.esx_host, vm_vnc_port, option)
            #
            # # Start to work with telnet console
            # session = None
            # while session is None:
            #     session = telnet(vm_ip_address, vm_login, vm_password)
            # conf_cmds = config.get(vm_name, 'telnet_commands').split('\n')
            # LOG.info(str(conf_cmds))
            # session.write('conf\n')
            # session.read_until('#', timeout=5)
            # for cmd in conf_cmds:
            #     session.write('%s\n' % cmd)
            #     LOG.info("Telnet cmd: %s" % cmd)
            #     session.read_until('#', timeout=5)
            # session.write('commit\n')
            # session.read_until('#', timeout=5)
            # session.write('save\n')
            # session.read_until('#', timeout=5)
            # session.close()

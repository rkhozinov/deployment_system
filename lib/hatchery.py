# This class developed for management ESXi-server using pySphere
# Main features:
# - Create/destroy virtual switch
# - Create/destroy virtual machine with specified parameters
# - Create/destroy resource pool

import pysphere
from pysphere import VIServer, VIProperty
from pysphere.resources import VimService_services as VI
from pysphere.vi_task import VITask


# An object of class Creator contain esx address and user credentials
DEFAULT_MEMORY_SIZE = 1024
DEFAULT_CPU_COUNT = 1
DEFAULT_DISK_SIZE = 1048576


class CreatorException(Exception): pass


class ExistenceException(CreatorException): pass


class Creator:
    # todo; add comment
    """

    """

    def __init__(self, manager_address, manager_user, manager_password):
        """

        :param manager_address:
        :param manager_user:
        :param manager_password:
        """
        self.esx_server = VIServer()
        self.esx_address = manager_address
        self.esx_user = manager_user
        self.esx_password = manager_password

    def __del__(self):
        self._disconnect_from_esx()

    # todo; add comment
    def _connect_to_esx(self):
        """


        :raise:
        """
        if not self.esx_server.is_connected():
            try:
                self.esx_server.connect(self.esx_address,
                                        self.esx_user, self.esx_password)
            except Exception as inst:
                raise CreatorException(str(inst))

    def _disconnect_from_esx(self):
        # todo; add comment
        """

        """
        if self.esx_server.is_connected():
            self.esx_server.disconnect()

    def create_resource_pool(self, name, parent_rp='/', esx_hostname=None,
                             cpu_resources=('normal', 4000, 0, True, -1),
                             memory_resources=('normal', 163840, 0, True, -1)):

        """
        Creates a resource pool on esx server
        name - name for new resource pool
        parent_pr - parent resource pool
        esx_hostname - host name of esx server when resource pool will be created
        cpu_resources and memory_resources: tuple
        0:share level - 'low' 'normal' 'high' 'custom'
        1:share value - 'custom' share value, int
        2:reservation - reserved CPU/Memory, int
        3:expandable reservation - bool
        4:limit - -1 - unlimited, another value - limit value, int

        :raise: CreatorException
        """
        self._connect_to_esx()

        if parent_rp == '/':
            parent_rpmor = None
            try:
                rp_mor_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                               if v == '/Resources']
            except IndexError:
                raise CreatorException("Couldn't find parent resource pool")
            if len(rp_mor_temp) == 0:
                raise CreatorException("Couldn't find parent resource pool")

            if esx_hostname:
                for rp in rp_mor_temp:
                    prop = VIProperty(self.esx_server, rp)
                    if prop.parent.name == esx_hostname:
                        parent_rpmor = rp
                        break
                if not parent_rpmor:
                    raise CreatorException("Couldn't find host")
            else:
                parent_rpmor = rp_mor_temp[0]
        else:
            parent_rp = '/Resources' + parent_rp
            parent_rpmor = None
            try:
                parent_rp_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                                  if v == parent_rp]
            except IndexError:
                raise CreatorException("Couldn't find parent a resource pool")
            if len(parent_rp_temp) == 0:
                raise CreatorException("Couldn't find parent a resource pool")
                ##222
            if len(parent_rp_temp) == 1:
                parent_rpmor = parent_rp_temp[0]
            elif esx_hostname:
                for rp in parent_rp_temp:
                    prop = VIProperty(self.esx_server, rp)
                    while prop.parent.name != "host":
                        prop = prop.parent
                        if prop.name == esx_hostname:
                            parent_rpmor = rp
                            break
            else:
                raise CreatorException("ESX Hostname must be specified")

        req = VI.CreateResourcePoolRequestMsg()
        _this = req.new__this(parent_rpmor)
        _this.set_attribute_type(parent_rpmor.get_attribute_type())
        req.set_element__this(_this)

        req.Name = name
        spec = req.new_spec()
        cpu_allocation = spec.new_cpuAllocation()
        memory_allocation = spec.new_memoryAllocation()

        #cpu allocation settings
        shares = cpu_allocation.new_shares()
        shares.Level = cpu_resources[0]
        shares.Shares = cpu_resources[1]
        cpu_allocation.Shares = shares
        cpu_allocation.Reservation = cpu_resources[2]
        cpu_allocation.ExpandableReservation = cpu_resources[3]
        cpu_allocation.Limit = cpu_resources[4]
        spec.CpuAllocation = cpu_allocation

        #memory allocation settings
        shares = memory_allocation.new_shares()
        shares.Level = memory_resources[0]
        shares.Shares = memory_resources[1]
        memory_allocation.Shares = shares
        memory_allocation.Reservation = memory_resources[2]
        memory_allocation.ExpandableReservation = memory_resources[3]
        memory_allocation.Limit = memory_resources[4]
        spec.MemoryAllocation = memory_allocation

        req.Spec = spec
        try:
            self.esx_server._proxy.CreateResourcePool(req)
        except Exception as inst:
            self._disconnect_from_esx()
            inst = str(inst)
            if "already exist" in inst:
                raise ExistenceException("Couldn't create resource pool '%s', because it already exist" % name)
            else:
                raise CreatorException("Couldn't create the resource pool with name '%s'" % name)


    def destroy_resource_pool(self, name, esx_hostname=None):
        """
        Destroy named resource pool; vm included in this pool will be thrown
        on upper resource pool
        :param esx_hostname: host name of esx server, which contains resource pool
        :param name: name of resource pool
        :raise: CreatorException, ExistenceException
        """
        self._connect_to_esx()
        if name[0] != '/':
            rp_name = '/Resources/' + name
        else:
            rp_name = '/Resources' + name

        try:
            rp_mor_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                           if v == rp_name]
        except IndexError:
            raise ExistenceException("Couldn't find resource pool '%s'" % name)

        rpmor = ''
        if esx_hostname:
            for rp in rp_mor_temp:
                prop = VIProperty(self.esx_server, rp)
                while prop.parent.name != "host":
                    prop = prop.parent
                    if prop.name == esx_hostname:
                        rpmor = rp
                        break
        elif len(rp_mor_temp) == 1:
            rpmor = rp_mor_temp[0]
        else:
            raise CreatorException("ESX Hostname must be specified")

        req = VI.Destroy_TaskRequestMsg()
        _this = req.new__this(rpmor)
        _this.set_attribute_type(rpmor.get_attribute_type())
        req.set_element__this(_this)

        try:
            self.esx_server._proxy.Destroy_Task(req)
            # self._disconnect_from_esx()
        except Exception:
            self._disconnect_from_esx()
            raise


    def destroy_resource_pool_with_vms(self, name, esx_hostname=None):
        """
        Destroy named resource pool; vm included in this pool also will be destroyed
        :param name:  name of resource pool
        :param esx_hostname: host name of esx server, which contains resource pool
        :raise: CreatorException, ExistenceException
        """
        self._connect_to_esx()

        if not name:
            raise CreatorException("Couldn't specify resource pool name")

        if name[0] != '/':
            rp_name = '/Resources/' + name
        else:
            rp_name = '/Resources' + name

        try:
            rp_mor_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                           if v == rp_name]
        except IndexError:
            raise CreatorException("Couldn't find resource pool '%s'" % name)

        rpmor = ''
        if esx_hostname:
            for rp in rp_mor_temp:
                prop = VIProperty(self.esx_server, rp)
                while prop.parent.name != "host":
                    prop = prop.parent
                    if prop.name == esx_hostname:
                        rpmor = rp
                        break
        elif len(rp_mor_temp) == 1:
            rpmor = rp_mor_temp[0]
        else:
            raise ExistenceException("Couldn't find resource pool '%s'" % name)

        prop = VIProperty(self.esx_server, rpmor)
        vms = [str(k.name) for k in prop.vm]
        for k in vms:
            self.destroy_vm(k)
        self.destroy_resource_pool(rp_name[10:], esx_hostname)

        # self._disconnect_from_esx()

    def destroy_vm(self, vmname):
        """
        Destroys virtual machine by name
        :param vmname: virtual machine name
        :raise: ExistenceException, CreatorException
        """

        self._connect_to_esx()

        try:
            vm = self.esx_server.get_vm_by_name(vmname)
        except Exception as error:
            self._disconnect_from_esx()
            raise ExistenceException("Couldn't find VM '%s' - %s" % (vmname, error.message))

        try:
            if vm.is_powered_on() or vm.is_powering_off() or vm.is_reverting():
                vm.power_off()
            request = VI.Destroy_TaskRequestMsg()
            _this = request.new__this(vm._mor)
            _this.set_attribute_type(vm._mor.get_attribute_type())
            request.set_element__this(_this)
            ret = self.esx_server._proxy.Destroy_Task(request)._returnval

            #Wait for the task to finish
            task = VITask(ret, self.esx_server)

            status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
            if status != task.STATE_SUCCESS:
                raise CreatorException("Couldn't destroy vm - " + task.get_error_message())
        except Exception:
            self._disconnect_from_esx()
            raise CreatorException("Couldn't destroy the virtual machine %s" % vmname)

    def create_vm_old(self, vmname, esx_hostname=None, iso=None, datacenter=None, resource_pool='/', networks=None,
                      datastore=None, description=None, create_hard_drive=True, guestosid="debian4Guest",
                      memorysize=512, cpucount=1, disk_space=1048576):
        """
        Creates virtual machine
        :param vmname: name of virtual machine
        :param esx_hostname: host's name, when vm will be created; if not specified
                       and ESX contains more than 1 hosts - raise CreatorException
        :param iso: path to .ISO image; must be stored in the same datastore
              as the virtual machine is created
        :param datacenter: name of datacenter, which contain hosts and datastores
        :param resource_pool: name of resource pool, when VM will be created
            (e.g. win-servers/win2003)
            if resource_pool_path is not defined, VM will created in root of inventory
        :param networks: list of existing port groups. NIC are based on this list
        :param datastore: name of datastore, which will be contain VM files; if not
            specified, VM will be placed in first datastore, which is avaliable
            for chosen host
        :param description: description for VM
        :param guestosid: ID for guest OS; full list
            http://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.vm.GuestOsDescriptor.GuestOsIdentifier.html
        :param memorysize: size of RAM, which will be avaliable on VM, in Mb
        :param cpucount: count of CPU, which will be avaliable on VM
        :param create_hard_drive: if True, new .vmdk disk will be created and added to VM
        :param disk_space: hard drive's maximal size, in Kb
        """
        params = {}

        if vmname:
            params['vm_name'] = vmname
        else:
            raise AttributeError("Couldn't specify a virtual machine name")

        if iso:
            params['iso'] = iso
        if datacenter:
            params['datacenter_name'] = datacenter
        if datastore:
            params['datastore_name'] = datastore
        if resource_pool:
            params['resource_pool_name'] = resource_pool
        if not networks:
            networks = []
        if networks:
            params['networks'] = networks
        if not description:
            params['description'] = "Description of %s" % vmname
        else:
            params['description'] = description

        params['esx_hostname'] = esx_hostname
        params['hard_drive'] = create_hard_drive
        params['guestosid'] = guestosid
        params['memory_size'] = memorysize
        params['cpu_count'] = cpucount
        params['disk_size'] = disk_space

        try:
            self.create_vm(params)
        except ExistenceException as error:
            raise
        except CreatorException as error:
            raise
        except Exception as error:
            raise

    def create_vm(self, vm_options):
        """
         Creates a virtual machine on ESXi server
        :param vm_options: dict, which contain parameters for VM
        'vm_name'
        'iso'
        'datacenter_name'
        'datastore_name'
        'resource_pool_name'
        'networks'
        'description'
        'esx_hostname'
        'hard_drive'
        'guestosid'
        'memory_size'
        'cpu_count'
        'disk_size'
        See create_vm_old for details
        :raise: CreatorException, ExistenceException
        """
        self._connect_to_esx()

        #VM NAME
        vm_name = None
        try:
            vm_name = str(vm_options['vm_name'])
            vm_temp = self.esx_server.get_vm_by_name(vm_name)
            if vm_temp:
                raise ExistenceException('VM "%s" already exists' % vm_name)
        except KeyError:
            raise CreatorException('Must specify VM name')
        except pysphere.VIException as inst:
            if '[Object Not Found]' in str(inst):
                pass

        # HOSTNAME
        hosts = self.esx_server.get_hosts()
        try:
            esx_hostname = vm_options['esx_hostname']
            if not esx_hostname in hosts.values():
                raise CreatorException("Couldn't find host '%s'" % esx_hostname)
        except KeyError:
            if len(hosts.values()) > 1:
                raise CreatorException("More than 1 host - must specify ESX Hostname")
            elif not hosts.values():
                raise CreatorException("Couldn't find available host")
            esx_hostname = hosts[0]
            # MOR and PROPERTIES
        hostmor = [k for k, v in hosts.items() if v == esx_hostname][0]
        hostprop = VIProperty(self.esx_server, hostmor)


        #DATACENTER - FIX EXCEPTION
        # todo: fix self.esx_server.get_datacenters().values()
        dcs = self.esx_server.get_datacenters()
        dc_values = dcs.values()
        try:
            dc_name = vm_options['datacenter_name']
            if not dc_name in dc_values:
                raise CreatorException("Couldn't find datacenter '%s'" + dc_name)
        except KeyError:
            if len(dc_values) > 1:
                raise CreatorException("More than 1 datacenter - must specify ESX Hostname")
            elif not dc_values:
                raise CreatorException("Couldn't find available datacenter")
            dc_name = dc_values[0]
            # MOR and PROPERTIES
        dcmor = [k for k, v in dcs.items() if v == dc_name][0]
        dcprops = VIProperty(self.esx_server, dcmor)

        #DATASTORE
        dcs = hostprop.datastore
        try:
            ds_name = vm_options['datastore_name']
            ds_list = []
            for ds in dcs:
                ds_list.append(ds.name)
            if not ds_name in ds_list:
                raise CreatorException("Couldn't find datastore or datastore is not available")
        except KeyError:
            if len(dcs) > 1:
                raise CreatorException("More than 1 datastore on ESX - must specify datastore name")
            elif not dcs:
                raise CreatorException("Couldn't find available datastore")
            ds_name = dcs[0].name

        # RESOURCE POOL
        resource_pool_name = ''
        try:
            resource_pool_name = vm_options['resource_pool_name']
            if resource_pool_name == '/':
                pass
            elif resource_pool_name[0] != '/':
                resource_pool_name = '/{0}'.format(resource_pool_name)
        except KeyError:
            resource_pool_name = '/'
        finally:
            rpmor = self._fetch_resource_pool(resource_pool_name, esx_hostname)
            if not rpmor:
                raise CreatorException("Couldn't find resource pool '%s'" % resource_pool_name)

        # NETWORKS
        try:
            networks = list(vm_options['networks'])
        except Exception:
            networks = []

        try:
            iso = vm_options['iso']
            #todo: hide magic
            iso = iso[iso.find(ds_name) + len(ds_name) + 1:]
        except KeyError:
            iso = None
        try:
            hard_drive = vm_options['hard_drive']
        except KeyError:
            hard_drive = True

        # Description
        try:
            description = vm_options['description']
        except KeyError:
            description = "Description for VM %s" % vm_name

        try:
            guestosid = vm_options['guestosid']
        except KeyError:
            guestosid = 'otherGuest'

        try:
            memory_size = int(vm_options['memory_size'])
            if memory_size <= 0:
                raise CreatorException('Disk size must be greater than 0')
        except Exception:
            memory_size = DEFAULT_MEMORY_SIZE  # MB

        try:
            cpu_count = int(vm_options['cpu_count'])
        except Exception:
            cpu_count = DEFAULT_CPU_COUNT

        try:
            disk_size = int(vm_options['disk_size'])
            if disk_size <= 0:
                raise CreatorException('Disk size must be greater than 0')
        except Exception:
            disk_size = DEFAULT_DISK_SIZE  # KB

        crprops = self._fetch_computer_resource(dcprops, hostmor)
        vmfmor = dcprops.vmFolder._obj

        #CREATE VM CONFIGURATION
        #get config target
        request = VI.QueryConfigTargetRequestMsg()
        _this = request.new__this(crprops.environmentBrowser._obj)
        _this.set_attribute_type(crprops.environmentBrowser._obj.get_attribute_type())
        request.set_element__this(_this)
        h = request.new_host(hostmor)
        h.set_attribute_type(hostmor.get_attribute_type())
        request.set_element_host(h)
        config_target = self.esx_server._proxy.QueryConfigTarget(request)._returnval

        #get default devices
        request = VI.QueryConfigOptionRequestMsg()
        _this = request.new__this(crprops.environmentBrowser._obj)
        _this.set_attribute_type(crprops.environmentBrowser._obj.get_attribute_type())
        request.set_element__this(_this)
        h = request.new_host(hostmor)
        h.set_attribute_type(hostmor.get_attribute_type())
        request.set_element_host(h)
        config_option = self.esx_server._proxy.QueryConfigOption(request)._returnval
        defaul_devs = config_option.DefaultDevice

        #get network name
        # todo: fix creating if not valid vm. Turn logging. Write message of unavailable network, but create vm
        _networks = []
        for n in config_target.Network:
            if n.Network.Accessible and networks.count(n.Network.Name):
                _networks.append(n.Network.Name)
        if len(networks) != len(_networks):
            raise CreatorException("Couldn't find all networks")
            #raise ExistenceException("Couldn't find network")


            #get datastore
        ds = None
        for d in config_target.Datastore:
            if d.Datastore.Accessible and d.Datastore.Name == ds_name:
                ds = d.Datastore.Datastore
                ds_name = d.Datastore.Name
                break
        if not ds:
            raise CreatorException("Datastore is not available")
        volume_name = "[%s]" % ds_name

        #add parameters to the create vm task
        create_vm_request = VI.CreateVM_TaskRequestMsg()
        config = create_vm_request.new_config()
        vmfiles = config.new_files()
        vmfiles.set_element_vmPathName(volume_name)
        config.set_element_files(vmfiles)
        config.set_element_name(vm_name)
        config.set_element_annotation(description)
        config.set_element_memoryMB(memory_size)
        config.set_element_numCPUs(cpu_count)
        config.set_element_guestId(guestosid)
        devices = []

        #add a scsi controller
        disk_ctrl_key = 1
        scsi_ctrl_spec = config.new_deviceChange()
        scsi_ctrl_spec.set_element_operation('add')
        scsi_ctrl = VI.ns0.VirtualLsiLogicController_Def("scsi_ctrl").pyclass()
        scsi_ctrl.set_element_busNumber(0)
        scsi_ctrl.set_element_key(disk_ctrl_key)
        scsi_ctrl.set_element_sharedBus("noSharing")
        scsi_ctrl_spec.set_element_device(scsi_ctrl)
        devices.append(scsi_ctrl_spec)

        #find ide controller
        if iso:
            ide_ctlr = None
            for dev in defaul_devs:
                if dev.typecode.type[1] == "VirtualIDEController":
                    ide_ctlr = dev
                    #add a cdrom based on a physical device
            if ide_ctlr:
                cd_spec = config.new_deviceChange()
                cd_spec.set_element_operation('add')
                cd_ctrl = VI.ns0.VirtualCdrom_Def("cd_ctrl").pyclass()
                cd_device_backing = VI.ns0.VirtualCdromIsoBackingInfo_Def("cd_device_backing").pyclass()
                ds_ref = cd_device_backing.new_datastore(ds)
                ds_ref.set_attribute_type(ds.get_attribute_type())
                cd_device_backing.set_element_datastore(ds_ref)
                cd_device_backing.set_element_fileName("%s %s" % (volume_name, iso))
                cd_ctrl.set_element_backing(cd_device_backing)
                cd_ctrl.set_element_key(20)
                cd_ctrl.set_element_controllerKey(ide_ctlr.get_element_key())
                cd_ctrl.set_element_unitNumber(0)
                cd_spec.set_element_device(cd_ctrl)
                devices.append(cd_spec)

        # create a new disk - file based - for the vm
        if hard_drive:
            disk_spec = config.new_deviceChange()
            disk_spec.set_element_fileOperation("create")
            disk_spec.set_element_operation("add")
            disk_ctlr = VI.ns0.VirtualDisk_Def("disk_ctlr").pyclass()
            disk_backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("disk_backing").pyclass()
            disk_backing.set_element_fileName(volume_name)
            disk_backing.set_element_diskMode("persistent")
            disk_ctlr.set_element_key(0)
            disk_ctlr.set_element_controllerKey(disk_ctrl_key)
            disk_ctlr.set_element_unitNumber(0)
            disk_ctlr.set_element_backing(disk_backing)
            disk_ctlr.set_element_capacityInKB(disk_size)
            disk_spec.set_element_device(disk_ctlr)
            devices.append(disk_spec)

        #add a NIC. the network Name must be set as the device name to create the NIC.
        for network_name in _networks:
            nic_spec = config.new_deviceChange()
            nic_spec.set_element_operation("add")
            nic_ctlr = VI.ns0.VirtualPCNet32_Def("nic_ctlr").pyclass()
            nic_backing = VI.ns0.VirtualEthernetCardNetworkBackingInfo_Def("nic_backing").pyclass()
            nic_backing.set_element_deviceName(network_name)
            nic_ctlr.set_element_addressType("generated")
            nic_ctlr.set_element_backing(nic_backing)
            nic_ctlr.set_element_key(4)
            nic_spec.set_element_device(nic_ctlr)
            devices.append(nic_spec)

        config.set_element_deviceChange(devices)
        create_vm_request.set_element_config(config)
        folder_mor = create_vm_request.new__this(vmfmor)
        folder_mor.set_attribute_type(vmfmor.get_attribute_type())
        create_vm_request.set_element__this(folder_mor)
        rp_mor = create_vm_request.new_pool(rpmor)
        rp_mor.set_attribute_type(rpmor.get_attribute_type())
        create_vm_request.set_element_pool(rp_mor)
        host_mor = create_vm_request.new_host(hostmor)
        host_mor.set_attribute_type(hostmor.get_attribute_type())
        create_vm_request.set_element_host(host_mor)

        #CREATE THE VM - add option "wait"
        taskmor = self.esx_server._proxy.CreateVM_Task(create_vm_request)._returnval
        task = VITask(taskmor, self.esx_server)
        task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if task.get_state() == task.STATE_ERROR:
            self._disconnect_from_esx()
            raise CreatorException("Error creating vm: %s" % task.get_error_message())


    def create_virtual_switch(self, name, num_ports, esx_hostname=None):
        """
        Creates a new standard virtual switch on esx
        :param name: name for new virtual switch
        :param num_ports: numbers of emulated ports
        :param esx_hostname: host name of esx server when virtual switch will be created
        :raise: CreatorException, ExistenceException
        """
        num_ports = int(num_ports)

        self._connect_to_esx()
        hosts = None
        try:
            hosts = self.esx_server.get_hosts()
            if esx_hostname:
                host_system = [k for k, v in hosts.items() if v == esx_hostname][0]
            else:
                host_system = hosts.keys()[0]
        except IndexError:
            raise CreatorException("Couldn't find host")
        if not host_system:
            raise CreatorException("Couldn't find host")

        prop = VIProperty(self.esx_server, host_system)
        network_system = prop.configManager.networkSystem._obj

        for vs in prop.configManager.networkSystem.networkInfo.vswitch:
            if vs.name == name:
                self._disconnect_from_esx()
                raise ExistenceException("Switch '%s' already exist" % name)

        request = VI.AddVirtualSwitchRequestMsg()
        _this = request.new__this(network_system)
        _this.set_attribute_type(network_system.get_attribute_type())
        request.set_element__this(_this)
        request.set_element_vswitchName(name)

        spec = request.new_spec()
        spec.set_element_numPorts(num_ports)
        request.set_element_spec(spec)

        try:
            self.esx_server._proxy.AddVirtualSwitch(request)
        except Exception:
            raise CreatorException("Couldn't create Switch")

        # self._disconnect_from_esx()

    def destroy_virtual_switch(self, name, esx_hostname=None):
        """
        Destroys a named standard virtual switch on esx
        :param name: virtual switch's name
        :param esx_hostname: host name of esx server when virtual switch placed
        :raise: CreatorException, ExistenceException
        """
        self._connect_to_esx()
        hosts = self.esx_server.get_hosts()
        try:
            if esx_hostname:
                host_system = [k for k, v in hosts.items()
                               if v == esx_hostname][0]
            else:
                host_system = hosts.keys()[0]
        except Exception:
            raise CreatorException("Couldn't find host")
        prop = VIProperty(self.esx_server, host_system)
        network_system = prop.configManager.networkSystem._obj

        exist = False
        for vs in prop.configManager.networkSystem.networkInfo.vswitch:
            if vs.name == name:
                exist = True
                break

        if exist:
            request = VI.RemoveVirtualSwitchRequestMsg()
            _this = request.new__this(network_system)
            _this.set_attribute_type(network_system.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_vswitchName(name)
            try:
                self.esx_server._proxy.RemoveVirtualSwitch(request)
            except Exception:
                raise CreatorException("Couldn't remove virtual switch '%s'" % name)
        else:
            raise ExistenceException("Couldn't find virtual switch '%s'" % name)
        # self._disconnect_from_esx()

    def add_port_group(self, switch_name, vlan_name, esx_hostname=None,
                       vlan_id=4095, promiscuous=False):
        """
        Add new network to exist switch

        :param switch_name: vlan_name of switch which will be reconfigured
        :param vlan_name: vlan_name of VLAN
        :param esx_hostname: ESX hostname
        :param vlan_id: id for VLAN
        :param promiscuous: promiscuous mode enable/disable (True/False)
        :raise: ExistenceException, CreatorException
        """
        self._connect_to_esx()

        vlan_id = int(vlan_id)

        hosts=self.esx_server.get_hosts()
        try:
            if esx_hostname:
                host_system = [k for k, v in hosts.items()
                               if v == esx_hostname][0]
            else:
                host_system = hosts.keys()[0]
        except Exception:
            raise CreatorException("Couldn't find host")

        prop = VIProperty(self.esx_server, host_system)
        network_system = prop.configManager.networkSystem._obj

        request = VI.AddPortGroupRequestMsg()
        _this = request.new__this(network_system)
        _this.set_attribute_type(network_system.get_attribute_type())
        request.set_element__this(_this)

        portgrp = request.new_portgrp()
        portgrp.set_element_name(vlan_name)
        portgrp.set_element_vlanId(vlan_id)
        portgrp.set_element_vswitchName(switch_name)

        policy = portgrp.new_policy()
        security = policy.new_security()
        security.set_element_allowPromiscuous(promiscuous)
        policy.set_element_security(security)
        portgrp.set_element_policy(policy)

        request.set_element_portgrp(portgrp)

        try:
            self.esx_server._proxy.AddPortGroup(request)
        except Exception as inst:
            message = str(inst)
            if 'already exist' in message:
                raise ExistenceException(
                    "Couldn't create network '%s:%s' on switch '%s', because it already exists" % vlan_name,
                    vlan_id, switch_name)
            else:
                raise CreatorException("Couldn't create network '%s:%s' on switch '%s'" % vlan_name,
                                       vlan_id, switch_name)

        # self._disconnect_from_esx()

    def is_connected(self):
        """
        Checks ESX manager connection

        :rtype : bool
        :return: connection status
        """
        return self.esx_server.is_connected()

    def vm_power_on(self, vmname):
        """
        Turns power on for the virtual machine

        :param vmname: virtual machine name
        :raise: ExistenceException, AttributeError, Exception
        """
        if not vmname:
            raise AttributeError("Couldn't specify the virtual machine name")

        if not self._is_vm_exist(vmname):
            raise ExistenceException("Couldn't find the virtual machine '%s'" % vmname)

        try:
            self._connect_to_esx()
            vm = self.esx_server.get_vm_by_name(vmname)
            if not vm.is_powered_on() and not vm.is_powering_on():
                vm.power_on()
        except Exception as error:
            self._disconnect_from_esx()
            raise CreatorException(error)

    def vm_power_off(self, vmname):
        """
        Turns power off for the virtual machine

        :param vmname: virtual machine name
        :raise: ExistenceException, AttributeError, Exception
        """
        if not vmname:
            raise AttributeError("Couldn't specify the virtual machine name")

        if not self._is_vm_exist(vmname):
            raise ExistenceException("Couldn't find the virtual machine '%s'" % vmname)

        try:
            self._connect_to_esx()
            vm = self.esx_server.get_vm_by_name(vmname)
            if not vm.is_powered_off() and not vm.is_powering_off():
                vm.power_off()
        except Exception as error:
            self._disconnect_from_esx()
            raise CreatorException(error)

    def vm_reset(self, vmname):
        """
        Resets a virtual machine.
        If the virtual machine is powered off, then turns the power on for this virtual machine
        :param vmname: virtual machine name
        :raise: AttributeError, ExistenceException, Exception
        """
        if not vmname:
            raise AttributeError("Couldn't specify the virtual machine name")

        if not self._is_vm_exist(vmname):
            raise ExistenceException("Couldn't find the virtual machine '%s'" % vmname)

        try:
            self._connect_to_esx()
            vm = self.esx_server.get_vm_by_name(vmname)
            if not vm.is_powered_off():
                vm.reset()
            else:
                vm.power_on()
        except Exception as error:
            self._disconnect_from_esx()
            raise CreatorException(error)

    def get_vm_path(self, vmname):

        """
        Gets a virtual machine path on ESX server
        :param vmname: virtual machine name
        :return: virtual machine path
        :raise: CreatorException
        """
        self._connect_to_esx()

        try:
            vm = self.esx_server.get_vm_by_name(vmname)
        except Exception:
            raise ExistenceException("Couldn't find the virtual machine '%s'" % vmname)

        try:
            return vm.get_property('path')
        except Exception as error:
            self._disconnect_from_esx()
            raise CreatorException(error)


            pass
        #todo: REVIEW ME
    def add_existence_vmdk(self, vm_name, path, space):
        """
        Add existence hard drive (.vmdk) to the virtual machine
        :param vm_name: virtual machine name
        :param path: hard drive path
        :param space: space for hard drive
        :raise: ExistenceException, CreatorException
        """
        self._connect_to_esx()
        try:
            vm = self.esx_server.get_vm_by_name(vm_name)
        except Exception:
            raise ExistenceException("Couldn't find the virtual machine %s" % vm_name)

        unit_number = 0
        for disk in vm._disks:
            unit_number = max(unit_number, disk['device']['unitNumber'])
        unit_number += 1

        request = VI.ReconfigVM_TaskRequestMsg()
        _this = request.new__this(vm._mor)
        _this.set_attribute_type(vm._mor.get_attribute_type())
        request.set_element__this(_this)

        spec = request.new_spec()

        dc = spec.new_deviceChange()
        dc.Operation = "add"

        hd = VI.ns0.VirtualDisk_Def("hd").pyclass()
        hd.Key = -100
        hd.UnitNumber = unit_number
        hd.CapacityInKB = space
        hd.ControllerKey = 1000

        backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("backing").pyclass()
        backing.FileName = path
        backing.DiskMode = "persistent"
        backing.ThinProvisioned = False
        hd.Backing = backing

        connectable = hd.new_connectable()
        connectable.StartConnected = True
        connectable.AllowGuestControl = False
        connectable.Connected = True
        hd.Connectable = connectable

        dc.Device = hd

        spec.DeviceChange = [dc]
        request.Spec = spec

        task = self.esx_server._proxy.ReconfigVM_Task(request)._returnval
        vi_task = VITask(task, self.esx_server)

        #Wait for task to finis
        status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                         vi_task.STATE_ERROR])
        if status == vi_task.STATE_ERROR:
            self._disconnect_from_esx()
            raise CreatorException("ERROR CONFIGURING VM:%s" % vi_task.get_error_message())

    # todo: add comment
    def _get_portgroup_name(self, name, esx_hostname=None):
        """
        Get exist network from ESX
        :param name: network name
        :param esx_hostname: ESX host name
        :return: :raise:
        """

        self._connect_to_esx()
        hosts = self.esx_server.get_hosts()
        try:
            if esx_hostname:
                host_system = [k for k, v in hosts.items() if v == esx_hostname][0]
            else:
                host_system = hosts.keys()[0]
        except IndexError:
            raise CreatorException("Couldn't find host")
        if not host_system:
            raise CreatorException("Couldn't find host")

        prop = VIProperty(self.esx_server, host_system)

        for pg in prop.configManager.networkSystem.networkInfo.portgroup:
            if pg.spec.name.lower() == name.lower():
                real_name = pg.spec.name
                # self._disconnect_from_esx()
                return real_name

        # self._disconnect_from_esx()
        return None


    # todo: add comment
    def _is_vm_exist(self, name):
        """

        :param name:
        :return:
        """
        self._connect_to_esx()
        exist = False
        try:
            self.esx_server.get_vm_by_name(name)
            exist = True
        except:
            pass
        # self._disconnect_from_esx()
        return exist

    # todo: add comment
    def _fetch_resource_pool(self, rp_name, esx_hostname):

        """

        :param rp_name:
        :param esx_hostname:
        :return:
        """
        rpmor = None

        if rp_name == '/':
            rp_mor_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                           if v == '/Resources']
            for rp in rp_mor_temp:
                prop = VIProperty(self.esx_server, rp)
                if prop.parent.name == esx_hostname:
                    rpmor = rp
                    break
        else:
            resource_pool = '/Resources' + rp_name

            rp_mor_temp = [k for k, v in self.esx_server.get_resource_pools().items()
                           if v == resource_pool]

            for rp in rp_mor_temp:
                prop = VIProperty(self.esx_server, rp)
                while prop.parent.name != "host":
                    prop = prop.parent
                    if prop.name == esx_hostname:
                        rpmor = rp
                        break
                if rp:
                    break

        return rpmor

    # todo: add comment
    def _fetch_computer_resource(self, datacenter_props, host):
        """

        :param datacenter_props:
        :param host:
        :return:
        """
        host_folder = datacenter_props.hostFolder._obj


        #get computer resources
        computer_resources = self.esx_server._retrieve_properties_traversal(
            property_names=['name', 'host'],
            from_node=host_folder,
            obj_type='ComputeResource')

        #get computer resource of this host
        crmor = None
        for cr in computer_resources:
            if crmor:
                break
            for p in cr.PropSet:
                if p.Name == "host":
                    for h in p.Val.get_element_ManagedObjectReference():
                        if h == host:
                            crmor = cr.Obj
                            break
                    if crmor:
                        break
        return VIProperty(self.esx_server, crmor)



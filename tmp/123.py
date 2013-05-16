from Hatchery import Creator as Manager
from Hatchery import CreatorException

serial_file_name = 'serial'
params = {'vm_name' : 'test_serial_port', 'esx_hostname' : '172.18.93.30',
            'resource_pool' : 'vkhlyunev'}

mgr = Manager('172.18.93.40','root','vmware')

#mgr.destroy_vm(params['vm_name'])
mgr.create_vm(params)
mgr._connect_to_esx()
vm = mgr.esx_server.get_vm_by_name(params['vm_name'])
path = vm.get_property('path')
path_temp = path.split(' ')
datastore = path_temp[0][1:-1]
vm_folder = path_temp[1].split('/')[0]
way_to_serial = '/vmfs/volumes/' + datastore + '/' + vm_folder + '/' + serial_file_name
way_to_vmx = '/vmfs/volumes/' + datastore + '/' + path_temp[1]


commands = []
commands.append('touch ' + way_to_serial)
commands.append('sed -i \'$ a serial0.present = "TRUE"\' ' + way_to_vmx)
commands.append('sed -i \'$ a serial0.yieldOnMsrRead = "TRUE" \' ' + way_to_vmx)
commands.append('sed -i \'$ a serial0.fileType = "pipe" \' ' + way_to_vmx)
commands.append('sed -i \'$ a serial0.fileName = \"' + way_to_serial + '\" \' ' + way_to_vmx)
commands.append('sed -i \'$ a serial0.pipe.endPoint = "server" \' ' + way_to_vmx)



for cmd in commands:
    print cmd

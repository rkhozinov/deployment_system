import cProfile

import lib.Hatchery as Manager


__author__ = 'rkhozinov'


class Box(object):
    host_name = '172.18.93.30'
    manager_address = '172.18.93.40'
    manager_user = 'root'
    manager_password = 'vmware'
    rpname = 'test_pool2'
    vmname = 'test_vm'
    switch_name = 'test_switch'
    vlan_name = 'test_net'
    vlan_id = 1515
    switch_name = 'test_switch'
    switch_ports = 8
    manager = Manager.Creator(manager_address,
                              manager_user,
                              manager_password)


pr = cProfile.Profile(subcalls=False, builtins=False)
pr2 = cProfile.Profile(subcalls=False, builtins=False)
try:
    try:
        pr.enable()
        Box.manager.destroy_virtual_switch(name=Box.switch_name,
                                           esx_hostname=Box.host_name)
    except Manager.ExistenceException:
        pass
    pr.disable()
    pr.create_stats()
    pr.print_stats()
    try:
        pr2.enable()
        Box.manager.create_virtual_switch(name=Box.switch_name,
                                          num_ports=Box.switch_ports,
                                          esx_hostname=Box.host_name)
    except Manager.ExistenceException:
        pass
    pr2.disable()
    pr2.create_stats()
    pr2.print_stats()

except Manager.CreatorException as error:
    print error.message


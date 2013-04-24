import os
import sys
import logging
import time
#import xlrd        # for work with the XLS files
import re
import ConfigParser
from pysphere import VIServer

lib_path = os.path.abspath('./')
sys.path.append(lib_path)
from lib.console import *
#from lib.TestLinkClient import *

LOG = logging.getLogger(__name__)
logging.basicConfig()
LOG.setLevel(logging.INFO)


def deploy(data_file, iso_file=''):
    config = ConfigParser.RawConfigParser()
    config.read(data_file)
    esx_ip = config.get('esx', 'ip')
    esx_user = config.get('esx', 'user')
    esx_pass = config.get('esx', 'password')
    esx_folder = config.get('esx', 'folder')
    esx_iso = config.get('esx', 'iso')
    ftp_ip = config.get('ftp', 'ip')
    ftp_user = config.get('ftp', 'user')
    ftp_pass = config.get('ftp', 'password')
    ftp_folder = config.get('ftp', 'folder')
    vnc_ip = config.get('vnc', 'ip')
    vnc_user = config.get('vnc', 'user')
    vnc_pass = config.get('vnc', 'password')
    # Search ISO file with latest build on the FTP server
    session = ssh_connect(ftp_ip, ftp_user, ftp_pass)
    res = remote_exec(session, 'ls -tlr ' + ftp_folder)
    result = None
    for line in res.splitlines():
        result = line
    session.close()
    if iso_file == '':
        build = re.search('(\S+).iso', result).group()
    else:
        build = iso_file
    LOG.info(build)

    #test_plan_id = "300"   # to determine this ID please see
    #
    #create_new_build(test_plan_id, build)

    # Connect to the ESX server and start to work with virtual machines
    esx_server = VIServer()
    esx_server.connect(esx_ip, esx_user, esx_pass)

    # Shutdown all Virtual Machines
    vm_list = config.get('hosts', 'list').split('\n')
    for vm_name in vm_list:
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        LOG.info("Revert to initial state for the virtual machine " + vm_name)
        try:
            vm.revert_to_named_snapshot("init")
        except:
            LOG.error("Can not revert to the snapshot.")

        LOG.info("Start to shutdown the virtual machine " + vm_name)
        try:
            vm.power_off()
        except:
            LOG.error("Can not shutdown the Virtual Machine.")

    # Remove old build from the ESX server
    session = ssh_connect(esx_ip, esx_user, esx_pass)
    res = remote_exec(session, 'rm ' + esx_folder + esx_iso)
    session.close()

    # Download ISO file to the ESX server
    session = ssh_connect(ftp_ip, ftp_user, ftp_pass)
    res = remote_exec(session, "sshpass -p '%s' scp %s%s"
                               " %s@%s:%s%s"
                               % (esx_pass, ftp_folder, str(build),
                                  esx_user, esx_ip, esx_folder, esx_iso))
    print ("sshpass -p '%s' scp %s%s"
           " %s@%s:%s%s"
           % (esx_pass, ftp_folder, str(build),
              esx_user, esx_ip, esx_folder, esx_iso))
    session.close()

    session = ssh_connect(esx_ip, esx_user, esx_pass)
    res = remote_exec(session, 'chmod 777 ' + esx_folder + esx_iso)
    session.close()

    # Start the Virtual Machines with a new ISO
    for vm_name in vm_list:
        LOG.info("Start to deploy the virtual machine " + vm_name)
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        try:
            vm.power_on()
        except:
            LOG.error("Can not start the Virtual Machine.")

    # sleep for a 60 seconds (for start VM from live CD)
    time.sleep(90)

    # start to configure Virtual Machines
    for vm_name in vm_list:
        vm_vnc_port = int(config.get(vm_name, 'vnc_port'))
        login = config.get(vm_name, 'user')
        password = config.get(vm_name, 'password')
        vm_ip_address = config.get(vm_name, 'ip')
        vm_ip_mask = config.get(vm_name, 'mask')
        vm_gw = config.get(vm_name, 'gw')

        LOG.info("Start to configure the virtual machine " + vm_name)

        # Start to work with VM using the VNC console.
        # After the base configuration for net interfaces and
        # telnet daemon switch to the telnet console
        run_vnc_command(esx_ip, vm_vnc_port, login)
        run_vnc_command(esx_ip, vm_vnc_port, password)
        run_vnc_command(esx_ip, vm_vnc_port, 'conf')
        config_str = 'se i e eth0 a ' + vm_ip_address + vm_ip_mask
        run_vnc_command(esx_ip, vm_vnc_port, config_str)
        config_str = 'se pr s route 0.0.0.0/0 n ' + vm_gw
        run_vnc_command(esx_ip, vm_vnc_port, config_str)
        config_str = 'se se t l ' + vm_ip_address
        run_vnc_command(esx_ip, vm_vnc_port, config_str)
        run_vnc_command(esx_ip, vm_vnc_port, 'commit')
        run_vnc_command(esx_ip, vm_vnc_port, 'save')
        run_vnc_command(esx_ip, vm_vnc_port, 'exit')

        # Start to work with telnet console
        session = None
        while session is None:
            session = get_telnet(vm_ip_address, login, password)
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

        LOG.info("Save state of VM after configuration... " + vm_name)
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        try:
            vm.delete_current_snapshot()
            vm.create_snapshot("init")
        except:
            LOG.error("Can not create the snapshot.")

    LOG.info('Finish')


def deploy_and_install(data_file, iso_file=''):
    config = ConfigParser.RawConfigParser()
    config.read(data_file)
    esx_ip = config.get('esx', 'ip')
    esx_user = config.get('esx', 'user')
    esx_pass = config.get('esx', 'password')
    esx_folder = config.get('esx', 'folder')
    esx_iso = config.get('esx', 'iso')
    ftp_ip = config.get('ftp', 'ip')
    ftp_user = config.get('ftp', 'user')
    ftp_pass = config.get('ftp', 'password')
    ftp_folder = config.get('ftp', 'folder')

    # Search ISO file with latest build on the FTP server
    session = ssh_connect(ftp_ip, ftp_user, ftp_pass)
    res = remote_exec(session, 'ls -tlr ' + ftp_folder)
    result = None
    for line in res.splitlines():
        result = line
    session.close()
    if iso_file == '':
        build = re.search('(\S+).iso', result).group()
    else:
        build = iso_file
    LOG.info(build)

    #test_plan_id = "300"   # to determine this ID please see
    #
    #create_new_build(test_plan_id, build)

    # Connect to the ESX server and start to work with virtual machines
    esx_server = VIServer()
    esx_server.connect(esx_ip, esx_user, esx_pass)

    # Shutdown all Virtual Machines
    vm_list = config.get('hosts', 'list').split('\n')
    for vm_name in vm_list:
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        LOG.info("Revert to initial state for the virtual machine " + vm_name)
        try:
            vm.revert_to_named_snapshot("init")
        except:
            LOG.error("Can not revert to the snapshot.")

        LOG.info("Start to shutdown the virtual machine " + vm_name)
        try:
            vm.power_off()
        except:
            LOG.error("Can not shutdown the Virtual Machine.")

    # Remove old build from the ESX server
    session = ssh_connect(esx_ip, esx_user, esx_pass)
    res = remote_exec(session, 'rm ' + esx_folder + esx_iso)
    session.close()

    # Download ISO file to the ESX server
    session = ssh_connect(ftp_ip, ftp_user, ftp_pass)
    res = remote_exec(session, "sshpass -p '%s' scp %s%s"
                               " %s@%s:%s%s"
                               % (esx_pass, ftp_folder, str(build),
                                  esx_user, esx_ip, esx_folder, esx_iso))
    session.close()

    session = ssh_connect(esx_ip, esx_user, esx_pass)
    res = remote_exec(session, 'chmod 777 ' + esx_folder + esx_iso)
    session.close()

    # Start the Virtual Machines with a new ISO
    for vm_name in vm_list:
        LOG.info("Set CD-ROM status for " + vm_name + " is CONNECTED")

        session = ssh_connect(esx_ip, esx_user, esx_pass)
        res = remote_exec(session,
                          'sed -i \'s/ide1:0.startConnected = "FALSE"/ide1:0.startConnected = "TRUE"/\' /vmfs/volumes/datastore1/' + vm_name + '/' + vm_name + '.vmx')
        session.close()

        LOG.info("Start Virtual Machine " + vm_name)
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        try:
            vm.power_on()
        except:
            LOG.error("Can not start the Virtual Machine.")

    # sleep for a 90 seconds (for start VM from live CD)
    time.sleep(90)

    # start to configure Virtual Machines
    for vm_name in vm_list:
        vm_vnc_port = int(config.get(vm_name, 'vnc_port'))
        login = config.get(vm_name, 'user')
        password = config.get(vm_name, 'password')
        vm_ip_address = config.get(vm_name, 'ip')
        vm_ip_mask = config.get(vm_name, 'mask')
        vm_gw = config.get(vm_name, 'gw')

        LOG.info("Start to install the virtual machine " + vm_name)

        # Start to work with VM using the VNC console.
        # Install (Upgrade) system
        run_vnc_command(
            esx_ip, vm_vnc_port, login)
        time.sleep(2)
        run_vnc_command(
            esx_ip, vm_vnc_port, password)
        run_vnc_command(
            esx_ip, vm_vnc_port, 'install system')
        #Would you like to continue ?
        run_vnc_command(
            esx_ip, vm_vnc_port, 'yes')
        time.sleep(3)
        #Partition
        run_vnc_command(
            esx_ip, vm_vnc_port, 'auto')
        time.sleep(2)
        #Install the image on ?
        run_vnc_command(
            esx_ip, vm_vnc_port, 'sda')
        time.sleep(2)
        #This destroy all data... Continue ?
        run_vnc_command(
            esx_ip, vm_vnc_port, 'yes')
        time.sleep(2)
        #/dev/sda has old configuration... save ?
        run_vnc_command(
            esx_ip, vm_vnc_port, 'no')
        time.sleep(2)
        #Would you like to keep ssh keys on new install ?
        run_vnc_command(
            esx_ip, vm_vnc_port, 'no')
        time.sleep(10)
        #How big of a root partition should I create ?
        run_vnc_command(
            esx_ip, vm_vnc_port, ' ')
        time.sleep(40)
        #Which I should copy to sda ?
        run_vnc_command(
            esx_ip, vm_vnc_port, ' ')
        time.sleep(2)
        #Enter password for user vyatta
        run_vnc_command(
            esx_ip, vm_vnc_port, password)
        time.sleep(2)
        #Retype password for user vyatta
        run_vnc_command(
            esx_ip, vm_vnc_port, password)
        time.sleep(2)
        #Which drive should GRUB modify the boot pertition on ?
        run_vnc_command(
            esx_ip, vm_vnc_port, ' ')
        time.sleep(3)

        LOG.info("Start to shutdown the virtual machine " + vm_name)
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")
        try:
            vm.power_off()
        except:
            LOG.error("Can not shutdown the Virtual Machine.")

        time.sleep(10)

        LOG.info("Set CD-ROM status for " + vm_name + " is NOT CONNECTED")

        session = ssh_connect(esx_ip, esx_user, esx_pass)
        res = remote_exec(session,
                          'sed -i \'s/ide1:0.startConnected = "TRUE"/ide1:0.startConnected = "FALSE"/\' /vmfs/volumes/datastore1/' + vm_name + '/' + vm_name + '.vmx')
        session.close()

        time.sleep(3)

        LOG.info("Start Virtual Machine " + vm_name)
        try:
            vm.power_on()
        except:
            LOG.error("Can not start the Virtual Machine.")

            # sleep for a 90 seconds (for start VM)
            #time.sleep(90)

    for vm_name in vm_list:
        vm_vnc_port = int(config.get(vm_name, 'vnc_port'))
        login = config.get(vm_name, 'user')
        password = config.get(vm_name, 'password')
        vm_ip_address = config.get(vm_name, 'ip')
        vm_ip_mask = config.get(vm_name, 'mask')
        vm_gw = config.get(vm_name, 'gw')

        LOG.info("Start to configure the virtual machine " + vm_name)

        # Start to work with VM using the VNC console.
        # Configure the system
        run_vnc_command(
            esx_ip, vm_vnc_port, login)
        time.sleep(2)
        run_vnc_command(
            esx_ip, vm_vnc_port, password)
        run_vnc_command(
            esx_ip, vm_vnc_port, 'conf')
        config_str = 'se i e eth0 a ' + vm_ip_address + vm_ip_mask
        run_vnc_command(
            esx_ip, vm_vnc_port, config_str)
        config_str = 'se pr s route 0.0.0.0/0 n ' + vm_gw
        run_vnc_command(
            esx_ip, vm_vnc_port, config_str)
        config_str = 'se se t l ' + vm_ip_address
        run_vnc_command(
            esx_ip, vm_vnc_port, config_str)
        run_vnc_command(
            esx_ip, vm_vnc_port, 'commit')
        run_vnc_command(
            esx_ip, vm_vnc_port, 'save')
        run_vnc_command(
            esx_ip, vm_vnc_port, 'exit')

        # Start to work with telnet console
        session = None
        while session is None:
            session = get_telnet(vm_ip_address, login, password)
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

        LOG.info("Save state of VM after configuration... " + vm_name)
        try:
            vm = esx_server.get_vm_by_name(vm_name)
        except:
            LOG.error("Can not find the Virtual Machine on the ESX server!")

        try:
            vm.delete_current_snapshot()
            vm.create_snapshot("init")
        except:
            LOG.error("Can not create the snapshot.")

    LOG.info('Finish')

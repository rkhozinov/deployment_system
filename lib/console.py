import paramiko
import logging
import subprocess
import os
import telnetlib
import time

LOG = logging.getLogger(__name__)
logging.basicConfig()
LOG.setLevel(logging.INFO)


def ssh_connect(server, user, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_con = ssh.connect(server, username=user, password=password)
        return ssh
    except paramiko.AuthenticationException:
        LOG.error('Authentication failed')
        ssh.close()
        return None


def remote_exec(ssh, cmd, ignore_output=False):
    # This function allow to execute commands via SSH
    # on the remote host
    #LOG.info('Exec command via SSH: ' + cmd)
    try:
        (stdin, stdout, stderr) = ssh.exec_command(cmd)
    except:
        LOG.error('Error during exec command')
        return ''
    if ignore_output is True:
        return ''
    else:
        result = ''
        for line in stdout.read().splitlines():
            result += line + '\n'
        for line in stderr.read().splitlines():
            result += line + '\n'
        #LOG.info('ssh remote execute out:%s' % result)
        return result


def get_telnet(host, user, password):
    # This function returns the telnet session instance.
    session = None
    LOG.info("Start to connect to test host via telnet")
    try:
        session = telnetlib.Telnet(host, timeout=5)
        session.read_until('login:')
        session.write(user + '\n')
        session.read_until('Password:')
        session.write(password + '\n')
        session.read_until('$')
    except:
        LOG.error("Can not login to the host " + host)

    return session


def run_vnc_command(vm_host, port, command):
    # This function allow to use VNC util
    # to send keys to the VNC console
    # of the virtual machine
    vncdotool = False
    path = os.environ['PATH']
    for dir in path.split(os.pathsep):
        binpath = os.path.join(dir, 'vncdotool')
        if os.path.exists(binpath):
            vncdotool = True
    if not vncdotool:
        raise Exception("You want working with VNC, but vncdotool not found !")
    cmd = ['vncdotool', '-s', vm_host + '::' + str(port)]
    for i in str(command):
        if i == '@':
            ncmd = ['key', 'shift-2']
            subprocess.check_output(cmd+ncmd)
        elif i == ' ':
            ncmd = ['type', ' ']
            subprocess.check_output(cmd + ncmd)
        elif i == ':':
            ncmd = ['key', 'shift-']
            subprocess.check_output(cmd + ncmd)
        else:
            ncmd = ['type', i]
            subprocess.check_output(cmd + ncmd)
            if i == i.upper() and i != i.lower():
                time.sleep(0.5)
                ncmd = ['key', 'caplk']
                subprocess.check_output(cmd + ncmd)
        time.sleep(0.1)
    ncmd2 = ['key', 'enter']
    subprocess.check_output(cmd + ncmd2)

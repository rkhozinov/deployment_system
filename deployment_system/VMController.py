__author__ = 'Administrator'
from lib.ssh import RemoteControl


class VMController(object):
    def __init__(self, vm, esx_host, esx_login, esx_password):
        # TODO: VMController creation
        self.vm = vm
        self.esx_session = RemoteControl(esx_host, esx_login, esx_password)
        self.vm_session = None
        self.vm_session_closed = True

    def __connect(self):
        self.esx_session.open()
        if self.vm_session_closed:
            cmd = "nc -U " + self.vm.serial_port_path
            self.esx_session.perform(cmd)

    def cmd(self, command):
        pass

    def __del__(self):
        self.esx_session.close()
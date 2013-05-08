__author__ = 'Administrator'
import pexpect
import logging

class VMController(object):
    def __init__(self, vm, esx_host, esx_login, esx_password):
        # TODO: VMController creation
        self.vm = vm
        self.esx_session = pexpect.spawn

        self.vm_session = None
        self.vm_session_closed = True

        self.log = logging.getLogger(__name__)
        logging.basicConfig()


def __connect(self, esx_host, esx_login, esx_password):
    connect_str = 'ssh %s@%s' % (esx_login, esx_host)
    try:
        return pexpect.spawn(connect_str)
    except pexpect.ExceptionPexpect as error:
        self.log.cr
        raise error


def cmd(self, command):
    pass


def __del__(self):
    self.esx_session.close()
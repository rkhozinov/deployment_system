__author__ = 'Administrator'
import logging
import os

import pexpect


class VMController(object):
    def __init__(self, vm, esx_host, esx_login, esx_password):
        # TODO: VMController creation
        self.vm = vm
        self.log = logging.getLogger(__name__)
        logging.basicConfig()
        self.esx_session = None

        try:
            self.esx_session = self.__connect_to_esx(esx_host, esx_login, esx_password)
            self.vm_session = self.__connect_to_vm()
        except pexpect.ExceptionPexpect as error:
            raise error
        except Exception as error:
            raise error

    def __connect_to_esx(self, esx_host, esx_login, esx_password):
        try:
            # connection_str = 'ssh %s@%s' % (esx_login, esx_host)
            #
            # session = pexpect.spawn(connection_str)
            # session.expect('.*assword:')
            # self.log.info(session.after)
            #
            # self.cmd(esx_password, expect='.*\#')

            child = pexpect.spawn("ssh root@172.18.93.30")
            child.expect(".*assword:")
            self.log.info('Before: %s \n Command: %s \n After: %s' %
                          (child.before, '', child.after))

            child.sendline("swordfish")
            child.expect(".*\# ")
            self.log.info('Before: %s \n Command: %s \n After: %s' %
                          (child.before, '', child.after))

            return child
        except pexpect.ExceptionPexpect as error:
            raise error


    def __connect_to_vm(self):
        try:
            # TODO: check work with path
            # TODO: add to vm a vm_path or get_path()

            connection_str = 'nc -U ' + os.path.normpath(self.vm.path + self.vm.name)

            self.cmd(connection_str + '\n', expect='.*ogin:')
            self.cmd(self.vm.login, expect='.*assword:')
            self.cmd(self.vm.password, expect='.*:')

        except pexpect.ExceptionPexpect as error:
            raise error


    def cmd(self, command, expect=None):
        try:
            self.esx_session.sendline(command)
            self.esx_session.expect(expect)
            self.log.info('Before: %s \n Command: %s \n After: %s' %
                          (self.esx_session.before, command, self.esx_session.after))
        except pexpect.ExceptionPexpect as error:
            raise error

    def configure(self, configuration=None):
        if not configuration:
            configuration = self.vm.configuration
        try:
            #TODO: need to use 'expect' for each option
            for option in configuration:
                self.cmd(option)

        except pexpect.ExceptionPexpect as error:
            self.log.critical(error.message)
            raise error

    def __del__(self):
        self.esx_session.close(force=True)
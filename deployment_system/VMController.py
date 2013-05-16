__author__ = 'Administrator'
import logging

import pexpect


class VMController(object):
    def __init__(self, vm, host_address, host_user, host_password):
        """
        Controller for configure the virtual machine
        :param vm: VirtualMachine instance
        :param host_address: esx host address
        :param host_user:  esx user
        :param host_password: esx password
        :raise: pexpect.ExceptionPexpect, Exception
        """
        self.vm = vm
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()
        self.esx_session = None

        try:
            self.esx_session = self.__connect_to_host(host_address, host_user, host_password)
            self.vm_session = self.__connect_to_vm()
        except pexpect.ExceptionPexpect as error:
            raise error
        except Exception as error:
            raise error

    def __connect_to_host(self, host_address, host_user, host_password):
        """
        Connects to ESX host for configure virtual machine
        :param host_address:
        :param host_user:
        :param host_password:
        :return: :raise:
        """
        try:
            connection_str = 'ssh %s@%s' % (host_user, host_address)

            # session = pexpect.spawn(connection_str)
            # session.expect('.*assword:')
            # self.logger.info(session.after)
            #
            # self.cmd(host_password, expect='.*\#')

            child = pexpect.spawn(connection_str)
            child.expect(".*assword:")
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                          (child.before, '', child.after))

            child.sendline("swordfish")
            child.expect(".*\# ")
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                          (child.before, '', child.after))

            return child
        except pexpect.ExceptionPexpect as error:
            raise error


    def __connect_to_vm(self):
        try:
            #connection_str = 'nc -U ' + os.path.normpath(self.vm.path + self.vm.name)
            connection_str = 'nc -U /vmfs/volumes/datastore1/%s/%s' % ( self.vm.name, self.vm.name)

            self.cmd(connection_str + '\n', expect='.*ogin:')
            self.cmd(self.vm.login, expect='.*assword:')
            self.cmd(self.vm.password, expect='.*:')

        except pexpect.ExceptionPexpect as error:
            raise error

    def cmd(self, command, expect=None):
        try:
            self.esx_session.sendline(command)
            self.esx_session.expect(expect)
            self.logger.info('Before: %s \n Command: %s \n After: %s' %
                          (self.esx_session.before, command, self.esx_session.after))
        except pexpect.ExceptionPexpect as error:
            raise error

    def configure(self, configuration=None):
        if not configuration:
            configuration = self.vm.configuration
        try:
            for option in configuration:
                self.cmd(option)

        except pexpect.ExceptionPexpect as error:
            self.logger.critical(error.message)
            raise error

    def __del__(self):
        self.esx_session.close(force=True)
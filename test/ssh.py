import paramiko
import logging

LOG = logging.getLogger(__name__)
logging.getLogger("paramiko").setLevel(logging.DEBUG)


class RemoteControl(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.closed = True

    def open(self):
        if self.closed:
            self._ssh.connect(self.host, username=self.user,
                              password=self.password)
            self.closed = False

    def close(self):
        if not self.closed:
            self._ssh.close()
            self.closed = True

    def perform(self, command):
        self.open()
        LOG.debug('performing command: {0}'.format(command))
        stdout, stderr = self._ssh.exec_command(command)[1:]
        status = stdout.channel.recv_exit_status()
        out = stdout.read()
        err = stderr.read()
        LOG.debug('command exit status: {0}, stdout: {1}, stderr: {2}'
                  .format(status, out, err))

        return status, out, err

    def get_file(self, remote_path, local_path):
        self.open()
        LOG.debug('Copying remote file {0} to local {1}'.format(remote_path,
                                                                local_path))
        sftp = self._ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return True

    def put_file(self, local_path, remote_path):
        self.open()

        LOG.debug('Copying local file {0} to remote {1}'.format(local_path,
                                                                remote_path))
        sftp = self._ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True

    def close(self):
        self._ssh.close()
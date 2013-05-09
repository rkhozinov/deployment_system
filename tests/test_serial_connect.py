import thread

__author__ = 'Administrator'

from lib.ssh import RemoteControl
import paramiko

esx_host = '172.18.93.30'
esx_password = 'swordfish'
esx_login = 'root'


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(esx_host, 22, esx_login, esx_password,allow_agent=False,)


stdin, stdout, stderr = client.exec_command('nc -U /vmfs/volumes/datastore1/pipe_client/pipe_client', get_pty=True)
print stderr.readlines()
print stdout.readlines()

stdin, stdout, stderr = client.exec_command('vyatta')
print stderr.readlines()
print stdout.readlines()

stdin, stdout, stderr = client.exec_command('vyatta')
print stderr.readlines()
print stdout.readlines()

client.close()



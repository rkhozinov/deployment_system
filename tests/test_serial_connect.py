import thread

__author__ = 'Administrator'

from lib.ssh import RemoteControl
import paramiko

esx_host = '172.18.93.30'
esx_password = 'swordfish'
esx_login = 'root'

# session = RemoteControl(esx_host, esx_login, esx_password)
#
# cmd = "nc -U /vmfs/volumes/datastore1/pipe_client/pipe_client"
#
#
# print session.perform(cmd)
# print session.perform('vyatta')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(esx_host, 22, esx_login, esx_password)
stdin, stdout, stderr = client.exec_command("nc -U /vmfs/volumes/datastore1/pipe_client/pipe_client",get_pty=True)

print stdout.read()
print stderr.read()

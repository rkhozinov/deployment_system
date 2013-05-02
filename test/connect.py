__author__ = 'Administrator'

from lib.ssh import RemoteControl

esx_host = '172.18.93.30'
esx_password = 'swordfish'
esx_login = 'root'

session = RemoteControl(esx_host, esx_login, esx_password)

cmd = "nc -U /vfms/volumes/datastore1/pipe_client/pipe_client"
print session.perform(cmd)
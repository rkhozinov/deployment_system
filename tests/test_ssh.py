
import pexpect


child = pexpect.spawn("ssh root@172.18.93.30")
child.expect(".*assword:")
print child.after

child.sendline("swordfish\r")
child.expect(".*\# ")
print(child.after)

child.sendline("ls\r")
child.expect(".*\# ")
print(child.after)

child.sendline('nc -U /vmfs/volumes/datastore1/pipe_client/pipe_client\r\n')
child.expect(".*ogin:")
print(child.after)

# child.timeout=10
child.sendline('vyatta')
child.expect(".*assword:")
print(child.after)

child.sendline('vyatta')
child.expect(".*:")
print(child.after)

child.sendline('configure')
child.expect(".*\#")
print(child.after)

child.sendline('set int eth eth0 address 192.168.26.1/24')
child.expect(".*\#")
print(child.after)

child.sendline('commit')
child.expect(".*\#")
print(child.after)

child.sendline('save')
child.expect(".*#")
print(child.after)

child.sendline('exit')
child.expect(".*:")
print(child.after)


child.sendline('show int')
child.expect(".*:")
print(child.after)


child.sendline('exit')
# child.expect(pexpect.EOF)
child.sendintr()
child.close(force=True)



__author__ = 'rkhozinov'

# connect to ESX host
import pexpect

child = None
password = 'swordfish'
try:
    child = pexpect.spawn("ssh %s@%s" % ('root', '172.18.93.30'))
    child.expect(".*assword:")
    child.sendline(password)
    child.expect(".*\# ", timeout=2)
    child.sendline('ls')
    child.expect(".*\# ")
    child.sendline('touch file1')
    child.sendline('touch file2')

    print '------------------'
    print(child.after)
    child.close()
except Exception as error:
    raise
# child.sendline('ls')
# child.expect(".*\# ")

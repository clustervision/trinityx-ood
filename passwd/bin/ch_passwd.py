import sys
import pexpect  # <---- ADD TO REQUIRMENTS

#cur_password = 'BLAATblaat123'
#new_password = 'admin--------ADMIN1234##'
#cur_password = 'admin--------ADMIN1234##'
#new_password = 'admin'

# cur_password and new_password to be provided through GUI

child = pexpect.spawnu('/usr/bin/passwd')
child.expect('[Cc]urrent [Pp]assword:.*')
child.sendline(cur_password)
ret = child.expect(['.*[Nn]ew password:.*', '[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
if ret > 0:
    print(f"{child.after}")
    sys.exit(1)
child.sendline(new_password)
child.expect(['[Rr]etype [Nn]ew [Pp]assword:.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
child.sendline(new_password)
ret = child.expect(['.*[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
if ret == 0:
    print(f"{child.after}")
    sys.exit(1)
if ret > 0:
    print("Password not changed due to unexpected EOF or timeout")
    sys.exit(1)
child.sendline(new_password)
ret = child.expect(['all authentication tokens updated successfully', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
if ret == 0:
    print("password change successfull")
    sys.stdout.flush()
    sys.exit(0)
print("Password not changed due to unexpected EOF or timeout")

sys.stdout.flush()
child.interact()
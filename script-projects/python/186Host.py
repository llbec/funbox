#!/usr/bin/python
import pexpect, os, sys, argparse

class Host :
    def __init__(self, subnet, user, passwd, port) :
        self.subnet = subnet
        self.user = user
        self.passwd = passwd
        self.port = port
    
    def Ip(self) :
        return '10.186.11.%s'%(self.subnet)
    
    def LoginWord(self) :
        return 'ssh -p %d %s@%s'%(self.port, self.user, self.Ip())
    
    """def Session(self) :
        ssh = pexpect.spawn(self.LoginWord())
        iret = ssh.expect([".*password.*", ".*continue.*?", 'Last login.*', pexpect.EOF, pexpect.TIMEOUT], timeout = 3)"""
    
g_Parser = argparse.ArgumentParser("SSH login host 10.186.11.x")
#g_Parser.add_argument('IP subnet', metavar='Subnet', type=str, nargs='+', help='the subnet value of the 10.186.11. ')
g_Parser.add_argument('subnet', metavar='Subnet', type=int, help='the subnet value of the 10.186.11. ')
g_Parser.add_argument('-u', '--usr', type=str, default='root', metavar='', help='ssh usr name, default is root')
g_Parser.add_argument('-p', '--port', type=int, default=22, metavar='', help='ssh port, default is 22')
g_Parser.add_argument('-s', '--passwd', type=str, default='Zxcvbn2018', metavar='', help='usr\'s password, default is Zxcvbn2018')

falgs = g_Parser.parse_args()
print('%d,%s,%d,%s'%(falgs.subnet, falgs.usr, falgs.port, falgs.passwd))
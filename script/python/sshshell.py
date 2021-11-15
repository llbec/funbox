#!/usr/bin/python

import pexpect
import os
import socket
import re
import sys
from enum import Enum


def localCmd(_cmd):
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data


expectRet = [
    '.*assword.*',
    'Last login.*',
    '.*verification code sent to your mobile phone.*',
    'Permission denied',
    '.*continue.*?',
    'Welcome to Ubuntu.*',
    '.*MFA auth.*',
    pexpect.EOF,
    pexpect.TIMEOUT,
]


class switchLoginExpect:
    def __init__(self, s, h):
        self.list = {
            # 'password'
            0: self.password,
            # 'success'
            1: self.success,
            # 'ali-verifycode'
            2: self.ali_verification,
            # 'permission'
            3: self.denied,
            # 'continue'
            4: self.sendYes,
            # 'welcome'
            5: self.success,
            # 'jumpserver-auth'
            6: self.xl_jumpserver_auth
        }
        self.timelimit = 10
        self.ssh = s
        self.host = h
        #function = self.list.get(expt, self.default)
        # function()

    def switch(self, expt):
        # print(expt)
        func = self.list.get(expt, self.default)
        return func()

    def Run(self):
        while True:
            _r = self.switch(self.ssh.expect(
                expectRet, timeout=self.timelimit))
            if _r == 0:
                continue
            elif _r > 0:
                return self.ssh
            return None

    def default(self):
        print(self.ssh.before)
        print(self.ssh.after)
        #self.err = self.ssh.after
        return -1

    def password(self):
        print("send password")
        self.ssh.sendline(self.host.passwd)
        _swt = switchLoginExpect(self.ssh, self.host)
        return _swt.switch(self.ssh.expect(expectRet, timeout=self.timelimit))

    def sendYes(self):
        print('send yes')
        self.ssh.sendline('yes\n')
        return 0

    def success(self):
        print(self.ssh.before)
        return 1

    def ali_verification(self):
        _vfcode = input(
            '\r\nPlease enter the verification code sent to your mobile phone:')
        self.ssh.sendline(_vfcode)
        return 0

    def denied(self):
        localCmd('chmod 400 %s' %
                 (os.path.dirname(__file__) + '/key/%s' % (self.host.key)))
        print('key file mod change to 400, try again!')
        #self.err = 'key file mod change to 400, try again!'
        return -1

    def xl_jumpserver_auth(self):
        _auth = input('\r\nPlease enter 6 digits.\r\n[MFA auth]:')
        self.ssh.sendline(_auth)
        return 1


class Host:
    def __init__(self, _ip, _port, _usrname, _passwd, _key, _alias, _route):
        self.ip = _ip
        self.port = _port
        self.usrname = _usrname
        self.passwd = _passwd
        self.key = _key
        self.alias = _alias
        self.route = _route

    def __repr__(self):
        return "Host %s@%s(%s)" % (self.usrname, self.ip, self.getSSHLoginCmd())

    def getSSHLoginCmd(self):
        if self.key != '':
            kpath = os.path.dirname(__file__) + '/key/%s' % (self.key)
            return 'ssh -o ServerAliveInterval=30 -p %d %s@%s -i %s' % (self.port, self.usrname, self.ip, kpath)
        else:
            return 'ssh -o ServerAliveInterval=30 -p %d %s@%s' % (self.port, self.usrname, self.ip)

    def SSH(self):
        if self.route == None:
            _shell = pexpect.spawn(self.getSSHLoginCmd())
            print('Login@%s ......' % self.ip)
            return switchLoginExpect(_shell, self).Run()
        else:
            _route = self.route.SSH()
            if _route == None:
                return None
            _route.sendline(self.getSSHLoginCmd())
            print('Login@%s ......' % self.ip)
            return switchLoginExpect(_route, self).Run()

    def getError(self, e):
        return "Host(%s) error: %s" % (self.ip, e)

    def Shell(self):
        _shell = self.SSH()
        if _shell == None:
            return
        _rows, _columns = os.popen('stty size', 'r').read().split()
        _shell.setwinsize(int(_rows), int(_columns))
        print('Welcome to %s\n' % (self.ip))
        _shell.interact()

# class switchHost :
#    def __init__(self) :


def InputIndex():
    try:
        _idx = int(input('Select one:')) - 1
    except:
        _idx = -1
    return _idx


hosts = []


class PARAMS(Enum):
    name = 0
    ip = 1
    port = 2
    usr = 3
    pwd = 4
    key = 5
    route = 6
    max = 7


def readHosts():
    fHost = open(os.path.dirname(__file__)+"/.servers")
    lines = fHost.readlines()
    for line in lines:
        if line[0] == '#':
            continue
        paras = line.split(',')
        if len(paras) != PARAMS.max.value:
            continue
        hosts.append(Host(paras[PARAMS.ip.value].strip(),
                     int(paras[PARAMS.port.value].strip()),
                     paras[PARAMS.usr.value].strip(),
                     paras[PARAMS.pwd.value].strip(),
                     paras[PARAMS.key.value].strip(),
                     paras[PARAMS.name.value].strip(),
                     None))
    fHost.close()


if __name__ == "__main__":
    readHosts()
    _i = 1
    for _h in hosts:
        print("\n%2d\t%s\t%s\n" % (_i, _h.ip, _h.alias))
        _i = _i + 1

    _id = InputIndex()
    if _id < len(hosts) and _id > 0:
        _h = hosts[_id]
        _h.Shell()

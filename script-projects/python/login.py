#!/usr/bin/python
import pexpect, os

class Host :
    def __init__(self, _ip, _port, _usrname, _passwd, _key, _alias, _relay) :
        self.ip = _ip
        self.port = _port
        self.usrname = _usrname
        self.passwd = _passwd
        self.key = _key
        self.alias = _alias
        self.relay = _relay

relayHosts = [
    Host('47.75.73.38', 22, 'ubuntu', '', 'hk.pem', 'HK-relay', -1),
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186-relay', -1),
]

hosts = [
    Host('45.77.223.88', 22, 'root', '9Y[zVY3PPS+GXBN]', '', '666MN', 0),
    Host('10.186.11.27', 22, 'root', 'Zxcvbn2018', '', '186-27', 0),
]

def ssh_passwd(_ssh, _host) :
    for _n in range(0, 3) :
        _ssh.sendline(_host.passwd)
        _i = _ssh.expect(['.*password.*', 'Last login.*'])
        if _i == 1 :
            return _i
        else :
            _host.passwd = input('Enter the password:')
            continue
    _n = -1
    return _n

def ssh_login(_ssh, _host) :
    while True :
        _i = _ssh.expect([".*password.*", ".*continue.*?", 'Last login.*', pexpect.EOF, pexpect.TIMEOUT], timeout = 3)
        if _i == 0 :
            return ssh_passwd(_ssh, _host)
        elif _i == 1 :
            _ssh.sendline('yes\n')
            continue
        elif _i == 2 :
            return 1
        else :
            print("[Error]Connection to %s fails"%(_host.ip))
            return -1

def getLoginCmd(_host) :
    if _host.passwd != '' :
        return 'ssh -p %d %s@%s'%(_host.port, _host.usrname, _host.ip)
    elif _host.key != '' :
        return 'ssh -p %d %s@%s -i %s'%(_host.port, _host.usrname, _host.ip, _host.key)
    return None

while True :
    print("==============[Menu]=============")
    for _index in range(len(hosts)) :
        print('\t%d.\t%s\t%s\n'%(_index+1, hosts[_index].alias, hosts[_index].ip))
    print('\tothers to quit')

    try :
        _idx = int(input('Enter the number:')) - 1
    except :
        print('Bye')
        break

    if _idx < 0 :
        print('Bye')
        break
    elif _idx >= len(hosts) :
        print('[ERROR]Range in 1 - %d'%(len(hosts)))
        continue

    _ssh = pexpect.spawn(getLoginCmd(relayHosts[hosts[_idx].relay]))
    if ssh_login(_ssh, relayHosts[hosts[_idx].relay]) < 0 :
        print('[ERROR]Connect relay host fails, try chmod 700 *.pem')
        continue
    _ssh.sendline(getLoginCmd(hosts[_idx]))
    if ssh_login(_ssh, hosts[_idx]) < 0 :
        print('[ERROR]Connect fails')
        _ssh.close()
        continue

    _rows, _columns = os.popen('stty size', 'r').read().split()
    _ssh.setwinsize(int(_rows), int(_columns))
    print('Welcome to %s\n'%(hosts[_idx].ip))
    _ssh.interact()
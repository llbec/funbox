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

hosts = [
    Host('45.77.223.88', 22, 'root', '9Y[zVY3PPS+GXBN]', '', '666MN', -1),
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186', -1),
    Host('10.186.11.27', 22, 'root', 'Zxcvbn2018', '', '186-27', 1),
]

def ssh_passwd(_ssh, _host) :
    for _n in range(0, 3) :
        _ssh.sendline(_host.passwd)
        _i = _ssh.expect(['.*password.*', 'Last login.*'])
        if _i == 1 :
            return _i
        else :
            _host.passwd = input('Enter the password for %s:'%(_host.ip))
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

def getPath(_id) :
    _i = _id
    listH = []
    listH.append(hosts[_i])
    while hosts[_i].relay >= 0 :
        _i = hosts[_i].relay
        listH.insert(0, hosts[_i])
    return listH

def myssh(_id) :
    hostpath = getPath(_id)
    if len(hostpath) < 1 :
        print('[ERROR]Host %s Path not existed'%hosts[_id].ip)
        return

    _ssh = pexpect.spawn(getLoginCmd(hostpath[0]))
    if ssh_login(_ssh, hostpath[0]) < 0 :
        _ssh.close()
        return

    for _i in range(1,len(hostpath)) :
        _ssh.sendline(getLoginCmd(hostpath[_i]))
        if ssh_login(_ssh, hostpath[_i]) < 0 :
            _ssh.close()
            return

    _rows, _columns = os.popen('stty size', 'r').read().split()
    _ssh.setwinsize(int(_rows), int(_columns))
    print('Welcome to %s\n'%(hosts[_idx].ip))
    _ssh.interact()

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
    
    myssh(_idx)
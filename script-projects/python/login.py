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
    Host('45.77.223.88', 22, 'root', '9Y[zVY3PPS+GXBN]', '', '666', -1),
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186', -1),
]

hs186 = [
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186', -1),
    Host('10.186.11.27', 22, 'root', 'Zxcvbn2018', '', '186-27', 0),
    Host('10.186.11.42', 22, 'root', 'Zxcvbn2018', '', '186-42', 0),
    Host('10.186.11.61', 22, 'root', 'chain33', '', '186-61', 0),
    Host('10.186.11.62', 22, 'root', 'chain33', '', '186-62', 0),
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
    _listH = []
    _listH.append(hosts[_i])
    while hosts[_i].relay >= 0 :
        _i = hosts[_i].relay
        _listH.insert(0, hosts[_i])
    if len(_listH) < 1 :
        print('[ERROR]Host %s Path not existed'%hosts[_id].ip)
    return _listH

def myssh(_hostpath) :
    if len(_hostpath) < 1 :
        return

    _ssh = pexpect.spawn(getLoginCmd(_hostpath[0]))
    if ssh_login(_ssh, _hostpath[0]) < 0 :
        _ssh.close()
        return

    for _i in range(1,len(_hostpath)) :
        _ssh.sendline(getLoginCmd(_hostpath[_i]))
        if ssh_login(_ssh, _hostpath[_i]) < 0 :
            _ssh.close()
            return

    _rows, _columns = os.popen('stty size', 'r').read().split()
    _ssh.setwinsize(int(_rows), int(_columns))
    print('Welcome to %s\n'%(_hostpath[-1].ip))
    _ssh.interact()

def get186Path(_host) :
    _h = _host
    _listH = []
    _listH.append(_h)
    while _h.relay >= 0 :
        _h = hs186[_h.relay]
        _listH.insert(0, _h)
    if len(_listH) < 1 :
        print('[ERROR]Host %s Path not existed'%_host.ip)
    return _listH

def ssh186() :
    while True:
        print("==============[186]=============")
        for _index in range(len(hs186)) :
            print('\t%d.\t%s\n'%(_index, hs186[_index].ip))
        print('\t%d.\tsubnet\n\tothers to quit'%len(hs186))
        
        try :
            _idx = int(input('Enter the number:'))
        except :
            return
        
        if _idx > len(hs186) :
            return
        elif _idx == len(hs186) :
            try :
                _snet = int(input('Enter the subnet:'))
            except :
                continue
            myssh(get186Path(Host('10.186.11.%d'%_snet, 22, 'root', 'Zxcvbn2018', '', '186-%d'%_snet, 0)))
        else :
            myssh(get186Path(hs186[_idx]))

while True :
    print("==============[Menu]=============")
    for _index in range(len(hosts)) :
        print('\t%d.\t%s\n'%(_index+1, hosts[_index].alias))
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
    
    if _idx == 1 :
        ssh186()
    else :
        myssh(getPath(_idx))
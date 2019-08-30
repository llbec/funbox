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

class Group :
    def __init__(self, name, hs) :
        self.name = name
        self.hs = hs

relayHost = [
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186', None),
]

hs186 = [
    Host('114.67.40.11', 20282, 'lbc', 'lbc', '', '186', None),
    Host('10.186.11.27', 22, 'root', 'Zxcvbn2018', '', '186-27', relayHost[0]),
    Host('10.186.11.42', 22, 'root', 'Zxcvbn2018', '', '186-42', relayHost[0]),
    Host('10.186.11.110', 22, 'root', 'Zxcvbn2019', '', '186-110', relayHost[0]),
    Host('10.186.11.198', 22, 'root', 'Zxcvbn2018', '', '186-198', relayHost[0]),
]

hschaosuan = [
    Host('114.67.38.12', 22, 'ubuntu', '', 'ubuntu', 'chs', None),
]

hs666 = [
    Host('45.77.223.88', 22, 'root', '9Y[zVY3PPS+GXBN]', '', '666', hs186[1]),
]

hsqulian = [
    Host('42.159.88.122', 22, 'xmeter', 'xmeter', '', 'qu1', None),
    Host('118.24.45.67', 22, 'xmeter', 'xmeter', '', 'qu2', None),
    Host('134.175.11.21', 22, 'xmeter', 'xmeter', '', 'qu3', None),
    Host('121.196.205.206', 22, 'xmeter', 'xmeter', '', 'qu4', None),
]

groups = [
    Group('666', hs666),
    Group('186', hs186),
    Group('chs', hschaosuan),
    Group('quL', hsqulian),
]

def ssh_passwd(_ssh, _host) :
    for _n in range(0, 3) :
        _ssh.sendline(_host.passwd)
        _i = _ssh.expect(['.*password.*', 'Last login.*', '.*verification.*', 'Permission denied'])
        if _i == 1 :
            return _i
        elif _i == 2 :
            _vfcode = input('\r\nPlease enter the verification code sent to your mobile phone:')
            _ssh.sendline(_vfcode)
            return 1
        elif _i == 3 :
            #print(_ssh.after)
            localCmd('chmod 400 %s'%(os.path.dirname(__file__) + '/key/%s'%(_host.key)))
            print('key file mod change to 400, try again!')
            os._exit(0)
        else :
            _host.passwd = input('Enter the password for %s:'%(_host.ip))
            continue
    _n = -1
    return _n

def ssh_login(_ssh, _host) :
    while True :
        _i = _ssh.expect(
                            [".*password.*",
                            ".*continue.*?",
                            'Last login.*',
                            '.*verification.*',
                            pexpect.EOF, 
                            pexpect.TIMEOUT], timeout = 3)
        if _i == 0 :
            return ssh_passwd(_ssh, _host)
        elif _i == 1 :
            _ssh.sendline('yes\n')
            continue
        elif _i == 2 :
            return 1
        elif _i == 3 :
            _vfcode = input('\r\nPlease enter the verification code sent to your mobile phone:')
            _ssh.sendline(_vfcode)
            return 1
        else :
            print("[Error]Connection to %s fails"%(_host.ip))
            return -1

def getLoginCmd(_host) :
    if _host.passwd != '' :
        return 'ssh -p %d %s@%s'%(_host.port, _host.usrname, _host.ip)
    elif _host.key != '' :
        kpath = os.path.dirname(__file__) + '/key/%s'%(_host.key)
        return 'ssh -p %d %s@%s -i %s'%(_host.port, _host.usrname, _host.ip, kpath)
    return None

def getPathbyId(_id, _hlist) :
    _h = _hlist[_id]
    _hs = []
    _hs.append(_h)
    while _h.relay != None :
        _h = _h.relay
        _hs.insert(0, _h)
    if len(_hs) < 1 :
        print('[ERROR]Host %s Path not existed'%_hlist[_id].ip)
    return _hs

def myssh(_hostpath) :
    if len(_hostpath) < 1 :
        return

    _ssh = pexpect.spawn(getLoginCmd(_hostpath[0]))
    print('Login@%s ......'%_hostpath[0].ip)
    if ssh_login(_ssh, _hostpath[0]) < 0 :
        _ssh.close()
        return

    for _i in range(1,len(_hostpath)) :
        _ssh.sendline(getLoginCmd(_hostpath[_i]))
        print('Login@%s ......'%_hostpath[_i].ip)
        if ssh_login(_ssh, _hostpath[_i]) < 0 :
            _ssh.close()
            return

    _rows, _columns = os.popen('stty size', 'r').read().split()
    _ssh.setwinsize(int(_rows), int(_columns))
    print('Welcome to %s\n'%(_hostpath[-1].ip))
    _ssh.interact()

def getPathbyHost(_host) :
    _h = _host
    _hs = []
    _hs.append(_h)
    while _h.relay != None :
        _h = _h.relay
        _hs.insert(0, _h)
    if len(_hs) < 1 :
        print('[ERROR]Host %s Path not existed'%_host.ip)
    return _hs

def ssh186() :
    while True:
        print("==============[186]=============")
        for _index in range(len(hs186)) :
            if _index == 0 :
                continue
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
            myssh(getPathbyHost(Host('10.186.11.%d'%_snet, 22, 'root', 'Zxcvbn2018', '', '186-%d'%_snet, hs186[0])))
        else :
            myssh(getPathbyHost(hs186[_idx]))

def sshgroup(_group) :
    if len(_group.hs) == 1:
        myssh(getPathbyHost(_group.hs[0]))
    elif _group.name == "186" :
        ssh186()
    else:
        while True :
            print("==============[%s]============="%_group.name)
            for _index in range(len(_group.hs)) :
                if _index == 0 :
                    continue
                print('\t%d.\t%s\n'%(_index, _group.hs[_index].ip))
            print('\tothers to quit')
            
            try :
                _idx = int(input('Enter the number:'))
            except :
                return
            
            if _idx >= len(_group.hs) :
                return
            else :
                myssh(getPathbyHost(_group.hs[_idx]))

def localCmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

while True :
    print("==============[Menu]=============")
    for _index in range(len(groups)) :
        print('\t%d.\t%s\n'%(_index+1, groups[_index].name))
    print('\tothers to quit')

    try :
        _idx = int(input('Enter the number:')) - 1
    except :
        print('Bye')
        break

    if _idx < 0 :
        print('Bye')
        break
    elif _idx >= len(groups) :
        print('[ERROR]Range in 1 - %d'%(len(groups)))
        continue
    
    sshgroup(groups[_idx])
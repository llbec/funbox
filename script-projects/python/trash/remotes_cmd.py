#!/usr/bin/python
import sys, os
import paramiko
import threading
import re
import socket

class Host :
    def __init__(self, _ip, _port, _usrname, _passwd, _arg1, _arg2) :
        self.ip = _ip
        self.port = _port
        self.usrname = _usrname
        self.passwd = _passwd
        self.arg1 = _arg1
        self.arg2 = _arg2

hosts = [
    Host("10.186.11.6", 22, "root", "Zxcvbn2018", "h-6", "10.186.11.27"),
    Host("10.186.11.7", 22, "root", "Zxcvbn2018", "h-7", "10.186.11.27"),
    Host("10.186.11.8", 22, "root", "Zxcvbn2018", "h-8", "10.186.11.27"),
    Host("10.186.11.27", 22, "root", "Zxcvbn2018", "h-27", "10.186.11.27"),
    Host("10.186.11.42", 22, "root", "Zxcvbn2018", "h-42", "10.186.11.60"),
    Host("10.186.11.60", 22, "root", "Zxcvbn2018", "h-60", "10.186.11.60"),
    Host("10.186.11.61", 22, "root", "Zxcvbn2018", "h-61", "10.186.11.61"),
    Host("10.186.11.62", 22, "root", "Zxcvbn2018", "h-62", "10.186.11.61"),
    Host("10.186.11.198", 22, "root", "Zxcvbn2018", "h-198", "10.186.11.60"),
    Host("10.186.11.227", 22, "root", "Zxcvbn2018", "h-227", "10.186.11.61"),
    Host("10.186.11.253", 22, "root", "Zxcvbn2018", "h-253", "10.186.11.60")
]

if len(sys.argv) < 2 :
    print(sys.argv[0] + ' "command"')
    os._exit(0)

command = sys.argv[1]
hostSelected = ''
resSuccess = 0
resPass = 0
resFail = 0
if len(sys.argv) == 3 :
    hostSelected = sys.argv[2]

class hostThread (threading.Thread):
    def __init__(self, _host):
        threading.Thread.__init__(self)
        self.host = _host
    def run(self):
        recordResult(hostProcess(self.host))

def hostProcess(_host) :
    if hostSelected != '' :
        if hostSelected != _host.ip :
            return 0
    
    _output = _host.ip + ':\n\t'

    if isLocalIP(_host.ip) == 1 :
        '''_outs = localCmd(command).split('\n')
        for _out in _outs :
            _output += _out + '\t'
        print(_output)'''
        print(_host.ip + ':\n' + localCmd(command))
        return 1
    try :
        #login in to host
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        
        #run command
        _stdin, _stdout, _stderr = _ssh.exec_command(command)
        _errs = _stderr.readlines()
        if len(_errs) != 0 :
            for _err in _errs :
                _output += _err + '\t'
        else :
            _outs = _stdout.readlines()
            for _out in _outs :
                _output += _out + '\t'
        print(_output)

        _ssh.close()
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1
    return 1

def isLocalIP(_addr):
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(('8.8.8.8', 80))
        _ip = _s.getsockname()[0]
    finally:
        _s.close()

    if _ip == _addr :
        return 1
    else :
        return 0

def localCmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def recordResult(_result) :
    global resFail, resPass, resSuccess
    if _result == 1 :
        resSuccess += 1
    elif _result == 0 :
        resPass += 1
    else :
        resFail += 1

def showResult() :
    print('Execution result:\tTotal:%d\tSucceed:%d\tPassed:%d\tFailed%d'%(resSuccess+resPass+resFail, resSuccess, resPass, resFail))

threads = []
for _host in hosts :
    _thd = hostThread(_host)
    _thd.start()
    threads.append(_thd)

for _t in threads :
    _t.join()

showResult()

#python3 /root/pro-test/script-projects/python/remotes_cmd.py "sed -i '\$a\export GOPATH=\"\$HOME/go\"' /etc/profile"
#python3 /root/pro-test/script-projects/python/remotes_cmd.py "sed -i '\$a\export GOBIN=\"\$GOPATH/bin\"' /etc/profile"
#python3 /root/pro-test/script-projects/python/remotes_cmd.py "sed -i '\$a\export PATH=\"\$PATH:/usr/local/go/bin:\$GOPATH/bin\"' /etc/profile"
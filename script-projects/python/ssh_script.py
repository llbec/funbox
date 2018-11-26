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
    Host("10.186.11.6", 22, "root", "Zxcvbn2018", "h-6", "10.186.11.61"),
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

if len(sys.argv) < 3 :
    print(sys.argv[0] + ' [run|stop|clean] targetfile')
    os._exit(0)

command = sys.argv[1]
fileName = sys.argv[2]
srcFile = srcPath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + "/"  + fileName
screenName = fileName.split('.')[0]
srcSize = os.path.getsize(srcFile)
destDirectory = 'ssh-script'
hostSelected = ''

#log result
resSuccess = 0
resPass = 0
resFail = 0

if len(sys.argv) == 4 :
    hostSelected = sys.argv[3]

def getScriptCmd(_script, _arg1, _arg2) :
    return 'python3 %s %s %s'%(_script, _arg1, _arg2)

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
    #local
    if _host.ip == getLocalIP() :
        if command == 'run' :
            if localCleanScreen() != 1 :
                print(_host.ip + ' clean screen failed!')
                return -1
            localCmd('screen -dmS %s %s'%(screenName, getScriptCmd(fileName, _host.arg1, _host.arg2)))
            print(_host.ip + ' script is working ...')
        elif command == 'stop' :
            if localCleanScreen() != 1 :
                print(_host.ip + ' stop failed!')
            print(_host.ip + ' stoped')
        elif command == 'clean' :
            if localCleanScreen() != 1 :
                print(_host.ip + ' clean screen failed!')
            #localCmd('rm %s'%(fileName))
            print(_host.ip + ' is clean')
        else :
            print(sys.argv[0] + " [run|stop|clean] targetfile")
            return 0
        return 1
    
    #remote
    _ssh = getRemote(_host)
    if _ssh == None :
        print("Login in %s failed!"%(_host.ip))
        return -1
    
    if command == 'run' :
        if searchPath(_ssh, _host) == 1 :
            if removeDestFile(_ssh, _host) != 1 :
                _ssh.close()
                return -1
        else :
            if makeDir(_ssh, _host) != 1 :
                print(_host.ip + ' make directory failed!')
                _ssh.close()
                return -1
        
        if copyDestFile(_ssh, _host) != 1 :
            print(_host.ip + ' copy file failed!')
            _ssh.close()
            return -1
        
        if cleanScreen(_ssh, _host) < 0 :
            _ssh.close()
            return -1
        
        if runFile(_ssh, _host) == 1 :
            print(_host.ip + ' script is working ...')
        else :
            print(_host.ip + ' script failed!')
    elif command == 'stop' :
        if cleanScreen(_ssh, _host) < 0 :
            print(_host.ip + 'stop failed! screen ' + screenName)
        _ssh.close()
        print(_host.ip + ' stoped')
    elif command == 'clean' :
        if cleanScreen(_ssh, _host) < 0 :
            print(_host.ip + 'stop failed! screen ' + screenName)
        if searchPath(_ssh, _host) == 1 :
            if removeDir(_ssh, _host) < 0 :
                print(_host.ip + 'clean failed!')
        print(_host.ip + ' is clean')
    else :
        print(sys.argv[0] + " [run|stop|clean] targetfile")
        return 0
    
    _ssh.close()
    return 1


# remote funcs
def getRemote(_host) :
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        return _ssh
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return None

def searchScreen(_ssh) :
    try :
        _stdin, _stdout, _stderr = _ssh.exec_command('screen -ls')
        _outs = _stdout.readlines()
        for _out in _outs :
            if re.search(screenName, _out) != None :
                return 1
        return 0
    except Exception as e:
        print(str(e))
        return -1

def getHome(_host) :
    if _host.usrname == 'root' :
        return '/root/'
    else :
        return '/home/%s/'%(_host.usrname)

def getDestFile(_host) :
    return getHome(_host) + destDirectory + '/' + fileName

def makeDir(_ssh, _host) :
    try :
        _cmd = 'mkdir ' + getHome(_host) + destDirectory
        _ssh.exec_command(_cmd)
        if searchPath(_ssh, _host) != 1 :
            return 0
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def removeDir(_ssh, _host) :
    try :
        _cmd = 'rm -rf ' + getHome(_host) + destDirectory
        _ssh.exec_command(_cmd)
        if searchPath(_ssh, _host) != 0 :
            return 0
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def searchPath(_ssh, _host) :
    try :
        _stdin, _stdout, _stderr = _ssh.exec_command('ls %s'%(getHome(_host)))
        _outs = _stdout.readlines()
        for _out in _outs :
            if re.search(destDirectory, _out) != None :
                return 1
        return 0
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def removeDestFile(_ssh, _host) :
    try :
        _cmd = "rm " + getDestFile(_host)
        _ssh.exec_command(_cmd)
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def copyDestFile(_ssh, _host) :
    try :
        _sftp = paramiko.SFTPClient.from_transport(_ssh.get_transport())
        _sftp = _ssh.open_sftp()
        _remote = _sftp.put(srcFile, getDestFile(_host))
        _sftp.close()
        if _remote.st_size != srcSize :
            print('%s copy file failed! size is %d, expert is %d'%(_host.ip, _remote.st_size, srcSize))
            return 0
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def cleanScreen(_ssh, _host) :
    try :
        _count = 0
        while searchScreen(_ssh) == 1 :
                _ssh.exec_command('screen -S %s -X quit'%(screenName))
                _count += 1
                if _count > 3 :
                    return 0
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

def runFile(_ssh, _host) :
    try :
        _ssh.exec_command('screen -dmS %s %s'%(screenName, getScriptCmd(getDestFile(_host), _host.arg1, _host.arg2)))
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

#local funcs
def localCmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def localCleanScreen() :
    _count = 0
    while re.search(screenName, localCmd("screen -ls")) != None :
        localCmd('screen -S %s -X quit'%(screenName))
        _count += 1
        if _count > 3 :
            return 0
    return 1

def getLocalIP():
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(('8.8.8.8', 80))
        _ip = _s.getsockname()[0]
    finally:
        _s.close()

    return _ip

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

def run() :
    print("Start to run %s in hosts"%(fileName))
    _threads = []
    for _host in hosts :
        _thd = hostThread(_host)
        _thd.start()
        _threads.append(_thd)

    for _t in _threads :
        _t.join()
    showResult()

run()

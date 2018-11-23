#!/usr/bin/python
import sys, os
import paramiko
import threading
import re

class Host :
    def __init__(self, _ip, _port, _usrname, _passwd, _hname, _remoteip) :
        self.ip = _ip
        self.port = _port
        self.usrname = _usrname
        self.passwd = _passwd
        self.hname = _hname
        self.remoteip = _remoteip

hosts = [
    Host("10.186.11.6", 22, "root", "Zxcvbn2018", "h-6", "10.186.11.27"),
    Host("10.186.11.7", 22, "root", "Zxcvbn2018", "h-7", "10.186.11.27"),
    Host("10.186.11.8", 22, "root", "Zxcvbn2018", "h-8", "10.186.11.27"),
    Host("10.186.11.42", 22, "root", "Zxcvbn2018", "h-42", "10.186.11.60"),
    Host("10.186.11.60", 22, "root", "Zxcvbn2018", "h-60", "10.186.11.60"),
    Host("10.186.11.61", 22, "root", "Zxcvbn2018", "h-61", "10.186.11.61"),
    Host("10.186.11.62", 22, "root", "Zxcvbn2018", "h-62", "10.186.11.61"),
    Host("10.186.11.198", 22, "root", "Zxcvbn2018", "h-198", "10.186.11.60"),
    Host("10.186.11.227", 22, "root", "Zxcvbn2018", "h-227", "10.186.11.61"),
    Host("10.186.11.253", 22, "root", "Zxcvbn2018", "h-253", "10.186.11.60")
]

if len(sys.argv) < 3 :
    print(sys.argv[0] + ' [run|stop|clear] targetfile')
    os._exit(0)

command = sys.argv[1]
fileName = sys.argv[2]
srcFile = srcPath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + "/"  + fileName
screenName = fileName.split('.')[0]
srcSize = os.path.getsize(srcFile)
destDirectory = 'ssh-script'

class hostThread (threading.Thread):
    def __init__(self, _host):
        threading.Thread.__init__(self)
        self.host = _host
    def run(self):
        hostProcess(self.host)

def hostProcess(_host) :
    _ssh = getRemote(_host)
    if _ssh == None :
        print("Login in %s failed!"%(_host.ip))
        return
    
    if command == 'run' :
        if searchPath(_ssh, _host) == 1 :
            if removeDestFile(_ssh, _host) < 0 :
                _ssh.close()
                return
        else :
            if makeDir(_ssh, _host) != 1 :
                print(_host.ip + ' make directory failed!')
                _ssh.close()
                return
        
        if copyDestFile(_ssh, _host) != 1 :
            print(_host.ip + ' copy file failed!')
            _ssh.close()
            return
        
        if clearScreen(_ssh, _host) < 0 :
            _ssh.close()
            return
        
        if runFile(_ssh, _host) == 1 :
            print(_host.ip + ' script is working ...')
        else :
            print(_host.ip + ' script failed!')
    elif command == 'stop' :
        if clearScreen(_ssh, _host) < 0 :
            print(_host.ip + 'stop failed! screen ' + screenName)
        _ssh.close()
    elif command == 'clear' :
        if searchPath(_ssh, _host) == 1 :
            if removeDir(_ssh, _host) < 0 :
                print(_host.ip + 'clear failed!')
    else :
        print(sys.argv[0] + " [run|stop|clear] targetfile")
    
    _ssh.close()
    return


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
        return 0
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

def clearScreen(_ssh, _host) :
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
        _ssh.exec_command('screen -dmS %s python3 %s %s %s'%(screenName, getDestFile(_host), _host.hname, _host.remoteip))
        return 1
    except Exception as e:
        print(_host.ip + ' ' + str(e))
        return -1

#local funcs
def run() :
    print("Start to run %s in hosts"%(fileName))
    _threads = []
    for _host in hosts :
        _thd = hostThread(_host)
        _thd.start()
        _threads.append(_thd)

    for _t in _threads :
        _t.join()
    print("All hosts are running!")

run()
#def stop() :
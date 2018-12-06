#!/usr/bin/python
import sys, os, time
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

def isLocalIP(_addr):
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(('8.8.8.8', 80))
        _ip = _s.getsockname()[0]
    finally:
        _s.close()
    if _ip == _addr :
        return 1
    return 0

def localCmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def cmdHandle(_host) :
    if len(sys.argv) < 3 :
        print('python ' + sys.argv[0].split('/')[-1] + ' cmd "command"')
        os._exit(0)
    if isLocalIP(_host.ip) == 1 :
        print(_host.ip + ':\n' + localCmd(sys.argv[2]))
        return 1
    #else remote
    #login in to host
    try :
        #login in to host
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        
        #run command
        _output = _host.ip + ':\n\t'
        _stdin, _stdout, _stderr = _ssh.exec_command(sys.argv[2])
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
        print(_host.ip + ',cmdHandle error: ' + str(e))
        return -1
    return 1

def getHome(_host) :
    if _host.usrname == 'root' :
        return '/root'
    else :
        return '/home/%s'%(_host.usrname)

def isExist(_ssh, _host, _path) :
    try :
        _stdin, _stdout, _stderr = _ssh.exec_command('ls ' + _path)
        for _out in _stdout.readlines() :
            if re.search('No such file or directory', _out) == None :
                return True
        return False
    except Exception as e:
        print(_host.ip + ',isExist error: ' + str(e))
        return False

def checkPath(_ssh, _host, _path) :
    try :
        _directs = _path.split('/')
        _index = 0
        for i in range(len(_directs)) :
            if i == 0 :
                if _directs[0] == '' :
                    _check = ''
                    continue
                else :
                    _check = getHome(_host)
            _check += '/'+_directs[i]
            _index = i
            if isExist(_ssh, _host, _check) == False :
                break
        if _index >= len(_directs) :
            return 1
        for _i in range(_index, len(_directs)-1) :
            if _i == _index :
                _ssh.exec_command('mkdir %s'%(_check))
            else :
                _check += '/'+_directs[_i]
                _ssh.exec_command('mkdir %s'%(_check))
        return 1
    except Exception as e:
        print(_host.ip + ',isExist error: ' + str(e))
        return -1

def copyFile(_ssh, _host, _src, _dest) :
    try :
        #rm file
        _ssh.exec_command('rm %s'%(_dest))
        if -1 == checkPath(_ssh, _host, _dest) :
            return -1
        #copy file
        _sftp = paramiko.SFTPClient.from_transport(_ssh.get_transport())
        _sftp = _ssh.open_sftp()
        _remote = _sftp.put(_src, _dest)
        _sftp.close()
        if _remote.st_size != os.path.getsize(_src) :
            print('%s copy file failed! size is %d, expert is %d'%(_host.ip, _remote.st_size, os.path.getsize(_src)))
            _ssh.exec_command('rm %s'%(_dest))
            return -1
        return 1
    except Exception as e:
        print('%s, copyFile error: %s. src is %s, dest is %s.'%(_host.ip, str(e), _src, _dest))
        return -1

def copyHandle(_host) :
    if len(sys.argv) < 4 :
        print('python ' + sys.argv[0].split('/')[-1] + ' cp srcfile destfile')
        os._exit(0)
    if isLocalIP(_host.ip) == 1 :
        return 0
    try :
        #login in to host
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        
        return copyFile(_ssh, _host, sys.argv[2], sys.argv[3])
    except Exception as e:
        print(_host.ip + ',copyHandle: ' + str(e))
        return -1

def getScreenName(_path) :
    _ts = _path.split('/')
    return _ts[len(_ts) - 1].split('.')[0]

def searchScreen(_ssh, _host, _scnname) :
    try :
        _stdin, _stdout, _stderr = _ssh.exec_command('screen -ls | grep %s'%(_scnname))
        if len(_stdout.readlines()) != 0 :
            return 1
        return 0
    except Exception as e:
        print(_host.ip + ',searchScreen error: ' + str(e))
        return -1

def localCleanScreen(_scnname) :
    _count = 0
    while re.search(_scnname, localCmd("screen -ls | grep %s"%(_scnname))) != None :
        localCmd('screen -S %s -X quit'%(_scnname))
        _count += 1
        if _count > 3 :
            return -1
    return 1

def cleanScreen(_ssh, _host, _scnname) :
    try :
        _count = 0
        while searchScreen(_ssh, _host, _scnname) == 1 :
                _ssh.exec_command('screen -S %s -X quit'%(_scnname))
                _count += 1
                if _count > 3 :
                    return -1
        return 1
    except Exception as e:
        print(_host.ip + ',cleanScreen error: ' + str(e))
        return -1

def getPythonCmd(_python, _arg1, _arg2) :
    return 'screen -x -S %s -p 0 -X stuff "python3 %s %s %s\n"'%(getScreenName(_python), _python, _arg1, _arg2)

def pythonRun(_host, _python) :
    if isLocalIP(_host.ip) == 1 :
        if localCleanScreen(getScreenName(_python)) != 1 :
            print(_host.ip + ' clean screen failed!')
            return -1
        localCmd('screen -dmS %s'%(getScreenName(_python)))
        localCmd(getPythonCmd(_python, _host.arg1, _host.arg2))
        print(_host.ip + ' python is working ...')
        return 1
    #else remote
    #login in to host
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        #screen clean
        if cleanScreen(_ssh, _host, getScreenName(_python)) <= 0 :
            _ssh.close()
            return -1
        #copy file
        if copyFile(_ssh, _host, _python, _python) != 1 :
            _ssh.close()
            return -1
        #create screen & run python
        _ssh.exec_command('screen -dmS %s'%(getScreenName(_python)))
        time.sleep(0.5)
        _ssh.exec_command(getPythonCmd(_python, _host.arg1, _host.arg2))
        print(_host.ip + ' python is working ...')
        _ssh.close()
        return 1
    except Exception as e:
        print(_host.ip + ',pythonRun error: ' + str(e))
        return -1

def pythonStop(_host, _python) :
    if isLocalIP(_host.ip) == 1 :
        return localCleanScreen(getScreenName(_python))
    #else remote
    #login in to host
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        _r = cleanScreen(_ssh, _host, getScreenName(_python))
        _ssh.close()
        return _r
    except Exception as e:
        print(_host.ip + ',pythonStop error: ' + str(e))
        return -1

def pythonClean(_host, _python) :
    if isLocalIP(_host.ip) == 1 :
        return localCleanScreen(getScreenName(_python))
    #else remote
    #login in to host
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        cleanScreen(_ssh, _host, getScreenName(_python))
        _ssh.exec_command('rm %s'%(_python))
        _ssh.close()
        return 1
    except Exception as e:
        print(_host.ip + ',pythonClean error: ' + str(e))
        return -1


def pythonHandle(_host) :
    if len(sys.argv) < 4 :
        print('python ' + sys.argv[0].split('/')[-1] + ' py [run|stop|clean] pythonfile')
        os._exit(0)
    _action = sys.argv[2]
    _python = sys.argv[3]
    if _python.split('/')[0] != '' and _python.split('/')[0] != '~' :
        _python = os.getcwd() + '/' + _python
    if _python.split('/')[0] == '~' :
        _python.replace('~/', '%s/'%(getHome(_host)))
    if _action == 'run' :
        return pythonRun(_host, _python)
    elif _action == 'stop' :
        return pythonStop(_host, _python)
    elif _action == 'clean' :
        return pythonClean(_host, _python)

def scnRun(_host, _scnname, _cmd) :
    if isLocalIP(_host.ip) == 1 :
        if localCleanScreen(_scnname) != 1 :
            print(_host.ip + ' clean screen failed!')
            return -1
        localCmd('screen -dmS %s'%(_scnname))
        localCmd('screen -x -S %s -p 0 -X stuff "%s\n"'%(_scnname, _cmd))
        print(_host.ip + ' screen is working ...')
        return 1
    #else remote
    #login in to host
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        #screen clean
        if cleanScreen(_ssh, _host, _scnname) <= 0 :
            _ssh.close()
            return -1
        #create screen & run cmd
        _ssh.exec_command('screen -dmS %s'%(_scnname))
        _ssh.exec_command('screen -x -S %s -p 0 -X stuff "%s\n"'%(_scnname, _cmd))
        print(_host.ip + ' screen is working ...')
        _ssh.close()
        return 1
    except Exception as e:
        print(_host.ip + ',scnRun error: ' + str(e))
        return -1

def scnStop(_host, _scnname) :
    if isLocalIP(_host.ip) == 1 :
        return localCleanScreen(_scnname)
    #else remote
    #login in to host
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        #screen clean
        if cleanScreen(_ssh, _host, _scnname) <= 0 :
            _ssh.close()
            return -1
        _ssh.close()
        return 1
    except Exception as e:
        print(_host.ip + ',scnRun error: ' + str(e))
        return -1

def screenHandle(_host) :
    if len(sys.argv) < 4 :
        print('python ' + sys.argv[0].split('/')[-1] + ' scn [run|stop] screenname [command|]')
        os._exit(0)
    _action = sys.argv[2]
    if _action == 'run' :
        if len(sys.argv) < 5 :
            print('python ' + sys.argv[0].split('/')[-1] + ' scn run screenname command')
            os._exit(0)
        return scnRun(_host, sys.argv[3], sys.argv[4])
    elif _action == 'stop' :
        return scnStop(_host, sys.argv[3])

#log result
resSuccess = 0
resPass = 0
resFail = 0

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

mapAct = {
    "cmd" : cmdHandle,
    "cp"  : copyHandle,
    "py"  : pythonHandle,
    "scn" : screenHandle
}

def helpinfo() :
    #print(sys.argv[0] + ' [cmd|cp|py] [args ...]')
    info = 'python ' + sys.argv[0].split('/')[-1] + ' ['
    for _key in mapAct.keys() :
        info += _key+'|'
    info = info[:-1]
    info += '] [args ...]'
    print(info)
    os._exit(0)

class hostThread (threading.Thread):
    def __init__(self, _host):
        threading.Thread.__init__(self)
        self.host = _host
    def run(self):
        recordResult(hostProcess(self.host))

def hostProcess(_host) :
    _act = sys.argv[1]
    '''if _act == "cmd" :
        return cmdHandle(_host)
    elif _act == "cp" :
        return copyHandle(_host)
    elif _act == 'py' :
        return pythonHandle(_host)
    elif _act == 'scn' :
        return screenHandle(_host)'''
    return mapAct[_act](_host)

if len(sys.argv) < 2 :
    helpinfo()
'''if sys.argv[1] != "cmd" and sys.argv[1] != "cp" and sys.argv[1] != "py" and sys.argv[1] != "scn" :
    helpinfo()'''
kExist = False
for keyAct in mapAct.keys() :
    if keyAct == sys.argv[1] :
        kExist = True
        break

if kExist == False :
    helpinfo()

threads = []
for _host in hosts :
    _thd = hostThread(_host)
    _thd.start()
    threads.append(_thd)

for _t in threads :
    _t.join()

showResult()
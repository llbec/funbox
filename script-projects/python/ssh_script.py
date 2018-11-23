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

if len(sys.argv) < 2 :
    print("please select a file as a parameter")
    os._exit(0)

father_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")
scriptfile = father_path + "/"  + sys.argv[1]
screenname = sys.argv[1].split('.')[0]
fsize = os.path.getsize(scriptfile)

class hostThread (threading.Thread):
    def __init__(self, _host):
        threading.Thread.__init__(self)
        self.host = _host
    def run(self):
        hostprocess(self.host)

def hostprocess(_host) :
    try :
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _ssh.connect(_host.ip, _host.port, _host.usrname, _host.passwd, timeout=5)
        print("ssh on ", _host.ip)

        #1st, delete file
        _cmd = "rm " + scriptfile
        _stdin, _stdout, _stderr = _ssh.exec_command(_cmd)
        '''_er = _stderr.readlines()
        if len(_er) != 0 :
            print('%s\t%s'%(_host.ip, _er[0]))'''
        
        #2nd, copy file
        _sftp = paramiko.SFTPClient.from_transport(_ssh.get_transport())
        _sftp = _ssh.open_sftp()
        _remote = _sftp.put(scriptfile, scriptfile)
        _sftp.close()
        if _remote.st_size != fsize :
            print('%s copy file failed! size is %d, expert is %d'%(_host.ip, _remote.st_size, fsize))
            return -1
        print('%s reload file %s'%(_host.ip, scriptfile))

        #3rd, clear screens
        while findScreen(_ssh) == 1 :
            _ssh.exec_command('screen -S %s -X quit'%(screenname))

        #4th, create new screen and run script
        _ssh.exec_command('screen -dmS %s python3 %s %s %s'%(screenname, scriptfile, _host.hname, _host.remoteip))
        print(_host.ip,' run %s in screen '%(scriptfile), screenname)

        #finish
        _ssh.close()
    except :
        print('%s\tError\n'%(_host.ip))
        return -2
    return 0

def findScreen(_ssh) :
    _stdin, _stdout, _stderr = _ssh.exec_command('screen -ls')
    _outs = _stdout.readlines()
    for _out in _outs :
        if re.search(screenname, _out) != None :
            return 1
    return 0

threads = []
for _host in hosts :
    _thd = hostThread(_host)
    _thd.start()
    threads.append(_thd)

for _t in threads :
    _t.join()

print("ALL Finish!")
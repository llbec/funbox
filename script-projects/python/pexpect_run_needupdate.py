import pexpect, paramiko
import os, sys
import threading

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
    print("Operation on ", _host.ip)
    _ssh = pexpect.spawnu('ssh -p %d %s@%s'%(_host.port, _host.usrname, _host.ip))
    try :
        _i = _ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)
        if _i == 0 :
            _ssh.sendline(_host.passwd)
        elif _i == 1:
            _ssh.sendline('yes\n')
            _ssh.expect('password: ')
            _ssh.sendline(_host.passwd)
        #operation start
        #1st, remove file
        _cmd = "rm " + scriptfile
        _ssh.sendline(_cmd)
        '''_i = _ssh.expect(['cannot remove', '#'], timeout=5)
        if _i == 0 :
            print("No such file")
        elif _i == 1 :
            print("file deleted")
        else :
            print("Unknow")'''
        
        #2nd, copy file
        _ret = scp_operation(_ssh, _host)
        if _ret == 0 :
            if mkdir_operation(_ssh, _host) != 1 :
                return -3
            if scp_operation(_ssh, _host) != 1 :
                return -5
        elif _ret < 0:
            return -4 
        #3rd, run file
        #operation end
    except pexpect.EOF:
        print("EOF")
        _ssh.close()
        return -1
    except pexpect.TIMEOUT:
        print("TIMEOUT")
        _ssh.close()
        return -2

def scp_operation(_ssh, _host) :
    _cmd = 'scp -P %d %s@%s:%s %s'%(_host.port, _host.usrname, _host.ip, scriptfile, scriptfile)
    _ssh.sendline(_cmd)
    try :
        _i = _ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)
        if _i == 0 :
            _ssh.sendline(_host.passwd)
        elif _i == 1:
            _ssh.sendline('yes\n')
            _ssh.expect('password: ')
            _ssh.sendline(_host.passwd)
    except pexpect.TIMEOUT :
        print("Copy file failed")
        return -3
    
    try :
        _i = _ssh.expect(['100%', 'No such file or directory'], timeout=5)
        if _i == 0 :
            return 1
        elif _i == 1:
            return 0
    except pexpect.TIMEOUT :
        return -1

#need update,is not work now
def mkdir_operation(_ssh, _host) :
    _dirs = father_path.split("/")
    for _dir in _dirs :
        if _dir == '' :
            continue
        if _dir == _host.usrname :
            _ssh.sendline('cd')
        else :
            _ssh.sendline('cd /%s'%(_dir))
            try :
                _i = _ssh.expect(['/%s#'%(_dir), 'No such file or directory'], timeout=1)
                if _i == 1 :
                    _ssh.sendline('mkdir %s'%(_dir))
                    _ssh.sendline('cd /%s'%(_dir))
                    _ssh.expect('/%s#'%(_dir), timeout=1)
            except pexpect.TIMEOUT :
                return -1
    return 1

threads = []
for _host in hosts :
    _thd = hostThread(_host)
    _thd.start()
    threads.append(_thd)

for _t in threads :
    _t.join()

print("Finish!")
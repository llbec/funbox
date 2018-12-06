#!/usr/bin/python

import os
#import re
import sys
import time
import json
import socket

gLetters=[chr(i) for i in range(97,123)]
gIndexs = [0] * 26
gLayers = 1

#logfile = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + '/script.log'

#func
def increaseLayers() :
    global gLayers
    _i = 0
    while 1 :
        gIndexs[_i] += 1
        if gIndexs[_i] < 26 :
            return

        gIndexs[_i] = 0
        if _i == gLayers - 1 :
            gLayers += 1

        if gLayers >= 27 :
            gLayers = 0
            return

        _i += 1
    return

def get_tx(_node, _value) :
    _v = '"'
    _v += _node
    for i in range(0,gLayers):
        _v += gLetters[gIndexs[i]]

    increaseLayers()
    _v += str(_value)
    _v += '='
    _v += str(_value)
    _v += '"\''
    return _v

def send_cmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def getLocalIP():
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(('8.8.8.8', 80))
        _ip = _s.getsockname()[0]
    finally:
        _s.close()
    return _ip
#func end

mapArgvs = {
    "10.186.11.6" : ["h-6", "10.186.11.61" ],
    "10.186.11.7" : ["h-7", "10.186.11.27" ],
    "10.186.11.8" : ["h-8", "10.186.11.27" ],
    "10.186.11.27" : ["h-27", "10.186.11.27" ],
    "10.186.11.42" : ["h-42", "10.186.11.60" ],
    "10.186.11.60" : ["h-60", "10.186.11.60" ],
    "10.186.11.61" : ["h-61", "10.186.11.61" ],
    "10.186.11.62" : ["h-62", "10.186.11.61" ],
    "10.186.11.198" : ["h-198", "10.186.11.60" ],
    "10.186.11.227" : ["h-227", "10.186.11.61" ],
    "10.186.11.253" : ["h-253", "10.186.11.60" ]
}

myArgv = mapArgvs[getLocalIP()]

if len(myArgv) < 2 :
    #print("please select a file as a parameter")
    os._exit(0)

nodename = myArgv[0]
host = myArgv[1]
i = 0

timsstart = 1542715140
tnow = time.time()
#log = open(logfile, mode = 'a')
print("script will start at :", time.asctime(time.localtime(timsstart)))
#log.write('%d#script will start after %s\n'%(time.time(),time.asctime(time.localtime(timsstart))))
while tnow < timsstart :
    time.sleep(1)
    tnow = time.time()

cmd_send_tx_prifix = 'curl -s \'' + host + ':26657/broadcast_tx_commit?tx='
while gLayers != 0 :
    cmd = cmd_send_tx_prifix + get_tx(nodename, i)
    i += 1
    if i == sys.maxsize :
        i = 0
    
    #ret = send_cmd(cmd)
    #res = re.match("error", send_cmd(cmd))
    res = json.loads(send_cmd(cmd)).get("result")
    if res != None :
        print('Trying', cmd, '... OK. Hash is:', res.get("hash"), '. Height is:', res.get("height"))
        #log.write('%d#Tring %s ... OK. Hash is: %s, Height is: %d'%(time.time(), cmd, res.get("hash"), res.get("height")))
    else :
        print('Trying', cmd, '... FAILED')
        #log.write('%d#Tring %s ... FAILED.'%(time.time(), cmd))
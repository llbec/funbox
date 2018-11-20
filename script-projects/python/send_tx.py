#!/usr/bin/python

import os
#import re
import sys
import time
import json

gLetters=[chr(i) for i in range(97,123)]
gIndexs = [0] * 26
gLayers = 1

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
#func end

node = input("Enter node name:")
host = input("Enter host ip:")
i = 0

timsstart = 1542715140
tnow = time.time()
print("script will start at :", time.asctime(time.localtime(timsstart)))
while tnow < timsstart :
    time.sleep(1)
    tnow = time.time()

cmd_send_tx_prifix = 'curl -s \'' + host + ':26657/broadcast_tx_commit?tx='
while gLayers != 0 :
    cmd = cmd_send_tx_prifix + get_tx(node, i)
    i += 1
    if i == sys.maxsize :
        i = 0
    
    #ret = send_cmd(cmd)
    #res = re.match("error", send_cmd(cmd))
    res = json.loads(send_cmd(cmd)).get("result")
    if res != None :
        print('Trying', cmd, '... OK. Hash is:', res.get("hash"), '. Height is:', res.get("height"))
    else :
        print('Trying', cmd, '... FAILED')
#!/usr/bin/python

import os, sys, argparse, json, getpass, random

class Address :
    def __init__(self, _Secret, _addr) :
        self.Secret = _Secret
        self.addr = _addr

srcAddr = Address("", "SZkgLVprTwMNBPzvSgCfrGtdFADyThzMPA")
listrcvs = []
listIndex = 0

def rpcwd(_m, *_params):
    _ps = ''
    for _p in _params:
        _ps += '%s,'%_p
    if _ps[len(_ps)-1] == ',':
        _ps = _ps[:len(_ps)-1]
    return 'curl -s --user Ulord130:Ulord130 --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://182.151.30.93:9889/'%(_m, _ps)

def operation (_cmd) :
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def callRpc(_wd):
    ret = json.loads(operation(_wd))
    if not ret['error'] is None:
        print(ret['error'])
        os._exit(0)
    return ret['result']

def GetUtxos(_addr) :
    return callRpc(rpcwd('getaddressutxos', '{"addresses": ["%s"]}'%_addr))

def GetBalance(_addr) :
    return callRpc(rpcwd('getaddressbalance', '{"addresses": ["%s"]}'%_addr))

def GetAmount() :
    return random.randint(5000,100000)

def createrawtx() :
    _vout = ''
    _vouts = {}
    _amount = 0
    for i in range(0,10) :
        _vouts[listrcvs[listIndex]] = GetAmount()
        _amount += _vouts[listrcvs[listIndex]]
        listIndex += 1


utxos = GetUtxos(srcAddr.addr)
print(len(utxos), GetAmount(), GetBalance(srcAddr.addr))
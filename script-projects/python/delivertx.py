#!/usr/bin/python

import os, sys, argparse, json, getpass, random

class Address :
    def __init__(self, _Secret, _addr) :
        self.Secret = _Secret
        self.addr = _addr

srcAddr = Address("", "UZEa2p6K4AjYyypGH7c12n7LM8s7YTQkxu")
listrcvs = []
listIndex = 0
COIN = 100000000

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
    return callRpc(rpcwd('getaddressbalance', '{"addresses": ["%s"]}'%_addr))["balance"]


def GetAmount() :
    return random.randint(5000,100000) * COIN

def GetVins(_addr, _num) :
    _vins = "["
    _utxos = GetUtxos(_addr)
    if _num > len(_utxos) :
        _num = len(_utxos)
    if _num == 0 :
        return "", 0
    _count = 0
    for i in range(0, _num) :
        _b = int(utxo["satoshis"])
        _vins += "{\"txid\":\"%s\",\"vout\":%d},"%(utxo["txid"], int(utxo["outputIndex"]))
        _count += _b
    _vins[len(_vins)-1] = "]"
    return _vins, _count

def createrawtx(_src, _dst, _amount) :
    _balance = GetBalance(_src)
    if _amount >= _balance :
        _amount = _balance - 1
    _vins, _count = GetVins(_addr, _amount)
    _change = _count - _amount - 1

    if _change != 0 and _amount != 0 :
        _vout = '{\"%s\":{:.8f},\"%s\":{:.8f}}'%(_src,a2str(_change/COIN),_dst,a2str(_amount/COIN))
    elif _change != 0 :
        _vout = '{\"%s\":{:.8f}}'%(_src,a2str(_change/COIN))
    elif _amount != 0 :
        _vout = '{\"%s\":{:.8f}}'%(_dst,a2str(_amount/COIN))
    else :
        print("Origin address has no balance")
        os._exit(0)

    _rawtx = rpcwd('createrawtransaction', _vins, _vout)
    print(_rawtx)


utxos = GetUtxos(srcAddr.addr)
print(len(utxos), GetAmount(), GetBalance(srcAddr.addr))
print(GetVins(srcAddr.addr, 5))
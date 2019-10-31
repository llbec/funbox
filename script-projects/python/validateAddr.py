#!/usr/bin/python

import os, sys, argparse, json, getpass

listSecret = []
listRcv = []
redeemScript = "532102e781a1e50d1b2868f1416a90889eebbd427d50cfec16f2c660244f4d704b1b9621030941e5c318708929ea61975996e2b1dbe4b4b6776d69bc2b7f6fc9e16be3b239210356f5a9acdf355094d34912d25eb5f2b02b1b095656a94892ee6f6ddbc94e1d2253ae"
script = "a91488ad225351c77286c5c3fc11695ba8a5065d41b687"

class validateAddress :
    def __init__(self, _listSecret, _threshold, _addr, _redeem, _script) :
        self.Secrets = _listSecret
        self.Threshold = _threshold
        self.addr = _addr
        self.Redeem = _redeem
        self.script = _script

srcAddr = validateAddress(listSecret, 3, "SPENofN6W55jViCHCnV4J8hqJh1p8S9bTu", redeemScript, script)

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

#def createtx() {}

print(GetUtxos(srcAddr.addr))
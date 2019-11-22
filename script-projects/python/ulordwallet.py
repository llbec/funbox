#!/usr/bin/python

import os, sys, argparse, json, getpass, random, time

Fee = 0.00000001
COIN = 100000000

class Rpc :
    def __init__ (self, _name, _pwd, _host, _port) :
        self.name = _name
        self.pwd = _pwd
        self.host = _host
        self.port = _port
    
    def word(self, _method, _params):
        _paramStr = ''
        for _p in _params:
            _paramStr += '%s,'%_p
        if _paramStr[len(_paramStr)-1] == ',':
            _paramStr = _paramStr[:len(_paramStr)-1]
        return 'curl -s --user %s:%s --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://%s:%s/'%(self.name, self.pwd, _m, _paramStr, self.host, self.port)

    def operation (self, _cmd) :
        _p = os.popen(_cmd)
        _data = _p.read()
        _p.close()
        return _data
    
    def Run(self, _method, _params):
        ret = json.loads(self.operation(self.word(_method, _params)))
        if not ret['error'] is None:
            print(ret['error'])
            os._exit(0)
        return ret['result']

class Key :
    def __init__ (self, _addr, _secret, _rpc) :
        self.address = _addr
        self.secret = _secret
        self.rpc = _rpc
    
    def Balance(self) :
        return self.rpc.Run('getaddressbalance', '{"addresses": ["%s"]}'%self.address)["balance"]
    
    def Utxos(self) :
        return self.rpc.Run('getaddressutxos', '{"addresses": ["%s"]}'%self.address)

    def UnMatures(self) :
        return self.rpc.Run('getaddressmempool', '{"addresses": ["%s"]}'%self.address)
    
    def CheckUtxo(self, _utxo) :
        _txid = _utxo["txid"]
        if _utxo["comfirms"] < 1 :
            return False
        
        for _memtx in self.UnMatures() :
            if _txid == _memtx["prevtxid"] :
                print("conflict tx: %s"%_txid)
                return False
        return True

    def createrawtx(self, _vin, _vout) :
        return self.rpc.Run('createrawtransaction', _vin, _vout)

    def signrawtx(self, _rawtx) :
        if _rawtx == None or _rawtx == "" :
            return None
        _ret = self.rpc.Run('signrawtransaction', '"%s"'%_rawtx.strip('\n'), '[]', '["%s"]'%self.secret)
        if _ret["complete"] == True:
            return _ret["hex"]
        print("Sign rawtransaction failed, without matched private key.")
        os._exit(0)

    def sendrawtx(self, _tx) :
        if _tx == None:
            return "No rawtransaction data"
        return self.rpc.Run('sendrawtransaction', '"%s"'%_tx.strip('\n'))

class Dispersion :
    def __init__ (self, _key, _recipients, _min, _max) :
        self.recipients = _recipients
        self.key = _key
        self.voutNumber = 5
        self.min = _min
        self.max = _max
    
    def GetAmount(self) :
        return random.randint(self.min, self.max)
    
    def createVin(self) :
        _voutNumber = self.voutNumber
        _vins = "["
        _utxos = self.key.Utxos()
        if _voutNumber > len(_utxos) :
            _voutNumber = len(_utxos)
        if _voutNumber == 0 :
            return "", 0
        _count = 0
        for i in range(0, _voutNumber) :
            _utxo = _utxos[i]
            if self.key.CheckUtxo(_utxo) == False :
                continue
            _b = _utxo["satoshis"]
            _vins += "{\"txid\":\"%s\",\"vout\":%d},"%(_utxo["txid"], int(_utxo["outputIndex"]))
            _count += _b
        _vins = _vins[:len(_vins)-1] + "]"
        return _vins, _count/COIN

    def createVout(self, _amount) :
        _index = random.randint(0, len(self.recipients))
        _voutStr = "{"
        for i in range(0, 20) :
            _value = GetAmount()
            if _value >= _amount :
                break
            _voutStr += "\"%s\":%d,"%(listrcvs[_index], _value)
            _amount -= _value
            _index += 1
            if _index >= len(listrcvs) :
                _index = 0

        if _amount > Fee :
            _change = _amount - Fee
            #print(_amount, Fee, _change)
            _voutStr += "\"%s\":%.8f,"%(_src, _change)
        _voutStr = _voutStr[:len(_voutStr)-1] + "}"
        return _voutStr

    def Run(self) :
        while True :
            vin, amount = self.createVin()
            if amount > 0 :
                vout = self.createVout(amount)
                rawtx = self.key.createrawtx(vin, vout)
                tx = self.key.signrawtx(rawtx)
                ret = self.key.sendrawtx(tx)
                print(ret)
            else :
                #print(GetUtxos(srcAddr.addr))
                print("No UTXO!")
            time.sleep(60)

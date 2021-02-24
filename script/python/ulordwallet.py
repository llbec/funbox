#!/usr/bin/python

import os, sys, argparse, json, getpass, random, time

Fee = 0.00000001
COIN = 100000000
GUTXOLimit = 100

def InputIndex() :
    try :
        _idx = int(input('Enter the number:')) - 1
    except :
        _idx = -1
    return _idx

class Rpc :
    def __init__ (self, _name, _pwd, _host, _port) :
        self.name = _name
        self.pwd = _pwd
        self.host = _host
        self.port = _port
    
    def word(self, _method, *_params):
        _paramStr = ''
        for _p in _params:
            _paramStr += '%s,'%_p
        if _paramStr[len(_paramStr)-1] == ',':
            _paramStr = _paramStr[:len(_paramStr)-1]
        return 'curl --user %s:%s --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://%s:%s/'%(self.name, self.pwd, _method, _paramStr, self.host, self.port)

    def operation (self, _cmd) :
        try:
            _p = os.popen(_cmd)
            _data = _p.read()
            _p.close()
        except OSError:
            print("command: %s\n error!\n"%(_cmd))
        else:
            return _data
    
    def Run(self, _method, *_params):
        _paramStr = ''
        for _p in _params:
            _paramStr += '%s,'%_p
        #print(_paramStr)
        if _paramStr[len(_paramStr)-1] == ',':
            _paramStr = _paramStr[:len(_paramStr)-1]
        _cmd = 'curl -s --user %s:%s --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://%s:%s/'%(self.name, self.pwd, _method, _paramStr, self.host, self.port)
        #print(_cmd)
        _retjson = self.operation(_cmd)
        if _retjson == "" :
            print("comand: %s\nGet none response!"%(_cmd))
            os._exit(-1)
        ret = json.loads(_retjson)
        if not ret['error'] is None:
            print(ret['error'])
            os._exit(0)
        return ret['result']
    
    def Height(self) :
        _h = self.Run("getinfo", "")["blocks"]
        _bhash = self.Run("getblockhash", _h)
        _block = self.Run("getblock", "\"%s\""%_bhash)
        _time = _block["time"]
        return _h, _time

class Config :
    def __init__ (self, _path) :
        self.path = _path
        self.loadfile()

    def __repr__(self) :
        return "Config path is %s\nContents:\n%s"%(self.path, self.json)

    def loadfile(self) :
        try:
            with open(self.path, 'r') as _f:
                #print("loadfile", _f)
                self.json = json.load(_f)
                #print(self.json)
        except Exception as e:
            print("loadfile error:", e)
            os._exit(0)

    def updatefile(self) :
        try:
            with open(self.path, 'w') as _f:
                json.dump(self.json, _f)
        except Exception as e:
            print("updatefile error:", e)
    
    def Read(self, _name, _save = True) :
        if self.json == "" :
            self.loadfile()
        if _name in self.json :
            return self.json[_name]
        else :
            if _save :
                _v = input("Enter the %s :"%(_name))
                if _v == "" :
                    os._exit(0)
                self.Write(_name, _v)
                return _v
            else :
                return None
    
    def Write(self, _name, _value) :
        if self.json == "" :
            self.loadfile()
        self.json[_name] = _value
        self.updatefile()

class Key :
    def __init__ (self, _addr, _secret, _rpc) :
        self.address = _addr
        self.secret = _secret
        self.rpc = _rpc
    
    def __repr__ (self) :
        return "Host:%s,%s"%(self.rpc.host, self.address)
    
    def Balance(self) :
        return self.rpc.Run('getaddressbalance', '{"addresses": ["%s"]}'%self.address)["balance"]
    
    def Utxos(self) :
        return self.rpc.Run('getaddressutxos', '{"addresses": ["%s"]}'%self.address)
    
    def TxIDs(self) :
        return self.rpc.Run('getaddresstxids', '{"addresses": ["%s"]}'%self.address)

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

# not stable
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

#create transaction and send. select vin and create vout
class Gather :
    def __init__(self, _key, _dst, _amount=0) :
        self.key = _key
        self.dst = _dst
        self.fee = Fee*COIN
        self.amount = _amount*COIN
    
    def __repr__(self) :
        return "Gather<Translate %.8f from %s to %s .Fee is %.8f>"%(self.amount/COIN, self.key.address, self.dst, self.fee/COIN)
    
    def __GetVin(self) :
        _utxos = self.key.Utxos()
        _vinStr = "["
        _balance = 0
        _utxocout = 0
        for _utxo in _utxos :
            _vinStr += "{\"txid\":\"%s\",\"vout\":%d},"%(_utxo["txid"], int(_utxo["outputIndex"]))
            _balance += _utxo["satoshis"]
            _utxocout += 1
            if self.amount > 0 and _balance > self.amount :
                break
            if _utxocout >= GUTXOLimit :
                break
        _vinStr = _vinStr[:len(_vinStr)-1] + "]"
        return _vinStr, _balance
    
    def __GetVins(self) :
        _utxos = self.key.Utxos()
        _vinList = []
        _amtList = []
        _vinStr = "["
        _balance = 0
        _utxocout = 0
        for _utxo in _utxos :
            _vinStr += "{\"txid\":\"%s\",\"vout\":%d},"%(_utxo["txid"], int(_utxo["outputIndex"]))
            _balance += _utxo["satoshis"]
            _utxocout += 1
            if self.amount > 0 and _balance > self.amount :
                break
            if _utxocout >= GUTXOLimit :
                _vinStr = _vinStr[:len(_vinStr)-1] + "]"
                _vinList.append(_vinStr)
                _amtList.append(_balance)
                _vinStr = "["
                _balance = 0
                _utxocout = 0
                continue
        _vinStr = _vinStr[:len(_vinStr)-1] + "]"
        _vinList.append(_vinStr)
        _amtList.append(_balance)

        return _vinList, _amtList

    def __GetVout(self, _balance) :
        #if self.amount == 0 :
        #    self.amount = _balance - self.fee
        _amount = _balance - self.fee
        _change = _balance - _amount - self.fee
        #print("change is ", _change)
        if _change < 0 :
            print("Not enough Fee! balance(%.8f),amount(%.8f),Feee(%.8f)"%(_balance/COIN, _amount/COIN, self.fee/COIN))
            os._exit(0)
        elif _change == 0 :
            return "{\"%s\":%.8f}"%(self.dst, _amount/COIN)
        else :
            return "{\"%s\":%.8f, \"%s\":%.8f}"%(self.dst, _amount/COIN, self.key.address, _change/COIN)
    
    def Run(self) :
        if self.key.secret == "" :
            #print("%s without a private key, translate cancel")
            self.key.secret = input("Enter a secret key to sign this transaction:")
            #return
        _vins, _balances = self.__GetVins()
        if len(_vins) != len(_balances) or len(_vins) == 0 :
            print("__GetVins: No coins!")
            return
        if self.amount == 0 :
            for num in _balances :
                self.amount += num
        if 'y' == input("%s\nEnter y to continue:"%(self)) :
            for i in range(len(_vins)) :
                _vout = self.__GetVout(_balances[i])
                _rawtx = self.key.createrawtx(_vins[i], _vout)
                _tx = self.key.signrawtx(_rawtx)
                print(self.key.sendrawtx(_tx))
        #if _balance == 0 :
        #    print("No coins! vin(%s)"%(_vin))
        #    return
        #_vout = self.__GetVout(_balance)
        #_rawtx = self.key.createrawtx(_vin, _vout)
        #_tx = self.key.signrawtx(_rawtx)
        #if 'y' == input("%s\nEnter y to continue:"%(self)) :
        #    print(self.key.sendrawtx(_tx))

class UtWallet :
    def __init__(self, _path="default") :
        if _path == "default" :
            _dir, _ = os.path.split(os.path.abspath(__file__))
            self.file = Config(_dir+"/.wallet")
        else :
            self.file = Config(_path)
        #self.rpc = Rpc("euclan", "six666", "113.31.119.157", 9879)
        self.rpc = Rpc(self.file.Read("rpcuser"), self.file.Read("rpcpswd"), self.file.Read("host"), self.file.Read("rpcport"))
        self.__keys = self.__GetKeys()
        _rlmt = self.file.Read("utxolimit")
        if _rlmt != None:
            GUTXOLimit = _rlmt

    def __repr__(self) :
        _i = 1
        str = ""
        for _k in self.__keys :
            str += "\n%2d, %s\t%.8f"%(_i, _k.address, _k.Balance()/COIN)
            _i += 1
        str += "\n"
        return str

    class Command:
        def __init__ (self, _wallet, _addr) :
            self.__wallet = _wallet
            self.__addr = _addr
            self.__list = {
                1:self.__Balance,
                2:self.__LastCoin,
                3:self.__Coins,
                4:self.__Txs,
                5:self.__Sendto
            }
            self.__helps = {
                1:"Balance",
                2:"Last incoming",
                3:"All UTXOs",
                4:"All Transactions",
                5:"Make a deal"
            }
        
        def __Balance(self) :
            print("%.8f"%self.__wallet.GetBalance(self.__addr))
            return 0
        
        def __LastCoin(self) :
            print(self.__wallet.GetLastCoin(self.__addr))
            return 0

        def __Coins(self) :
            print(self.__wallet.GetCoins(self.__addr))
            return 0

        def __Txs(self) :
            self.__wallet.ShowRecords(self.__addr)
            return 0

        def __Sendto(self) :
            _dst = input('Enter the receiver address:')
            _amount = InputIndex() + 1
            self.__wallet.Sendto(self.__addr, _dst, _amount)
            return 0

        def __Handler(self, _id) :
            func = self.__list.get(_id, lambda :-1)
            return func()

        def __Titlie(self) :
            _titlie = "\n****** %s ******\nSelect a action:\n"%(self.__addr)
            for _k in self.__list.keys() :
                _titlie += "%d.\t%s\n"%(_k, self.__helps[_k])
            return _titlie

        def Run(self):
            while True :
                print(self.__Titlie())
                _id = InputIndex() + 1
                if self.__Handler(_id) < 0 :
                    break
    
    def Title(self) :
        _i = 1
        str = ""
        for _k in self.__keys :
            str += "\n%2d, %s\t%.8f"%(_i, _k.address, _k.Balance()/COIN)
            _i += 1
        str += "\n%2d, enter a address\n"%_i
        return str
    
    def __GetKeys(self) :
        _keys = []
        for _k in self.file.Read("keys", False) :
            if "secret" in _k :
                _keys.append(Key(_k["address"], _k["secret"], self.rpc))
            else :
                 _keys.append(Key(_k["address"], "", self.rpc))
        return _keys
    
    def __FindKey(self, _addr) :
        for _k in self.__keys :
            if _k.address == _addr :
                return _k
        return Key(_addr, "", self.rpc)

    def GetBalance(self, _addr) :
        return self.__FindKey(_addr).Balance()/COIN
    
    def GetAddress(self, _id) :
        if _id >= 0 and _id < len(self.__keys) :
            return self.__keys[_id].address
        return None
    
    def GetCoins(self, _addr) :
        _k = self.__FindKey(_addr)
        _utxos = _k.Utxos()
        _last = 0
        _str = "The coins in %s:\n"%(_addr)
        for _coin in _utxos :
            _confirm = _coin["currentheight"] - _coin["height"]
            _str += "\t<%s-%d>,%.8f,%d(%d),%d\n"%(
                _coin["txid"],
                _coin["outputIndex"],
                _coin["satoshis"]/COIN,
                _coin["height"],
                _coin["height"]-_last,
                _confirm
            )
            _last = _coin["height"]
        _h, _t = self.rpc.Height()
        _str += "checking at %d, %s"%(_h, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_t)))
        return _str

    def GetLastCoin(self, _addr) :
        _k = self.__FindKey(_addr)
        _last = _k.Utxos()[-1]
        _rawtx = self.rpc.Run("getrawtransaction", "\"%s\", 1"%(_last["txid"]))
        _str = "Last incoming @ %d(%s), confirms %d, amount %.8f, coin<%s-%d>\nchecking at %d, %s"%(
            _last["height"],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_rawtx["time"])),
            _last["currentheight"] - _last["height"],
            _last["satoshis"]/COIN,
            _last["txid"],
            _last["outputIndex"],
            _last["currentheight"],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        )
        return _str
    
    def Sendto(self, _addr, _dst, _amount=0) :
        _sender = Gather(self.__FindKey(_addr), _dst, _amount)
        _sender.Run()
    
    def ShowRecords(self, _addr, _writefile=True) :
        _k = self.__FindKey(_addr)
        _txs = _k.TxIDs()
        if _writefile :
            _dir, _ = os.path.split(os.path.abspath(__file__))
            _path = _dir + "/%s_%d.log"%(_addr, time.time())
            print("%s transaction records(%d):"%(_addr, len(_txs)))
            _index = 1
            with open(_path, 'a+') as _f:
                for _tx in _txs :
                    _f.write(self.AnalyzeTx(_addr, _tx))
                    print("\r%d"%_index, end="")
                    _index += 1
            print("\nDone")
        else:
            print("%s transaction records:\n"%(_addr))
            for _tx in _txs:
                print("\t%s\n"%(self.AnalyzeTx(_addr, _tx)))
    
    def AnalyzeTx(self, _addr, _tx, _detail=False) :
        _rawtx = self.rpc.Run("getrawtransaction", "\"%s\", 1"%(_tx))
        _coinbase = False
        _spentlist = []
        _rcvlist = []
        _amount = 0
        _invlaue = 0
        _outvalue = 0
        for _in in _rawtx["vin"] :
            if _in.__contains__("coinbase") :
                _coinbase = True
                break
            if _in["address"] == _addr :
                _amount -= _in["valueSat"]
                _spentlist.append({"txid":"%s"%(_in["txid"]),"outindex":_in["vout"],"amount":_in["valueSat"]})
            _invlaue += _in["valueSat"]
        for _out in _rawtx["vout"] :
            if _out["scriptPubKey"].__contains__("addresses") == False :
                continue
            _rcv = _out["scriptPubKey"]["addresses"][0]
            if _rcv == _addr :
                _amount += _out["valueSat"]
                _rcvlist.append({"address":"%s"%(_rcv),"outindex":_out["n"],"amount":_out["valueSat"]})
            _outvalue += _out["valueSat"]
        _str = ""
        if _detail :
            pass
        else :
            _str += "\r%s, %.8f"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_rawtx["time"])), _amount/COIN)
            if _coinbase :
                _str += ", Fee(0.0),        coinbase"
            else :
                _str += ", Fee(%.8f)"%((_invlaue-_outvalue)/COIN)
                if _amount > 0:
                    for _in in _rawtx["vin"]:
                        _str += ", %s(%.8f)"%(_in["address"], _in["valueSat"]/COIN)
                else :
                    for _out in _rawtx["vout"] :
                        _str += ", %s(%.8f)"%(_out["scriptPubKey"]["addresses"][0], _out["valueSat"]/COIN)
        return _str

if __name__ == "__main__":
    _wallet = UtWallet()
    while True :
        print(_wallet.Title())
        _id = InputIndex()
        if _id < 0 :
            break
        _addr = _wallet.GetAddress(_id)
        if _addr == None :
            _addr = input("Enter an address")
        _wallet.Command(_wallet, _addr).Run()
#Host49_233_162_142 = Rpc("six666", "six666", "49.233.162.142", 9879)
#print(Host49_233_162_142.Height())
#testKey = Key("UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h", "", Host49_233_162_142)
#print(testKey.Balance()/COIN)
#gether = Gather(testKey, "UduLEFeiDBYmZfW6qAL3ZUHSnYnsJ8yvam", 5632)
#gether.Run()
#print(UtWallet().GetLastCoin("UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h"))
#UtWallet().GetCoins("UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h")
#print(UtWallet().AnalyzeTx("UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h", "c90c3f23bbf6651b9b575d5929c4ef6bfc01c3ec7f2bdc691c0c35175454f24e"))
#print(UtWallet().AnalyzeTx("UU6n1tCZ62zbMFxwYMqxov3NBw69LnNCxn", "b854c10342a9e8ddf5466a7022f8f9cd59df61457c7fa7b88f880b14f206f8ba"))

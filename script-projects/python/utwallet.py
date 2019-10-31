#!/usr/bin/python

import os, sys, argparse, json, getpass

kpath = '.key'
argParser = argparse.ArgumentParser('utchain wallet')
argParser.add_argument('-o', '--origin', type=str, default='UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h', metavar='', help='Transaction origination address, type string')
argParser.add_argument('-r', '--receive', metavar='', type=str, default='UP4cRYyc71x3gd9pTFRvCRkppDJhz9RsG3', help='Transaction receiving address, type string')
argParser.add_argument('-f', '--fee', type=float, default=0.00000001, metavar='', help='Transaction fee, type float')
argParser.add_argument('-k', '--key', type=str, default='', metavar='', help='The private key to sign the transaction, type string')
argParser.add_argument('-c', '--coins', type=bool, default=False, metavar='', help='Show coins of origin address, type bool')
argParser.add_argument('-b', '--balance', type=bool, default=False, metavar='', help='Show balance of origin address, type bool')
argParser.add_argument('-s', '--send', type=bool, default=False, metavar='', help='Send transaction, type bool')
argParser.add_argument('-d', '--dumpkey', type=bool, default=False, metavar='', help='List Keys, type bool')
argParser.add_argument('-p', '--password', type=bool, default=False, metavar='', help='Set a new password for the commands, type bool')
argParser.add_argument('-l', '--list', type=bool, default=False, metavar='', help='List addresses, type bool')
argParser.add_argument('-t', '--rawtx', type=bool, default=False, metavar='', help='Show createrawtransaction')

def printAddrList(o, r):
    d = 'origin  address: %s\nreceive address: %s\n\n\n'%(o,r)
    d += '666\tUU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h\nkkkk\tUP4cRYyc71x3gd9pTFRvCRkppDJhz9RsG3\nlf\tUduLEFeiDBYmZfW6qAL3ZUHSnYnsJ8yvam\nmn\tUgVa3XSwPTomDiwSQLQ6t8L9u3zVNLiuBC'
    print(d)

def rpcwd(_m, *_params):
    _ps = ''
    for _p in _params:
        _ps += '%s,'%_p
    if _ps[len(_ps)-1] == ',':
        _ps = _ps[:len(_ps)-1]
    return 'curl -s --user Ulord03:Ulord03 --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://127.0.0.1:9889/'%(_m, _ps)
    #return 'curl --user Ulord130:Ulord130 --data-binary \'{"jsonrpc": "1.0", "id":"ut", "method": "%s", "params": [%s] }\' -H \'content-type: text/plain;\' http://182.151.30.93:9889/'%(_m, _ps)

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

def getCoins (_addr) :
    #return operation('%s getaddrvin %s'%(ut,_addr))
    return callRpc(rpcwd('getaddrvin', '"%s"'%_addr))

def a2str(_a) :
    return '%.8f'%_a

def createrawtx(_coins, _o, _r, _f) :
    _vout = ''
    _balance = _coins['balance']
    if _o == _r :
        _amount = _balance - _f
        _change = 0
    else :
        _amount = int(_balance)
        _change = _balance - _amount - _f

    if _change != 0 and _amount != 0 :
        _vout = '{\"%s\":%s,\"%s\":%s}'%(_o,a2str(_change),_r,a2str(_amount))
    elif _change != 0 :
        _vout = '{\"%s\":%s}'%(_o,a2str(_change))
    elif _amount != 0 :
        _vout = '{\"%s\":%s}'%(_r,a2str(_amount))
    else :
        print("Origin address has no balance")
        os._exit(0)

    #_rawtx = '%s createrawtransaction \'%s\' \'%s\''%(ut, _coins['Vin'], _vout)
    _rawtx = rpcwd('createrawtransaction', _coins['Vin'], _vout)
    #print(_rawtx)
    return callRpc(_rawtx)

def signrawtx(_rawtx) :
    _keys = getKeys()
    if _keys == None:
        print("None private key file")
        os._exit(0)
    for _k in _keys:
        #_cmd = '%s signrawtransaction %s \'[]\' \'["%s"]\''%(ut, _rawtx.strip('\n'), _k)
        _cmd = rpcwd('signrawtransaction', '"%s"'%_rawtx.strip('\n'), '[]', '["%s"]'%_k)
        _r = callRpc(_cmd)
        if _r["complete"] == True:
            return _r["hex"]
    print("Sign rawtransaction failed, without matched private key.")
    os._exit(0)

def sendrawtx(_tx):
    if _tx == None:
        return "No rawtransaction data"
    #return operation('%s sendrawtransaction %s'%(ut, _tx.strip('\n')))
    return callRpc(rpcwd('sendrawtransaction', '"%s"'%_tx.strip('\n')))

def encrypt(_s):
    a = bytearray(str(_s), 'utf-8')
    for index in range(len(a)):
        a[index] = a[index] ^ 87
    return a.decode(encoding='utf-8')

def decrypt(_s):
    a = bytearray(str(_s), 'utf-8')
    for index in range(len(a)):
        a[index] = a[index] ^ 87
    return a.decode(encoding='utf-8')

def loadFile():
    #_keys = None
    try:
        with open(kpath, 'r') as _f:
            return json.load(_f)
    except Exception as e:
        print(e)
        return None
    #_list = []
    #for _k in _keys:
    #    _list.append(decrypt(_k.strip('\n')))
    #return _list

def savekey(_k):
    _json = loadFile()
    if _json == None:
        _json = {'1':encrypt(_k)}
    else:
        _json['%d'%(len(_json))] = encrypt(_k)
    with open(kpath, 'w') as _f:
        json.dump(_json, _f)

def getKeys():
    _j = loadFile()
    if _j == None:
        return None
    _list = []
    for _i,_v in _j.items():
        if _i == 'password':
            continue
        _list.append(decrypt(_v))
    return _list

def updatekey(_key):
    _ks = getKeys()
    if _ks != None:
        for _k in _ks:
            if _key == _k:
                print("Already exesit!")
                return
    savekey(_key)
    print(getKeys())

def getPwd():
    _j = loadFile()
    if 'password' in _j:
        return decrypt(_j['password'])
    return ''

def checkPwd():
    password = getpass.getpass('please input your password:')
    if password != getPwd():
        print("Invalid password.")
        os._exit(0)

def updatePwd(new):
    _j = loadFile()
    _j['password'] = encrypt(new)
    with open(kpath, 'w') as _f:
        json.dump(_j, _f)

def main () :
    args = argParser.parse_args()

    if args.list:
        printAddrList(args.origin, args.receive)
        return

    if args.coins :
        print(getCoins(args.origin))
        return

    if args.balance:
        #print(operation('%s getaddrbalance %s'%(ut, args.origin)))
        b = callRpc(rpcwd('getaddrbalance', '"%s"'%args.origin))
        print('Balance: %.8f, Received: %.8f'%(b['balance'], b['received']))
        return

    if args.key != '':
        updatekey(args.key)
        return

    #the follow operations need password
    if args.password:
        checkPwd()
        pw1 = getpass.getpass('please input your new password:')
        pw2 = getpass.getpass('please repeat your new password:')
        if pw1 != pw2:
            print("The password is not same!")
            return
        updatePwd(pw1)
        return

    if args.dumpkey:
        checkPwd()
        print(getKeys())
        return
    
    if args.rawtx:
        coins = getCoins(args.origin)
        print(createrawtx(coins, args.origin, args.receive, args.fee))
        return

    if args.send:
        checkPwd()
        coins = getCoins(args.origin)
        rtx = createrawtx(coins, args.origin, args.receive, args.fee)
        tx = signrawtx(rtx)
        ret = sendrawtx(tx)
        print(ret)
        return

    print("Use -h or --help")
    return

main()


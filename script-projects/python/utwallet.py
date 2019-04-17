#!/usr/bin/python

import os, sys, argparse, json

ut = '~/utchain/src/ulord-cli'
argCount = 0
argParser = argparse.ArgumentParser('utchain wallet')
argParser.add_argument('-o', '--origin', type=str, default='UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h', metavar='', help='Transaction origination address')
argParser.add_argument('-r', '--receive', metavar='', type=str, default='UP4cRYyc71x3gd9pTFRvCRkppDJhz9RsG3', help='Transaction receiving address')
argParser.add_argument('-f', '--fee', type=float, default=0.00000001, metavar='', help='Transaction fee')
argParser.add_argument('-k', '--key', type=str, default='', metavar='', help='The private key to sign the transaction')
argParser.add_argument('-c', '--coins', type=bool, default=False, metavar='', help='Show coins of origin address')
argParser.add_argument('-b', '--balance', type=bool, default=False, metavar='', help='Show balance of origin address')
argParser.add_argument('-s', '--send', type=bool, default=False, metavar='', help='Send transaction')

def helpinfo() :
    print("%s address"%sys.argv[0])

def operation (_cmd) :
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def getCoins (_addr) :
    return operation('%s getaddrvin %s'%(ut,_addr))

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

    _rawtx = '%s createrawtransaction \'%s\' \'%s\''%(ut, _coins['Vin'], _vout)
    #print(_rawtx)
    return operation(_rawtx)

def signrawtx(_rawtx) :
    _keys = getKeys()
    if _keys == None:
        print("None private key file")
        os._exit(0)
    for _k in _keys:
        _cmd = '%s signrawtransaction %s \'[]\' \'["%s"]\''%(ut, _rawtx.strip('\n'), _k)
        _r = json.loads(operation(_cmd))
        if _r["complete"] == True:
            return _r["hex"]
    print("Sign rawtransaction failed, without matched private key.")
    os._exit(0)

def sendrawtx(_tx):
    if _tx == None:
        return "No rawtransaction data"
    return operation('%s sendrawtransaction %s'%(ut, _tx.strip('\n')))

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

def loadkey():
    #_keys = None
    try:
        with open('key', 'r') as _f:
            return json.load(_f)
    except Exception as e:
        print(e)
        return None
    #_list = []
    #for _k in _keys:
    #    _list.append(decrypt(_k.strip('\n')))
    #return _list

def savekey(_k):
    _json = loadkey()
    if _json == None:
        _json = {'0':decrypt(_k)}
    else:
        _json['%d'%(len(_json))] = decrypt(_k)
    with open('key', 'w') as _f:
        json.dump(_json, _f)

def getKeys():
    _j = loadkey()
    if _j == None:
        return None
    _list = []
    for _i,_v in _j.items():
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

def main () :
    args = argParser.parse_args()

    if args.coins :
        print(getCoins(args.origin))
        return

    if args.balance:
        print(operation('%s getaddrbalance %s'%(ut, args.origin)))
        return

    if args.key != '':
        updatekey(args.key)
        return

    if args.send:
        coins = json.loads(getCoins(args.origin))
        rtx = createrawtx(coins, args.origin, args.receive, args.fee)
        tx = signrawtx(rtx)
        ret = sendrawtx(tx)
        print(ret)
        return

    print("Use -h or --help")
    return

main()


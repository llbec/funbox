#!/usr/bin/python

import os, sys, argparse, json

ut = '~/utchain/src/ulord-cli'
argCount = 0
argParser = argparse.ArgumentParser('ulord transaction')
argParser.add_argument('-o', '--origin', type=str, default='UU6Zf3QBTmwaxEyLiuBCfXAGvamDHCMP8h', metavar='', help='Transaction origination address')
argParser.add_argument('-r', '--receive', type=str, metavar='UP4cRYyc71x3gd9pTFRvCRkppDJhz9RsG3', help='Transaction receiving address')
argParser.add_argument('-f', '--fee', type=float, default=0.00000001, metavar='', help='Transaction fee')
argParser.add_argument('-k', '--key', type=str, default='', metavar='', help='The private key to sign the transaction')
argParser.add_argument('-v', '--vin', type=bool, default=False, metavar='', help='Just show coins of origin address')

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
    except Exception:
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

    if args.vin :
        print(getCoins(args.origin))
        return

    if args.key != '':
        updatekey(args.key)
        return

    coins = json.loads(getCoins(args.origin))
    #print(coins['balance'], coins['Vin'])

    rtx = createrawtx(coins, args.origin, args.receive, args.fee)
    tx = signrawtx(rtx)
    ret = sendrawtx(tx)
    print(ret)

    return

main()


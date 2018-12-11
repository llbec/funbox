#!/usr/bin/python
import os, json

def send_cmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

class Transaction :
    def __init__(self, amount, token, fromname, toaddr) :
        self.amount = amount
        self.token = token
        self.fromname = fromname
        self.toaddr = toaddr
    
    #gaiacli tx send --amount=10000UToken --from=validator227 --to=cosmos1mdfar4yj3vlkrzxyhfskfz8sxw0uacarnthrfw  --chain-id=testnet-186
    def command(self) :
        return 'gaiacli tx send --amount=%d%s --from=%s --to=%s --chain-id=testnet-186'%(self.amount, self.token, self.fromname, self.toaddr)
    
    def execute(self) :
        return send_cmd(self.command())
    
class Balance :
    def __init__(self, addr) :
        self.addr = addr
    
    #gaiacli query account cosmos1mdfar4yj3vlkrzxyhfskfz8sxw0uacarnthrfw --chain-id=testnet-186
    def command(self) :
        return 'gaiacli query account %s --chain-id=testnet-186'%(self.addr)
    
    def query(self, token) :
        js = json.loads(send_cmd(self.command()))
        return
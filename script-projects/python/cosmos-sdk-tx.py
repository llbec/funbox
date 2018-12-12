#!/usr/bin/python
import os, json, socket, time, pexpect, re

def send_cmd(cmd) : 
    p = os.popen(cmd)
    data = p.read()
    p.close()
    return data

class Coin :
    def __init__(self, token, amount) :
        self.token = token
        self.amount = amount

class Transaction :
    def __init__(self, amount, token, fromname, toaddr) :
        self.amount = amount
        self.token = token
        self.fromname = fromname
        self.toaddr = toaddr
    
    #gaiacli tx send --amount=10000UToken --from=validator227 --to=cosmos1mdfar4yj3vlkrzxyhfskfz8sxw0uacarnthrfw  --chain-id=testnet-186
    def command(self) :
        return 'gaiacli tx send --amount=%d%s --from=%s --to=%s --chain-id=testnet-186'%(self.amount, self.token, self.fromname, self.toaddr)
    
    def execute(self, passwd) :
        #return send_cmd(self.command())
        tx = pexpect.spawnu(self.command())
        i = tx.expect(["Password to sign with", pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        if i == 0 :
            tx.sendline(passwd)
            i = tx.expect(["Committed at", pexpect.EOF, pexpect.TIMEOUT], timeout=5)
            if 0 == i :
                searchObj = re.search(r'block\s(\d+)', tx.buffer)
                if searchObj != None :
                    return "Committed at block %s"%(searchObj.group())
                return tx.buffer
            elif i == 1:
                return "EOF"
            else :
                return "TIMEOUT"
        elif i == 1 :
            return "Eof"
        else :
            return "Timeout"
    
class Balance :
    def __init__(self, addr) :
        self.addr = addr
    
    #gaiacli query account cosmos1mdfar4yj3vlkrzxyhfskfz8sxw0uacarnthrfw --chain-id=testnet-186
    def command(self) :
        return 'gaiacli query account %s --chain-id=testnet-186'%(self.addr)
    
    def query(self) :
        try:
            ret = []
            rjs = json.loads(send_cmd(self.command()))
            coins = rjs["value"]["coins"]
            for coin in coins :
                if int(coin["amount"]) != 0 :
                    ret.append(Coin(coin["denom"], int(coin["amount"])))
        except Exception as e:
            print(str(e))
        return ret

class Account :
    def __init__(self, name, addr, passwd) :
        self.name   = name
        self.addr   = addr
        self.passwd = passwd
    
    def balance(self) :
        return Balance(self.addr).query()

    def send(self, token, amount, to) :
        return Transaction(amount, token, self.name, to).execute(self.passwd)

class Host :
    def __init__(self, ip, account) :
        self.ip = ip
        self.account = account

def getLocalIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

g_Hosts = [
    Host("10.186.11.198",  Account("bank198",      "cosmos1mdfar4yj3vlkrzxyhfskfz8sxw0uacarnthrfw", "qaz1wsx2")),
    Host("10.186.11.60",   Account("validator60",  "cosmos1vv805rlyqkf9mxly52rwm3l2h7spj68cupw5pa", "qaz1wsx2")),
    Host("10.186.11.61",   Account("validator61",  "cosmos1vlekuyywkfjwqv4pafas6c4sn8af8dp2syseey", "qaz1wsx2")),
    Host("10.186.11.62",   Account("validator62",  "cosmos13et83jyfddc5evufpt2uhzceg8g2lcmfu5ccay", "qaz1wsx2")),
    Host("10.186.11.227",  Account("validator227", "cosmos1tprzy9h98hnja0yvdjlwchg70n32zd7hkghq8h", "qaz1wsx2")),
]

def getLocal() :
    ip = getLocalIP()
    for host in g_Hosts :
        if host.ip == ip :
            return host
    return None

g_Local = getLocal()
if g_Local == None :
    print("[ERROR] Fail to get host %s"%(getLocalIP()))
    os._exit(0)

g_Index = 0
g_amount = 1
while True :
    coins = g_Local.account.balance()
    if len(coins) == 0 or (len(coins) == 1 and coins[0].token == "STAKE") :
        print('[INFO] Have no coins to spend, hold a monent ...')
        time.sleep(1)
        continue
    for coin in coins :
        if coin.token == "STAKE" :
            continue
        if g_Hosts[g_Index].ip == g_Local.ip :
            g_Index = (g_Index + 1) % len(g_Hosts)
        if coin.amount > g_amount :
            print(g_Local.account.send(coin.token, g_amount, g_Hosts[g_Index].account.addr))
        else :
            print(g_Local.account.send(coin.token, coin.amount, g_Hosts[g_Index].account.addr))
        g_Index = (g_Index + 1) % len(g_Hosts)
import pexpect
import re
import sys


#letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
letters=[chr(i) for i in range(97,123)]
indexs = [0] * 26
layers = 1

#func
def increaseLayers() :
    global layers
    i = 0
    while 1 :
        indexs[i] += 1
        if indexs[i] < 26 :
            return

        indexs[i] = 0
        if i == layers - 1 :
            layers += 1

        if layers >= 27 :
            layers = 0
            return

        i += 1
    return


def get_tx(node, value) :
    v = '"'
    v += node
    for i in range(0,layers):
        v += letters[indexs[i]]

    increaseLayers()
    v += str(value)
    v += '='
    v += str(value)
    v += '"'
    return v
#func end

analyzer = pexpect.spawnu('abci-cli console')
analyzer.expect('> ')

node = input("Enter node name:")
i = 0

while layers != 0 :
    cmd = 'deliver_tx '
    cmd += get_tx(node, i)
    i += 1
    if i == sys.maxsize :
        i = 0
    
    #print('Trying', cmd, '...')
    analyzer.sendline(cmd)
    analyzer.expect('-> code: ')
    res = re.match("OK", analyzer.buffer)
    if res != None :
        print('Trying', cmd, '... OK')
    else :
        print('Trying', cmd, '... FAILED')
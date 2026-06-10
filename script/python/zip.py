#!/usr/bin/python

import zipfile
import itertools
import os
import sys
import threading
from threading import Lock

lock = Lock()

if len(sys.argv) != 2:
    os._exit(-1)

filename = sys.argv[1]
def uncompress(password):
    try:
        with zipfile.ZipFile(filename) as zfile:
            zfile.extractall("./", pwd=password.encode("utf-8"))
        return True
    except:
        return False

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"
symbols = "!@#$%^&*,."
total = letters + digits + symbols

"""
print("start:\n")
count = 0
for i in range(4, 15):
    for c in itertools.permutations(total, i):
        pwd = "".join(c)
        count += 1
        if uncompress(pwd):
            print('password is {}\n'.format(pwd))
            os._exit(0)
        else:
            print('\r' + '{}-{}'.format(i, count), end='', flush=True)
"""
done = False

def Finish():
    global done
    done = True

def Done():
    global done
    return done

class breakCode (threading.Thread):
    def __init__(self, length):
        threading.Thread.__init__(self)
        self.length = length
    def run(self) -> None:
        print('start search in length {}\n'.format(self.length))
        for c in itertools.permutations(total, self.length):
            pwd = "".join(c)
            if uncompress(pwd):
                print('password is {}\n'.format(pwd))
                lock.acquire()
                Finish()
                lock.release()
                return
            lock.acquire()
            if Done():
                lock.release()
                return
            lock.release()

list = []

for i in range(4,15):
    list.append(breakCode(i))

for trd in list:
    trd.start()
for trd in list:
    trd.join()

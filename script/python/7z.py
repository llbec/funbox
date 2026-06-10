#!/usr/bin/python

import py7zr
import sys
import os
import itertools

if len(sys.argv) < 2:
    print("example: python 7z.py 8\n")
    os._exit(-1)

def uncompress(pwd):
    try:
        with py7zr.SevenZipFile('【2000部】.7z', mode='r', password=pwd) as archive:
            archive.extractall()
        return True
    except:
        return False

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"
symbols = "!@#$%^&*,."
total = letters + digits + symbols

print("start:\n")
count = 0
for c in itertools.permutations(total, int(sys.argv[1])):
    pwd = "".join(c)
    count += 1
    if uncompress(pwd):
        print('password is {}\n'.format(pwd))
        os._exit(0)
    else:
        print('\r' + '{}-{}'.format(int(sys.argv[1]), count), end='', flush=True)


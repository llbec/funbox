
import zipfile
import itertools
import os

filename = ""
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

print("start:\n")
count = 0
total = letters + digits + symbols
for i in range(4, 15):
    for c in itertools.permutations(total, i):
        pwd = "".join(c)
        count += 1
        if uncompress(pwd):
            print('password is {}\n'.format(pwd))
            os._exit(0)
        else:
            print('\r' + '{}-{}'.format(i, count), end='', flush=True)

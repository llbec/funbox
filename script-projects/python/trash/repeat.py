#!/usr/bin/python
import os, sys, argparse, time

def GetRepeat(i) :
    return './chain33/chain33-cli send bty transfer -a 1 -n "for para chain %d" -t 14a4XnxAQ7iGzhKdzisEhX45YQdbHHP8cq -k 1CbEVT9RnM5oZhWMj4fxUrJX94VtRotzvs'%(i)

def send_cmd(_cmd) : 
    _p = os.popen(_cmd)
    _data = _p.read()
    _p.close()
    return _data

def HandleData(data) :
    print(data)

gArgs = argparse.ArgumentParser("repeat a command")
gArgs.add_argument('-s', '--start', type=int, default=0, metavar='', help='The command start index, default is 0')
gArgs.add_argument('-r', '--rounds', type=int, default=1, metavar='', help='The command repeat times, default is 1')
gArgs.add_argument('-p', '--period', type=float, default=0, metavar='', help='The command rounds sleep time, default is 0 s')

args = gArgs.parse_args()

for i in range(args.start, args.start+args.rounds) :
    HandleData(send_cmd(GetRepeat(i)))
    if args.period > 0 :
        time.sleep(args.period)
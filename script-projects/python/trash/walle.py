#!/usr/bin/python
import os, sys, argparse, time, termios, tty, string

class Tree :
    childs = []
    def __init__(self, p, d):
        self.parent = p
        self.data = d
        p.AddChild(self)
    def AddChild(self, c) :
        self.childs.append(c)
    def ShowChilds(self) :
        for cv in self.childs :
            print(cv.data, end='')
        print('\n')

class CmdView(Tree) :
    def __init__(self, p, d, f):
        super(Tree).__init__(p, d)
        self.excute = f
    def Check(self, s) :
        _matchs = []
        for cv in self.childs :
            if string.find(cv.data, s) == 0:
                _matchs.append(cv)
        if _matchs.count() > 1 :
            self.ShowChilds()
        elif _matchs.count() == 1:
            pass
        else :
            pass

if __name__ == '__main__' :
    str = ''
    while True:
        fd=sys.stdin.fileno()
        old_settings=termios.tcgetattr(fd)
        try :
            tty.setraw(fd)
            ch=sys.stdin.read(1)
        finally :
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ord(ch) == 0x3:
            #这个是ctrl c, 9 tab, 13 enter, 32 space
            break
        elif ord(ch) == 9:
            pass
        elif ord(ch) == 13:
            pass
        

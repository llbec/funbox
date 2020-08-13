#!/usr/bin/python

import json, os

class Config :
    def __init__ (self, _path) :
        self.path = _path
        self.loadfile()

    def __repr__(self) :
        return "Config path is %s\nContents:\n%s"%(self.path, self.json)

    def loadfile(self) :
        try:
            with open(self.path, 'r') as _f:
                #print("loadfile", _f)
                self.json = json.load(_f)
                #print(self.json)
        except Exception as e:
            print("loadfile error:", e)
            os._exit(0)

    def updatefile(self) :
        try:
            with open(self.path, 'w') as _f:
                json.dump(self.json, _f)
        except Exception as e:
            print("updatefile error:", e)
    
    def Read(self, _name) :
        if self.json == "" :
            self.loadfile()
        return self.json[_name]
    
    def Write(self, _name, _value) :
        if self.json == "" :
            self.loadfile()
        self.json[_name] = _value
        self.updatefile()
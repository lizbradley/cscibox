#! /usr/bin/python

import json

filename = "RAPiD-12-1K.Thornalley.2009.jsonld"

def readJson(filename):
    file = open(filename)
    jstr = file.read()
    file.close()
    data = json.loads(jstr)
    return data

if __name__ == "__main__":
    print readJson(filename)

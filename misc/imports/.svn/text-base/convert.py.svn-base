#!/usr/bin/env python

import os
import os.path

program1 = "./xml_convert.py"
program2 = "./xml_to_csv.py"

def convert():
    items = os.listdir('.')
    input = [item for item in items if item.endswith('.xml')]
    for file in input:
        output   = file[0:len(file)-4] + "-converted.xml"
        command  = program1 + " " + file + " " + output
        status   = os.system(command)
    items = os.listdir('.')
    input = [item for item in items if item.endswith('-converted.xml')]
    for file in input:
        output   = file[0:len(file)-14] + ".csv"
        command  = program2 + " " + file + " " + output
        status   = os.system(command)

if __name__ == '__main__':
    convert()

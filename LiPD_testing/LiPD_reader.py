#!/usr/bin/env python2

import json
import bagit
import zipfile
import tempfile
import os
import sys
import csv
import shutil

class TemporaryDirectory(object):
    """
    Temporary Directory management class, copied mostly from Python 3 source code,
    where it is part of the tempfile library.
    """
    def __init__(self, suffix="", prefix="tmp", dir=None):
        self.name = tempfile.mkdtemp(suffix, prefix, dir)
    def __repr__(self):
        return self.name
    def __enter__(self):
        return self.name
    def __exit__(self, exc, value, tb):
        self.cleanup()
    def cleanup(self):
        shutil.rmtree(self.name)

def toplevel(data,levels = 1):
    """
    toplevel(data, levels = 1)
    Returns the top n levels of a dictionary passed in as data, with the fields
    below the nth level replaced with their type (converted to a string, in order
    to be json serializeable). Example:

    > toplevel({"key1":5,"key2":6,"key3":{"key4":1},"key5":[1,2,3]})
    {'key3': "<type 'dict'>", 'key2': 6, 'key1': 5, 'key5': <type 'list'>}
    """
    if isinstance(data,dict):
        top = {}
        for i in data.items():
            if levels == 1:
                if isinstance(i[1],int) or isinstance(i[1],unicode):
                    top[i[0]] = i[1]
                else:
                    top[i[0]] = str(type(i[1]))
            else:
                top[i[0]] = toplevel(i[1],levels-1)
        return top
    elif isinstance(data,list) or isinstance(data,tuple):
        return [toplevel(i,levels) for i in data]
    else:
        return data

def jtlevel(data,levels=1):
    """
    Wraps toplevel in a call to produce formatted (json) output.
    """
    return json.dumps(toplevel(data,levels),indent=2,sort_keys=True)


#taken from http://kechengpuzi.com/q/s8689938
def get_members(zfile):
    """
    Returns a list of the members of a directory.
    """
    parts = []
    for name in zfile.namelist():
        if not name.endswith('/'):
            parts.append(name.split('/')[:-1])
    prefix = os.path.commonprefix(parts) or ''

    if prefix:
        prefix = '/'.join(prefix) + '/'
    offset = len(prefix)

    for zinfo in zfile.infolist():
        name = zinfo.filename
        if len(name) > offset:
            zinfo.filename = name[offset:]
            yield zinfo

def hasextension(ending):
    """
    Returns a function that checks to see if x ends with ending
    """
    return lambda x: x.endswith(ending)

def dataRead(tempdir,tabledata):
    """
    This function pulls relevant metadata from a dictionary and matches it with
    the correct column from the corresponding file.
    """
    print "\t ", tabledata["filename"], ":\n",
    with open(tempdir + '/data/' + tabledata["filename"], 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        data = list(reader)
        for k in tabledata["columns"]:
            print "\t\t",k["number"], ":", k[u'variableName'],
            if u'description' in k:
                print ",", k[u'description'],
            if u'units' in k:
                print ",", k[u'units'],
            print "\n", [data[i][k["number"]-1] for i in range(len(data))],"\n"
    print ""

def readLiPD(tempdir,filename):
    """
    This function returns the metadata in a dictionary from a LiPD file after
    validating it's contents, and throwing errors if it is not a valid
    """
    zfile = zipfile.ZipFile(filename)
    zfile.extractall(tempdir, get_members(zfile))
    lipdbag = bagit.Bag(tempdir)

    if not lipdbag.is_valid():
        raise ValueError(filename+" does not contain a valid bagit directory")

    jfilels = filter(hasextension('.jsonld'),os.listdir(tempdir+"/data"))

    if len(jfilels) > 1:
        raise ValueError("Too many jsonld files")
    elif len(jfilels) == 0:
        raise ValueError("No jsonld files")

    jfilename = jfilels[0]
    with open(tempdir + '/data/' + jfilename,'r') as jfile:
        metadata = json.loads(jfile.read())
    return metadata

def LiPD_data(tempdir,metadata):
    print "Dataset", metadata["dataSetName"], "Loaded successfully"
    print "Archive contains", metadata["archiveType"]
    print "File is LiPD v", metadata["LiPDVersion"]
    geodata = metadata['geo']['geometry']['coordinates']
    print "Latitude:", geodata[0],", Longitude:", geodata[1], ", Elevation:", geodata[2]
    #print "Latitude:", geodata[0],", Longitude:", geodata[1], ", Elevation:", geodata[2]

    print "Chron Variables recorded : "
    for i in metadata["chronData"]:
        for j in i["chronMeasurementTable"]:
            dataRead(tempdir,j)

    print "Paleo Variables recorded : "
    for i in metadata["paleoData"]:
        for j in i["paleoMeasurementTable"]:
            dataRead(tempdir,j)

filename = "test.lpd"

with TemporaryDirectory() as tempdir:
    metadata = readLiPD(tempdir,filename)
    LiPD_data(tempdir,metadata)

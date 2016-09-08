#! /usr/bin/python

import json
import bagit
import zipfile
import tempfile
import os
import sys

filename = "test.lpd"
tempdir = tempfile.mkdtemp(prefix='tmp')

#taken from http://kechengpuzi.com/q/s8689938
def get_members(zfile):
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
    return lambda x: x.endswith(ending)

try:
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

    print json.dumps(metadata, indent=4, separators=(',', ': '))



except Exception as e:
    print "FILE READING ERROR!\nThere was an error reading the LiPD file:"
    raise e

import json
import bagit
import zipfile
import tempfile
import os
import sys

filename = "test.lpd"
tempdir = tempfile.mkdtemp(prefix='tmp')

def toplevel(data,levels = 1):
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
    return json.dumps(toplevel(data,levels),indent=2,sort_keys=True)


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
except Exception as e:
    print "FILE READING ERROR!\nThere was an error reading the LiPD file:"
    raise

#print jtlevel(metadata,levels = 1)

try:
    print "Dataset", metadata["dataSetName"], "Loaded successfully"
    print "Archive contains", metadata["archiveType"]
    print "File is LiPD v", metadata["LiPDVersion"]
    geodata =metadata['geo']['geometry']['coordinates']
    print "Latitude:", geodata[0],", Longitude:", geodata[1], ", Elevation:", geodata[2]
    #print "Latitude:", geodata[0],", Longitude:", geodata[1], ", Elevation:", geodata[2]

except Exception as e:
    print "JSON PARSING ERROR!\nThere was an error while interpereting the LiPD data:"
    raise

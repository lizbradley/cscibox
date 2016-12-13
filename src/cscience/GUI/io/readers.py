import os
import shutil

import csv
import json

import bagit
import zipfile
import tempfile

import itertools

from cscience.framework import samples, datastructures


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
    def get_name(self):
        return self.name
    def cleanup(self):
        shutil.rmtree(self.name)
        
        
class LiPDReader(object):
    """
    This function returns the metadata in a dictionary from a LiPD file after
    validating it's contents, and throwing errors if it is not valid
    """
    def __init__(self, path):
        self.path = path
        self.fielddict = None
        self.metadata = {}
        
        with TemporaryDirectory() as tempdir, zipfile.ZipFile(self.path) as zfile:
            zfile.extractall(tempdir, self.get_members(zfile))
            lipdbag = bagit.Bag(tempdir)
        
            if not lipdbag.is_valid():
                raise ValueError("%s does not contain a valid bagit directory" % self.path)
        
            jfilels = filter(lambda x: x.lower().endswith('.jsonld'), 
                             os.listdir(os.path.join(tempdir, 'data')))
        
            if len(jfilels) > 1:
                raise ValueError("Too many jsonld files")
            elif len(jfilels) == 0:
                raise ValueError("No jsonld files")
        
            jfilename = jfilels[0]
            with open(os.path.join(tempdir, 'data', jfilename), 'r') as jfile:
                self.metadata = json.loads(jfile.read())
        
            for i in self.metadata["chronData"]:
                for j in i["chronMeasurementTable"]:
                    self.dataRead(tempdir, j)
        
            for i in self.metadata["paleoData"]:
                for j in i["paleoMeasurementTable"]:
                    self.dataRead(tempdir, j)
                    
        self.pdata = {k.get("variableName", ""): k
                for j in self.metadata.get("paleoData", [])
                for i in j.get("paleoMeasurementTable", [])
                for k in i.get("columns", {})}
        
        self.cdata = {k.get("variableName", ""): k
                for j in self.metadata.get("chronData", [])
                for i in j.get("chronMeasurementTable", [])
                for k in i.get("columns", {})}
        
        #for key in sorted(self.metadata.keys()):
        #    print key, type(self.metadata[key])
        
        #print self.metadata['archiveType']
        #print self.metadata['geo']
        #print self.metadata['pub']
        
        #print self.metadata['chronData'][0]
                    
    @property
    def core_name(self):
        return self.metadata[u"dataSetName"]
    @property
    def fieldnames(self):
        return itertools.chain(self.cdata.keys(), self.pdata.keys())
    @property
    def allfields(self):
        ret = {}
        ret.update(self.cdata)
        ret.update(self.pdata)
        return ret
    
    def get_known_metadata(self):
        known = {}
        if 'geo' in self.metadata:
            known['Core Site'] = datastructures.GeographyData.parse_value(self.metadata['geo'])
        if 'pub' in self.metadata:
            known['Required Citations'] = datastructures.PublicationList.parse_value(self.metadata['pub'])
        return known
    
    def get_unit_dict(self):
        return {key: value.get('units', None) for key, value in
                self.allfields.iteritems()}
    
    def get_data_reader(self, fielddict):
        filtered = {key: value.get('data', []) for 
                    key, value in self.allfields.iteritems() if 
                    key in fielddict}
        #TODO: this can almost certainly be done in 1-2 lines...
        flipped = [{} for i in filtered["depth"]]
        
        for key, value in filtered.iteritems():
            for i in range(len(value)):
                flipped[i][key] = value[i]

        return sorted(flipped, key=lambda x: x["depth"])
        
                    
    #taken from http://kechengpuzi.com/q/s8689938
    def get_members(self, zfile):
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
    
    def dataRead(self, tempdir, tabledata):
        """
        This function pulls relevant metadata from a dictionary and matches it with
        the correct column from the corresponding file.
        """
        #print "\t ", tabledata["filename"], ":\n",
        with open(os.path.join(tempdir, 'data', tabledata["filename"]), 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            data = list(reader)
            for k in tabledata["columns"]:
                k[u"data"] = [data[i][k["number"]-1] for i in range(len(data))]


class CSVReader(object):
    
    def __init__(self, path):
        self.path = path
        with open(self.path, 'rU') as input_file:
            #allow whatever sane csv formats we can manage, here
            sniffer = csv.Sniffer()
            #TODO: report error here on _csv.Error so the user knows wha hoppen
            dialect = sniffer.sniff(input_file.read(1024))
            dialect.skipinitialspace = True
            input_file.seek(0)
    
            #mild hack to make sure the file isn't empty and does have data,
            #before we start importing...
            #I would use the same reader + tell/seek but per
            #http://docs.python.org/2/library/stdtypes.html#file.tell
            #I'm not 100% confident that will work.
            tempreader = csv.DictReader(input_file, dialect=dialect)
            if not tempreader.fieldnames:
                wx.MessageBox("Selected file is empty.", "Operation Cancelled",
                              wx.OK | wx.ICON_INFORMATION)
                return False
            try:
                dataline = tempreader.next()
            except StopIterationException:
                wx.MessageBox("Selected file appears to contain no data.",
                              "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                return False
    
            input_file.seek(0)
            reader = csv.DictReader(input_file, dialect=dialect)
            # strip extra spaces, so users don't get baffled
            self.fieldnames = [name.strip() for name in reader.fieldnames]
            # read all the data in now, because having it sitting around in
            # memory while we wizard is just easier on the brain.
            # I've written less gross code, but I've written worse, too :P
            self.lines = [line for line in reader]
        
    @property
    def core_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]
    
    def get_unit_dict(self):
        return {name:None for name in self.fieldnames}
    def get_known_metadata(self):
        return {}
    
    def get_data_reader(self, fielddict=None):
        return self.lines
        
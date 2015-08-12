import ipdb
"""
coremetadata.py
* Copyright (c) 2012-2015, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This module lays out the data structure for displaying metadata of cores and
virtual cores
"""


class CoreAttribute(object):
    # Attributes for a Core or CompPlan
    def __init__(self, cplan, name, value, jsonKey):
        self.name = name
        self.value = str(value)  # convert the value to string for display
        self.cplan = cplan
        self.jsonKey = jsonKey

    def __repr__(self):
        return 'Attribute: %s-%s' % (self.name, self.value)

    def toJSON(self):
        key = self.jsonKey
        value = self.value
        return key, value


class CoreGeoAtt(CoreAttribute):
    def __init__(self, cplan, name, value, site, jsonKey='geo'):
        self.lat = value[0]
        self.lon = value[1]
        try:
            self.elev = value[3]
        except:
            self.elev = 'NA'
        self.site = site
        CoreAttribute.__init__(self, cplan, name, [self.lat,
                               self.lon, self.elev], jsonKey)

    def __repr__(self):
        return 'Geo: (' + self.lat + ', ' + self.lon + ', ' + self.elev + ')'

    def toJSON(self):
        key = self.jsonKey
        value = {"type": "Feature",
                       "geometry": {
                            "type": "Point",
                            "coordinates": [self.lat, self.lon, self.elev]
                       },
                       "properties": {
                            "siteName": self.site
                       }}
        return key, value


class CorePubAtt(CoreAttribute):
    # TODO: finish this class to store full publications
    def __init__(self, cplan, name, value, pubtype='article',
                 year='NA', jsonKey='pub'):
        CoreAttribute.__init__(self, cplan, name, value, jsonKey)
        self.author = []
        self.pubtype = pubtype
        self.id = []
        self.pubYear = year

    def toJSON(self):
        key = self.jsonKey
        authlist = []
        for name in self.author:
            authlist.append({'name': name})
        value = {'author': authlist,
                 'type': self.pubtype,
                 'identifier': self.id,
                 'pubYear': self.pubYear}
        return key, value


class DataTable(object):
    def __init__(self, name, fname, jsonKey):
        self.columns = []
        self.name = name
        self.fname = fname
        self.key = jsonKey

    def __toJSON__(self):
        key = self.jsonKey
        # TODO: construct the JSON object
        return key


class PaleoDT(DataTable):
    def __init__(self, name, fname):
        DataTable.__init__(name, fname, 'paleoData')


class ChronDT(DataTable):
    def __init__(self, name, fname):
        DataTable.__init__(name, fname, 'chronData')


class TableColumn(object):
    def __init__(self, num, param, pType, units, desc, dType="", notes=""):
        self.number = num  # column number
        self.parameter = param  # name of the column
        self.parameterType = pType  # measured/inferred
        self.units = units  # engineering units
        self.description = desc  # description
        self.datatype = dType  # string, float, int, bool, etc.
        self.notes = notes

    def __repr__(self):
        return 'Column: ' + self.parameter

    def __toJSON__(self):
        return self.__dict__


class Core(object):
    def cb_default():
        TypeError('callback has not been set')

    # metadata for original imported core, with no computation plan
    def __init__(self, name):
        self.name = name
        self.atts = {}
        self.cps = {}
        self.dataTables = {}
        self._LiPD = {}

    def update_gui_table(self):
        if self.callback:
            self.callback()
        else:
            TypeError('Expected function as argument')

    @property
    def LiPD(self):
        # code to generate LiPD structure
        pass

    def __repr__(self):
        return 'Core: ' + self.name


class CompPlan(Core):
    # metadata for a virtualcore: has a parent core
    def __init__(self, name):
        Core.__init__(self, name)
        del self.cps  # no cps in a cp

    def __repr__(self):
        return 'CP: ' + self.name

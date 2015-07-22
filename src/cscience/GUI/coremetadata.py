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
This module lays out the data structure for displaying metadata of cores and virtual cores
"""

import wx
import json

""" Code adapted from DVC_DataViewModel.py in demo code """

#----------------------------------------------------------------------
# We'll use instaces of these classes to hold our data. Items in the
# tree will get associated back to the coresponding mdCoreAttribute or core object.

class mdCoreAttribute(object):
    # Attributes for a mdCore or mdCompPlan
    def __init__(self, id, cplan, name, value, core, jsonKey):
        self.name = name
        self.value = str(value)  # convert the value to string for display
        self.parent = core
        self.cplan = cplan
        self.id = id
        self.jsonKey = jsonKey

    def __repr__(self):
        return 'Attribute: %s-%s' % (self.name, self.value)
    def toJSON(self):
        key = self.key
        value = self.value
        return key, value

class mdCoreGeoAtt(mdCoreAttribute):
    def __init__(self, id, cplan, name, value, core, jsonKey='geo'):
        self.lat = lat
        self.lon = lon
        self.elev = elev
        mdCoreAttribute.__init__(self,id, cplan, name, [lat, lon, elev], core, jsonKey)

    def __repr__(self):
        return 'Geo: (' + self.lat + ', ' + self.lon + ', ' + self.elev +')'

    def toJSON(self):
        key = self.jsonKey
        value = {"type":"Feature",
                       "geometry":{
                            "type":"Point",
                            "coordinates":[self.lat,self.lon,self.elev]
                       },
                       "properties":{
                            "siteName":self.site
                       }}
        return key, value

class mdCorePubAtt(mdCoreAttribute):
    def __init__(self, id, cplan, name, value, core, jsonKey = 'pub'):
        mdCoreAttribute.__init__(id, cplan, name, value, core, jsonKey)
    def toJSON(self):
        key = self.jsonKey
        value = self.value
        return key, value

class mdDataTable(object):
    def __init__(self, name, fname, jsonKey):
        self.columns = []
        self.name = name
        self.fname = fname
        self.key = jsonKey
    def __toJSON__(self):
        key = jsonKey
        #TODO: construct the JSON object

class mdPaleoDT(mdDataTable):
    def __init__(self, name, fname):
        mdDataTable.__init__(name, fname, 'paleoData')

class mdChronDT(mdDataTable):
    def __init__(self, name, fname):
        mdDataTable.__init__(name, fname, 'chronData')


class mdTableColumn(object):
    def __init__(self, num, param, pType, units, desc, dType="", notes=""):
        self.number = num #column number
        self.parameter = param # name of the column
        self.parameterType = pType # measured/inferred
        self.units = units # engineering units
        self.description = desc # description
        self.datatype = dType # string, float, int, bool, etc.
        self.notes = notes
    def __repr__(self):
        return 'Column: ' + self.parameter
    def __toJSON__(self):
        return self.__dict__

class mdCore(object):
    # metadata for original imported core, with no computation plan
    def __init__(self, name):
        self.name = name
        self.paleoData = []
        self.chronData = []
        self.atts = []
        self.vcs = []

        #TODO: possible get rid of vcs, and infer that from the paleoData/chronData variables

    def __repr__(self):
        return 'Core: ' + self.name

class mdCompPlan(mdCore):
    # metadata for a virtualcore: has a parent core
    def __init__(self,id, parent, name):
        mdCore.__init__(self, name)
        self.parent = parent
        self.id = str(id)

    def __repr__(self):
        return 'CP: ' + self.name

#----------------------------------------------------------------------

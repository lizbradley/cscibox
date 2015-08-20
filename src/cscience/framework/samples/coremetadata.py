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

import sys


class CoreAttribute(object):
    # Attributes for a Core or CompPlan
    def __init__(self, cplan, name, value, jsonKey):
        self.name = name
        self.value = value
        self.cplan = cplan
        self.jsonKey = jsonKey

    def __repr__(self):
        return 'Attribute: %s-%s' % (self.name, self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = str(val)

    @property
    def LiPD(self):
        key = self.jsonKey
        value = self.value
        return key, value


class CoreGeoAtt(CoreAttribute):
    def __init__(self, cplan, name, value, site, jsonKey='geo'):
        self.lat = value[0]
        self.lon = value[1]
        try:
            self.elev = value[3]
        except IndexError:
            self.elev = 'NA'

        self.site = site
        super(self.__class__, self).__init__(cplan, name, [self.lat,
                                             self.lon, self.elev], jsonKey)

    def __repr__(self):
        return 'Geo: (' + str(self.lat) + ', ' + \
            str(self.lon) + ', ' + str(self.elev) + ')'

    @property
    def LiPD(self):
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
        super(self.__class__, self).__init__(cplan, name, value, jsonKey)
        self.author = []
        self.pubtype = pubtype
        self.id = []
        self.pubYear = year

    @property
    def LiPD(self):
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
        self._columns = []
        self.name = name
        self.fname = fname
        self.jsonKey = jsonKey

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val.replace(' ', '_')  # make sure there are no spaces

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, val):
        self._fname = val.replace(' ', '_')  # make sure there are no spaces

    @property
    def LiPD(self):
        key = self.jsonKey
        val = {}
        val['filename'] = self.fname
        val['tableName'] = self.name
        val['columns'] = []
        for col in self.columns:
            val['columns'].append(col.LiPD)

        return key, val

    def get_column_names(self):
        return [col.parameter for col in self._columns]

    @property
    def columns(self):
        return self._columns

    def column_add(self, param, pType, units, desc, dType="", notes=""):
        col = TableColumn(len(self._columns)+1, param, pType, units, desc)
        self._columns.append(col)


# Some small helper classes to reduce clutter for creating DataTables
class InputDT(DataTable):
    def __init__(self, name, fname):
        super(self.__class__, self).__init__(name, fname, 'inputData')


class CompPlanDT(DataTable):
    def __init__(self, name, fname):
        super(self.__class__, self).__init__(name, fname, 'compplanData')


class UncertainDT(DataTable):
    def __init__(self, name, fname):
        super(self.__class__, self).__init__(name, fname, 'uncertainData')


class TableColumn(object):
    # This class is basically representing sample.Attributes in metadata and
    # allowing for small changes required for LiPD (key names, etc.)
    def __init__(self, num, param, pType, units, desc, dType="", notes=""):
        self.number = num  # column number
        self.parameter = param  # name of the column
        self.parameterType = pType  # measured/inferred
        self.units = units  # engineering units
        self.description = desc  # description
        self.datatype = dType  # string, float, int, bool, etc.
        self.notes = notes

    def __repr__(self):
        return 'Column #' + str(self.number) + ': ' + self.parameter

    @property
    def LiPD(self):
        return self.__dict__


class Core(object):
    # metadata for original imported core, with no computation plan
    def __init__(self, name):
        self.name = name
        self.version = 1.0  # not really used right now
        self.archiveType = ""  # not really used right now
        self.investigators = ""  # not really used right now
        self.atts = {}
        self.cps = {}
        self.dataTables = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val.replace(' ', '_')

    def getLiPD(self, cps_out=None):
        # code to generate LiPD structure, this will recurse into computation
        # plans and through dataTables

        # TODO: This is not truly LiPD format because I haven't added in
        # @context. we should consider adding this at some point. I think it is
        # too complex to try adding this, especially for a standard that is
        # still in development. There is a 'real' LiPD example and context file
        # in the 'io' folder.
        LiPD = {}
        LiPD['dataSetName'] = self.name
        LiPD['version'] = self.version

        if not isinstance(self, CompPlan):
            LiPD['archiveType'] = self.archiveType
            LiPD['investigators'] = self.investigators
            # We have GUID's implemented for a similar purpose, this is
            # technically supposed to be DOI
            LiPD['dataDOI'] = self.atts.get('Core GUID', '')

            if cps_out is None:
                # set of the names of cps to be included. Defaults to all if no
                # external argument is provided
                cps_out = set([cp for cp in self.cps])

            for cp in self.cps:
                if cp in cps_out:
                    val = self.cps[cp].getLiPD()
                    LiPD[cp.replace(' ','_')] = val

        for table in self.dataTables:
            key, val = self.dataTables[table].LiPD
            if key not in LiPD.keys():
                LiPD[key] = []
            LiPD[key].append(val)

        for item in self.atts:
            key, val = self.atts[item].LiPD
            LiPD[key] = val

        return LiPD

    def __repr__(self):
        return 'Core: ' + self.name


class CompPlan(Core):
    # metadata for a virtualcore: has a parent core
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        # remove attributes that are only for Cores
        del self.cps
        del self.archiveType
        del self.investigators

    def __repr__(self):
        return 'CP: ' + self.name

"""
user_polling.py

* Copyright (c) 2006-2009, University of Colorado.
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

This module contains stuff to poll the user when I encounter a field I wanted
and don't yet seem to have.
"""

import wx
import wx.html as html
import logging
import urllib2
import httplib


logger = logging.getLogger(__name__)

def result_query(arg):
    dialog = ResultQuery(arg)
    result = None

    if dialog.ShowModal() == wx.ID_OK:
        result = dialog.result
        logger.debug("OK pressed, got resut: {}".format(result))
    dialog.Destroy()

    if "Latitude" in result.keys() and "Longitude" in result.keys():
        # Show the map
        mapDialog = MapDialog("Reservoir Location Map", tuple([result["Latitude"], result["Longitude"]]), result)
        if mapDialog.ShowModal() == wx.ID_OK:
            result = mapDialog.result
            mapDialog.Destroy()
            return result
        else:
            # selection rejected, go back to previous screen
            logger.debug("Rejected reservoir selection, going back to previous screen...")
            mapDialog.Destroy()
            return result_query(arg)
    else:
        logger.debug("Have explicit values for reservoir age correction..use these directly: {}".format(result))
        return result

class BooleanInput(wx.RadioBox):

    def __init__(self, parent):
        super(BooleanInput, self).__init__(parent, wx.ID_ANY, label="",
                                           choices=['Yes', 'No'])

    def get_value(self):
        #not, since we have No in the 1 position
        return not self.GetSelection()

class NumericInput(wx.TextCtrl):

    def __init__(self, parent):
        super(NumericInput, self).__init__(parent, wx.ID_ANY)

        self.SetValue('0')
        self.SetSelection(-1, -1)

        self.Bind(wx.EVT_KILL_FOCUS, self.check_input)
        self.Bind(wx.EVT_SET_FOCUS, self.highlight)

    def check_input(self, event):
        try:
            float(self.GetValue())
        except ValueError:
            self.SetValue('0')
            self.SetBackgroundColour('red')
            self.SetSelection(-1, -1)
        else:
            self.SetBackgroundColour('white')

        event.Skip()

    def highlight(self, event):
        #wait till all selections are actually finshed, then select
        wx.CallAfter(self.SetSelection, -1, -1)
        event.Skip()

    def get_value(self):
        return float(self.GetValue())

class LabelledInput(wx.Panel):

    control_types = {bool: BooleanInput, float: NumericInput}

    def __init__(self, parent, label, input_type):
        super(LabelledInput, self).__init__(parent)

        self.control = self.control_types[input_type](self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=label), flag=wx.ALL, border=2)
        sizer.Add(self.control, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
        self.SetSizer(sizer)

    def get_value(self):
        return self.control.get_value()


class PollingDialog(wx.Dialog):

    def __init__(self, caption):
        super(PollingDialog, self).__init__(None, title=caption, style=wx.CAPTION)

        self.controls = {}

        scrolledwindow = wx.ScrolledWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.setup_window(scrolledwindow, sizer)

        scrolledwindow.SetSizer(sizer)
        scrolledwindow.SetScrollRate(20, 20)
        scrolledwindow.EnableScrolling(True, True)

        self.finish_ui(scrolledwindow)
        scrolledwindow.Layout()
        self.Centre()

    def create_control(self, name, tp, parent):
        ctrl = LabelledInput(parent, name, tp)
        self.controls[name] = ctrl
        return ctrl

class ResultQuery(PollingDialog):

    def __init__(self, argument):
        self.argument = argument
        super(ResultQuery, self).__init__("Please check results")

    def setup_window(self, window, sizer):
        for name, tp in self.argument.conclusion.result:
            sizer.Add(self.create_control(name, tp, window),
                      flag=wx.EXPAND | wx.ALL, border=3)

    def finish_ui(self, controlswindow):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(self,
            label='Suggested Values for {}'.format(self.argument.conclusion.name)),
                  flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
        sizer.Add(wx.StaticText(self,
            label=str(self.argument.conclusion.result)),
                  flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)

        sizer.Add(controlswindow, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)

        sizer.Add(wx.Button(self, wx.ID_OK), flag=wx.CENTER|wx.TOP, border=5)

        self.SetSizer(sizer)
        #self.SetSize(wx.Size(400, 480))
        # self.SetAutoLayout(True)
        # sizer.Fit(self)

    @property
    def result(self):
        res = {}
        for name, tp in self.argument.conclusion.result:
            # If any of these fields has a value, just sent these forward
            if self.controls[name].get_value() is not 0:
                res[name] = self.controls[name].get_value()
        if len(res) is 0:
            res = dict([(name, ctrl.get_value()) for name, ctrl in self.controls.items()])

        return res

class MapDialog(wx.Dialog):


    def internet_on(self):
        try:
            response=urllib2.urlopen('http://74.125.224.72',timeout=1)
            return True
        except (urllib2.URLError, httplib.BadStatusLine) as err: pass
        return False

    def __init__(self, caption, coordinates, previous_result):
        super(MapDialog, self).__init__(None, title=caption, style=wx.CAPTION)

        self.coordinates = coordinates
        self._previous_result = previous_result
        self._previous_result.pop('Latitude', None)
        self._previous_result.pop('Longitude', None)
        self._closest_point = None

        self._closest_point = self.getClosestReservoirAdjustment(self.coordinates[0], self.coordinates[1])
        self.reservoir_coordinates = self._closest_point[0]

        logger.debug("Input coordinates = ({}, {})".format(self.coordinates[0], self.coordinates[1]))
        logger.debug("Closest coordinates = ({}, {})".format(self.reservoir_coordinates[0], self.reservoir_coordinates[1]))

        self.browser = html.HtmlWindow(self, wx.ID_ANY, size=wx.Size(400, 300))

        sizer = wx.BoxSizer(wx.VERTICAL)

        if self.internet_on():
            # We have an internet
            sizer.Add(self.browser, flag=wx.EXPAND | wx.ALL, border=0)

            h_sizer = wx.BoxSizer(wx.HORIZONTAL)
            h_sizer.Add(wx.StaticText(self, label="R = Reservoir Location"),flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
            h_sizer.Add(wx.StaticText(self, label="S = Sample Location"),flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)

            sizer.Add(h_sizer)

            html_string = "<html xmlns=\"http://www.w3.org/1999/xhtml\"><img src=\"http://maps.googleapis.com/maps/api/staticmap?size=400x300&markers=color:blue|label:S|{0},{1}&markers=color:red|label:R|{2},{3}\"</img></html>".format(self.coordinates[0], self.coordinates[1], self.reservoir_coordinates[0], self.reservoir_coordinates[1])

            logger.debug("HTML = {}".format(html_string))

            self.browser.SetPage(html_string)
        else:
            # No network connection, fallback to textual display (no map)
            sizer.Add(wx.StaticText(self, label="Selected Reservoir Coordinates:"),flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
            sizer.Add(wx.StaticText(self, label="{0}, {1}".format(self.reservoir_coordinates[0], self.reservoir_coordinates[1])),flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
            sizer.Add(wx.StaticText(self, label="Reservoir Age: {0}, Error: {1}".format(self._closest_point[1]['Correction'], self._closest_point[1]['Error'])),flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)


        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(wx.Button(self, wx.ID_CANCEL, label="Reject Selection"), flag=wx.CENTER|wx.ALL, border=5)
        button_sizer.Add(wx.Button(self, wx.ID_OK, label="Accept Selection"), flag=wx.CENTER|wx.ALL, border=5)

        sizer.Add(button_sizer, flag=wx.CENTER|wx.TOP, border = 5)

        self.SetSizer(sizer)
        self.Centre()
        self.SetSize(wx.Size(410, 400))

    @property
    def result(self):
        self._previous_result['+/- Adjustment Error'] = self._closest_point[1]['Error']
        self._previous_result['Adjustment'] = self._closest_point[1]['Correction']
        logger.debug("Returning updated reservoir correction: {}".format(self._previous_result))
        return self._previous_result


    def haversine(self, lon1, lat1, lon2, lat2):
        from math import radians, cos, sin, asin, sqrt
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # 6367 km is the radius of the Earth
        km = 6367 * c
        return km

    def getClosestReservoirAdjustment(self, sample_lat, sample_long):
        from cscience import datastore
        datastore = datastore.Datastore()
        milieus = datastore.milieus['ReservoirLocations']
        distance = -1
        closest_point = None
        closest_point_value = None
        for key, value in milieus.iteritems():
            if value['Correction'] is not None and value['Error'] is not None:
                new_distance = self.haversine(sample_long, sample_lat, key[1], key[0])
                if new_distance < distance or distance == -1:
                    distance = new_distance
                    closest_point = key
                    closest_point_value = value

        return tuple([closest_point, closest_point_value])

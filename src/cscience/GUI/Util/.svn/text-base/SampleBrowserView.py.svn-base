"""
SampleBrowserView.py

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
"""

class SampleBrowserView(object):

    view_key      = "windows/samplebrowser/view"
    filter_key    = "windows/samplebrowser/filter"
    primary_key   = "windows/samplebrowser/primary"
    secondary_key = "windows/samplebrowser/secondary"
    direction_key = "windows/samplebrowser/direction"

    def __init__(self, config):
        self.config    = config
        self.view      = self.config.Read(SampleBrowserView.view_key, "Required Inputs")
        self.filter    = self.config.Read(SampleBrowserView.filter_key, "<No Filter>")
        self.primary   = self.config.Read(SampleBrowserView.primary_key, "id")
        self.secondary = self.config.Read(SampleBrowserView.secondary_key, "experiment")
        self.direction = self.config.Read(SampleBrowserView.direction_key, "Ascending")

    def get_view(self):
        return self.view

    def set_view(self, new_view):
        self.view = new_view
        self.config.Write(SampleBrowserView.view_key, new_view)

    def get_filter(self):
        return self.filter

    def set_filter(self, new_filter):
        self.filter = new_filter
        self.config.Write(SampleBrowserView.filter_key, new_filter)

    def get_primary(self):
        return self.primary

    def set_primary(self, new_primary):
        self.primary = new_primary
        self.config.Write(SampleBrowserView.primary_key, new_primary)

    def get_secondary(self):
        return self.secondary

    def set_secondary(self, new_secondary):
        self.secondary = new_secondary
        self.config.Write(SampleBrowserView.secondary_key, new_secondary)

    def get_direction(self):
        return self.direction

    def set_direction(self, new_direction):
        self.direction = new_direction
        self.config.Write(SampleBrowserView.direction_key, new_direction)

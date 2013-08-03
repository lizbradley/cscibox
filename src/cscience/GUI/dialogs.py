"""
dialogs.py

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

A collection of small dialogs useful to ACE's gui/editors.
"""

import wx
import wx.html
import wx.lib.hyperlink

from cscience.framework import samples
from cscience.GUI import events

def field_dialog(name, query_name):
    #TODO: this might be better done with a metaclass? not sure.
    class EditField(wx.Dialog):
        def __init__(self, parent, att='', att_type='float', att_unit='',
                           query_val=False, in_use=False):
            super(EditField, self).__init__(parent, wx.ID_ANY, 
                    (att and 'Edit %s' or 'Add %s') % name)
            
            att_type = (att_type or 'float').capitalize()
            name_label = wx.StaticText(self, wx.ID_ANY, "%s Name" % name)
            type_label = wx.StaticText(self, wx.ID_ANY, "%s Type" % name)
            unit_label = wx.StaticText(self, wx.ID_ANY, "%s Units" % name)
            query_label = wx.StaticText(self, wx.ID_ANY, "Is %s?" % query_name)
            uncertainty_label = wx.StaticText(self, wx.ID_ANY, "Generate Uncertainty Attributes?")
    
            self.name_box = wx.TextCtrl(self, wx.ID_ANY, att, size=(150, -1))
            self.type_box = wx.ComboBox(self, wx.ID_ANY, value=att_type, 
                    choices=samples.TYPES, style=wx.CB_DROPDOWN | wx.CB_READONLY)
            self.unit_box = wx.ComboBox(self, wx.ID_ANY, 
                                        choices=samples.standard_cal_units, 
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY)
            self.query_box = wx.CheckBox(self, wx.ID_ANY)
            self.query_box.SetValue(query_val)
            self.error_box = wx.CheckBox(self, wx.ID_ANY)
            self.error_box.SetValue(True)
    
            btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
            sizer = wx.GridBagSizer(3, 3)
            sizer.Add(name_label, pos=(0, 0), border=5, 
                      flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
            sizer.Add(type_label, pos=(0, 1), border=5, 
                      flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
            sizer.Add(unit_label, pos=(0,2), border=5,
                      flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
            sizer.Add(query_label, pos=(0, 3), border=5, 
                      flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
            sizer.Add(uncertainty_label, pos=(0, 4), border=5, 
                      flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM) 
            sizer.Add(self.name_box, pos=(1, 0), border=5, 
                      flag=wx.ALIGN_LEFT | wx.ALL)
            sizer.Add(self.type_box, pos=(1, 1), border=5, 
                      flag=wx.ALIGN_LEFT | wx.ALL)
            sizer.Add(self.unit_box, pos=(1,2), border=5,
                      flag=wx.ALIGN_LEFT | wx.ALL)
            sizer.Add(self.query_box, pos=(1, 3), border=5, 
                      flag=wx.ALIGN_LEFT | wx.ALL)
            sizer.Add(self.error_box, pos=(1, 4), border=5, 
                      flag=wx.ALIGN_LEFT | wx.ALL)
            sizer.Add(btnsizer, pos=(2, 0), border=5, span=(1, 5), 
                      flag=wx.ALIGN_CENTER | wx.ALL)
            
            if in_use:
                self.name_box.Disable()
                self.type_box.Disable()
    
            self.SetSizer(sizer)
            sizer.Fit(self)
            self.Centre(wx.BOTH)
    
        @property
        def field_unit(self):
            return self.unit_box.GetValue()
        @property
        def field_name(self):
            return self.name_box.GetValue()
        @property
        def field_type(self):
            return self.type_box.GetValue().lower()
        @property
        def has_uncertainty(self):
            return self.error_box.GetValue()
        
    #create is_attribute/is_key/etc property
    setattr(EditField, 'is_%s' % query_name.lower(), 
            property(lambda self:self.query_box.GetValue()))
    return EditField

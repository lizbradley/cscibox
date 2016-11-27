"""
AttEditor.py

* Copyright (c) 2006-2013, University of Colorado.
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

import wx
import wx.lib.agw.hypertreelist as HTL
from cscience import datastore
from cscience.framework import datastructures, Attribute
from cscience.GUI import events
from cscience.GUI.Editors import MemoryFrame

datastore = datastore.Datastore()

class AddAttribute(wx.Dialog):
    def __init__(self, parent, typeset):
        super(AddAttribute, self).__init__(parent, wx.ID_ANY, "Add Attribute")

        name_label = wx.StaticText(self, wx.ID_ANY, "Name")
        self.name_box = wx.TextCtrl(self, wx.ID_ANY, size=(150, -1))
        type_label = wx.StaticText(self, wx.ID_ANY, "Type")
        self.type_box = wx.ComboBox(self, wx.ID_ANY, value='Float',
                choices=typeset, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.query_box = wx.CheckBox(self, wx.ID_ANY, "Is Output?")

        self.numericpanel = wx.Panel(self, wx.ID_ANY)
        unitlabel = wx.StaticText(self.numericpanel, wx.ID_ANY, "Units")
        self.unit_box = wx.ComboBox(self.numericpanel, wx.ID_ANY,
                                    choices=datastructures.standard_cal_units,
                                    style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.unit_box.Select(0)
        self.error_box = wx.CheckBox(self.numericpanel, wx.ID_ANY, 'Has Error?')
        numsizer = wx.BoxSizer(wx.VERTICAL)
        unitsizer = wx.BoxSizer(wx.HORIZONTAL)
        unitsizer.Add(unitlabel, border=5, flag=wx.ALL)
        unitsizer.Add(self.unit_box, border=5, flag=wx.ALL)
        numsizer.Add(unitsizer)
        numsizer.Add(self.error_box, border=5, flag=wx.ALL)
        self.numericpanel.SetSizer(numsizer)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.GridBagSizer()
        sizer.Add(name_label, pos=(0, 0), span=(1,1), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.name_box, pos=(0, 1), span=(1,1), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)

        sizer.Add(type_label, pos=(1, 0), span=(1,1), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.type_box, pos=(1, 1), span=(1,1), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.numericpanel, pos=(2, 1), span=(2, 2), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)

        sizer.Add(self.query_box, pos=(4, 0), span=(1,2), border=5,
                  flag=wx.ALIGN_LEFT | wx.ALL)

        sizer.Add(btnsizer, pos=(5, 0), border=5, span=(1, 3),
                  flag=wx.ALIGN_CENTER | wx.ALL)


        self.Bind(wx.EVT_COMBOBOX, self.type_updated, self.type_box)
        self.SetSizerAndFit(sizer)
        self.Centre(wx.BOTH)

    def type_updated(self, event=None):
        numeric = datastructures.is_numeric(self.type_box.GetValue())
        if not numeric:
            self.unit_box.Select(0)
            self.error_box.SetValue(False)
        self.numericpanel.Enable(numeric)

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
    def is_output(self):
        return self.query_box.GetValue()
    @property
    def has_error(self):
        return self.error_box.GetValue()

class AttributeTreeList(HTL.HyperTreeList):
    #TODO: this would really look a lot better with alternating background colors
    labels = ['Attribute', 'Type', 'Unit', 'Is Output?', 'Has Error?']

    def __init__(self, data, *args, **kwargs):
        self.data = data
        if 'style' in kwargs:
            style = kwargs['agwStyle']
        else:
            style = 0
        kwargs['agwStyle'] = style | HTL.TR_HAS_BUTTONS | HTL.TR_HIDE_ROOT | \
                                HTL.TR_SINGLE | HTL.TR_FULL_ROW_HIGHLIGHT | \
                                HTL.TR_TWIST_BUTTONS | HTL.TR_NO_LINES | \
                                HTL.TR_ELLIPSIZE_LONG_ITEMS | \
                                HTL.TR_HAS_VARIABLE_ROW_HEIGHT
       # HTL.TR_VIRTUAL

        HTL.HyperTreeList.__init__(self, *args, **kwargs)
        self.AddColumn('Attribute')
        self.AddColumn('Type', 60)
        self.AddColumn('Unit', 80)
        self.AddColumn('Has Error?', flag=wx.ALIGN_CENTER)
        self.AddColumn('Is Output?', flag=wx.ALIGN_CENTER)
        self.SetMainColumn(0)
        self.SetBackgroundColour(wx.WHITE)
        self.root = self.AddRoot("The Root Item (Should never see)")
        #TODO: this would look nicer with a larger font size
        self.refresh_view()

    #Probably a better way to do this than deleting all the items and
    #repopulating, but this works for now.
    def update_items(self):
        def as_check(value):
            if value:
                return unichr(10003)
            else:
                return 'X'

        self.DeleteChildren(self.root)
        for att in self.data:
            if att.is_virtual:
                continue
            new_item = self.AppendItem(self.root, att.name)
            self.SetPyData(new_item, att)
            self.SetItemText(new_item, att.type_.title(), 1)
            self.SetItemText(new_item, as_check(att.output), 4)
            if att.is_numeric():
                self.SetItemText(new_item, att.unit, 2)
                self.SetItemText(new_item, as_check(att.has_error), 3)


    def refresh_view(self):
        self.update_items()
        maxext = max(80, max([0] + [self.GetTextExtent(name)[0]
                    for name in self.data.keys()]))
        maxext += 25
        self.SetColumnWidth(0, maxext)
        self.Refresh()


class AttEditor(MemoryFrame):

    framename = 'atteditor'

    def __init__(self, parent):
        ds = wx.DisplaySize()
        super(AttEditor, self).__init__(parent, id=wx.ID_ANY,
                                        title='Attribute Editor', size=(ds[0]/2, ds[1]/2))

        self.SetBackgroundColour(wx.Colour(215,215,215))

        sampletext = wx.StaticText(self, wx.ID_ANY, "Sample Attributes")
        titlefont = sampletext.GetFont().Bold().MakeLarger()
        sampletext.SetFont(titlefont)
        self.sampleadd_button = wx.Button(self, wx.ID_ANY, "Add...")
        ssizer = wx.BoxSizer(wx.HORIZONTAL)
        ssizer.Add(sampletext, border=10, flag=wx.ALL | wx.EXPAND)
        ssizer.Add(self.sampleadd_button, border=10, flag=wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
        self.samplectrl = AttributeTreeList(datastore.sample_attributes, self, wx.ID_ANY)

        coretext = wx.StaticText(self, wx.ID_ANY, "Core Attributes")
        coretext.SetFont(titlefont)
        self.coreadd_button = wx.Button(self, wx.ID_ANY, "Add...")
        csizer = wx.BoxSizer(wx.HORIZONTAL)
        csizer.Add(coretext, border=10, flag=wx.ALL | wx.EXPAND)
        csizer.Add(self.coreadd_button, border=10, flag=wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self.corectrl = AttributeTreeList(datastore.core_attributes, self, wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ssizer, flag=wx.ALIGN_CENTER)
        sizer.Add(self.samplectrl, border=10, flag=wx.EXPAND | wx.ALL, proportion=1)
        sizer.Add(csizer, flag=wx.ALIGN_CENTER)
        sizer.Add(self.corectrl, border=10, flag=wx.EXPAND | wx.ALL, proportion=1)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.add_sample_attribute, self.sampleadd_button)
        self.Bind(wx.EVT_BUTTON, self.add_core_attribute, self.coreadd_button)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        self.SetInitialSize(wx.Size(600, 600))

    def on_repository_altered(self, event):
        if 'attributes' in event.changed:
            self.samplectrl.refresh_view()
            self.corectrl.refresh_view()
        event.Skip()

    def do_add_dlg(self, typelist, collection):
        # TODO: I think it would be an improvement to change this so that the
        # attributes are modified within the list itself, and the add attribute
        # button just adds a new row to the list for the user to fill out.
        # Not going to worry about it right now, though.
        dlg = AddAttribute(self, typelist)
        if dlg.ShowModal() == wx.ID_OK:
            if not dlg.field_name:
                return
            if dlg.field_name not in collection:

                collection.add_attribute(dlg.field_name,
                                dlg.field_type, dlg.field_unit, dlg.is_output,
                                dlg.has_error)
                events.post_change(self, 'attributes')
            else:
                wx.MessageBox('Attribute "%s" already exists!' % dlg.field_name,
                        "Duplicate Attribute", wx.OK | wx.ICON_INFORMATION)

        dlg.Destroy()

    def add_sample_attribute(self, event=None):
        self.do_add_dlg(datastructures.SIMPLE_TYPES, datastore.sample_attributes)

    def add_core_attribute(self, event=None):
        self.do_add_dlg(datastructures.TYPES, datastore.core_attributes)

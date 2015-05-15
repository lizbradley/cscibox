"""
MilieuBrowser.py

* Copyright (c) 2006-2015, University of Colorado.
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

import os
import wx
import wx.gizmos as gizmos
import wx.grid

import csv
from cscience import datastore
from cscience.GUI.Util import grid, FunctionValidator
from cscience.GUI.Editors import MemoryFrame
from cscience.GUI import events

datastore = datastore.Datastore()

class MilieuGridTable(grid.UpdatingTable):
    def __init__(self, *args, **kwargs):
        self._milieu = {}
        self.template = {}
        super(MilieuGridTable, self).__init__(*args, **kwargs)

    def reset_view(self):
        super(MilieuGridTable, self).reset_view()
        #Need to re-create these or wx apparently gc's them unexpectedly :P
        base_attrs = wx.grid.GridCellAttr()
        base_attrs.SetBackgroundColour(self.grid.DefaultCellBackgroundColour)
        base_attrs.SetFont(self.grid.DefaultCellFont)
        if self.template:
            key_attrs = wx.grid.GridCellAttr()
            key_attrs.SetBackgroundColour('light grey')
            font = self.grid.GetDefaultCellFont()
            font.SetWeight(wx.BOLD)
            key_attrs.SetFont(font)

            for col in xrange(len(self.template.key_fields)):
                self.grid.SetColAttr(col, key_attrs)
            for col in xrange(len(self.template.key_fields)):
                self.grid.SetColAttr(col, base_attrs)
        else:
            self.grid.SetColAttr(0, base_attrs)

    @property
    def milieu(self):
        return self._milieu
    @milieu.setter
    def milieu(self, value):
        self._milieu = value or {}
        if value:
            self.template = value.template
            self.sorted_keys = sorted(self.milieu.keys())
            self.milieu.preload()
        else:
            self.template = {}
        self.reset_view()

    def GetNumberRows(self):
        return len(self.milieu) or 1
    def GetNumberCols(self):
        return len(self.template) or 1
    def GetValue(self, row, col):
        if not self.milieu:
            return "Select a Paleobase Milieu"
        mrow = self.sorted_keys[row]
        if col < len(self.template.key_fields):
            return mrow[col]
        else:
            return self.milieu[mrow][self.template.keys()[col]]

    def GetRowLabelValue(self, row):
        return ''
    def GetColLabelValue(self, col):
        if not self.milieu:
            return "No Milieu Selected"
        return self.template.keys()[col]

class MilieuBrowser(MemoryFrame):

    framename = 'milieubrowswer'

    def __init__(self, parent):
        super(MilieuBrowser, self).__init__(parent, id=wx.ID_ANY, title='Paleobase Browser')


        menu_bar = wx.MenuBar()
        edit_menu = wx.Menu()
        copy_item = edit_menu.Append(wx.ID_COPY, "Copy\tCtrl-C",
                                     "Copy selected Paleobase items")
        edit_menu.Enable(wx.ID_COPY, False)
        menu_bar.Append(edit_menu, "Edit")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.copy, copy_item)
        self.menu_bar = wx.MenuBar()
        self.SetBackgroundColour(wx.Colour(215,215,215))
        self.milieu_label = wx.StaticText(self, wx.ID_ANY, "(No Milieu Selected)")
        self.milieus_list = wx.ListBox(self, wx.ID_ANY,
                                       choices=sorted(datastore.milieus),
                                       style=wx.LB_SINGLE)

        self.grid = grid.LabelSizedGrid(self, wx.ID_ANY)
        self.table = MilieuGridTable(self.grid)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)

        self.add_button = wx.Button(self, wx.ID_ANY, "Create New Milieu...")

        #TODO: try out "add many"
        sz = wx.FlexGridSizer(2, 2, 10, 10)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Paleobase Milieus"))
        sz.Add(self.milieu_label)
        sz.Add(self.milieus_list, proportion=1, flag=wx.EXPAND)
        sz.Add(self.grid, proportion=1, flag=wx.EXPAND)
        sz.AddGrowableRow(1)
        sz.AddGrowableCol(0)
        sz.AddGrowableCol(1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sz, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.add_button, border=5, flag=wx.ALL)

        self.SetSizer(sizer)

        # DEBUG this must be a nonblocking call....
        self.Bind(wx.EVT_LISTBOX, self.select_milieu, self.milieus_list)
        self.Bind(wx.EVT_BUTTON, self.create_new_milieu, self.add_button)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.allow_copy, self.grid)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)

    def allow_copy(self, event):
        menu_bar = self.GetMenuBar()
        edit = menu_bar.GetMenu(menu_bar.FindMenu("Edit"))
        edit.Enable(wx.ID_COPY, bool(self.grid.SelectedRows))

    def copy(self, event):
        rowtext = ['\t'.join(self.table.template.keys())]
        for row in self.grid.SelectedRows:
            rowtext.append('\t'.join([str(self.table.GetValue(row, col)) for col in
                                      range(self.table.GetNumberCols())]))

        data = wx.TextDataObject()
        data.SetText(os.linesep.join(rowtext))
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def on_repository_altered(self, event):
        if 'milieus' in event.changed:
            self.milieus_list.Set(sorted(datastore.milieus.keys()))
            if event.value:
                try:
                    new_index = self.milieus_list.GetItems().index(event.value)
                except ValueError:
                    pass
                else:
                    #bah, there's no good way to make this fire an event
                    self.milieus_list.SetSelection(new_index)
                    self.select_milieu()
        event.Skip()

    def select_milieu(self, event=None):
        name = self.milieus_list.GetStringSelection()
        mil = datastore.milieus[name]
        self.milieu_label.SetLabel("Milieu %s; Template Type: %s" %
                                      (mil.name, mil.template.name))
        self.grid.ClearSelection()
        self.table.milieu = mil

    def create_new_milieu(self, event):
        dlg = CreateMilieu(self)
        if dlg.ShowModal() == wx.ID_OK:
            template = datastore.templates[dlg.template]
            #TODO: handle errors!
            #TODO: waiting cursor!
            with open(dlg.path, 'rU') as input_file:
                coll = template.new_milieu(csv.DictReader(input_file, dlg.order))
            coll.name = dlg.name
            datastore.milieus.add(coll)
            events.post_change(self, 'milieus', coll.name)
        dlg.Destroy()

class CreateMilieu(wx.Dialog):
    def name_validator(self):
        def validator(self, *args, **kwargs):
            control = self.GetWindow()
            name = control.GetValue()

            def show_error(text, title):
                control.SetValue('')
                control.SetBackgroundColour("pink")
                wx.MessageBox(text, title, wx.OK | wx.ICON_INFORMATION)
                control.SetFocus()
                control.Refresh()

            if not name:
                show_error('Milieu name not specified!', "Illegal Milieu Name")
                return False
            elif name in datastore.milieus:
                show_error('Milieu "%s" already exists!' % name,
                           "Duplicate Milieu Name")
                return False
            else:
                control.SetBackgroundColour(
                        wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                control.Refresh()
                return True
        return FunctionValidator(validator)

    def content_validator(self, getter, message, name):
        def validator(self, *args, **kwargs):
            control = self.GetWindow()
            if not getattr(control, getter)():
                control.SetBackgroundColour("pink")
                wx.MessageBox(message, "Illegal %s Name" % name,
                              wx.OK | wx.ICON_INFORMATION)
                control.SetFocus()
                control.Refresh()
                return False
            else:
                control.SetBackgroundColour(
                        wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                control.Refresh()
                return True
        return FunctionValidator(validator)

    def __init__(self, parent):
        #TODO: this guy needs to be resizable!
        super(CreateMilieu, self).__init__(parent, wx.ID_ANY, 'Create Milieu')
        self.was_valid = None
        template_names = sorted(datastore.templates)

        name_label = wx.StaticText(self, wx.ID_ANY, "Milieu Name")
        type_label = wx.StaticText(self, wx.ID_ANY, "Based On")
        path_label = wx.StaticText(self, wx.ID_ANY, "Path to CSV File")

        curtype = template_names[0]
        self.name_box = wx.TextCtrl(self, wx.ID_ANY, size=(150, -1),
                validator=self.name_validator())
        self.type_box = wx.ComboBox(self, wx.ID_ANY, value=curtype,
                choices=template_names, style=wx.CB_DROPDOWN | wx.CB_READONLY,
                validator=self.content_validator('GetValue',
                                    'Template name not specified!', 'Template'))
        self.path_box = wx.FilePickerCtrl(self, wx.ID_ANY, wildcard='*.csv',
                message="Select a CSV File that contains data for this milieu",
                validator=self.content_validator('GetPath',
                                    'Problem with Path Name!', 'Path'))
        self.order_box = gizmos.EditableListBox(self, wx.ID_ANY,
                'Select Field Order     ', style=0) #just up/down buttons
        self.order_box.Strings = datastore.templates[curtype].keys()

        buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_COMBOBOX, self.change_template, self.type_box)

        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(name_label, pos=(1, 0), span=(2, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(type_label, pos=(3, 0), span=(2, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(path_label, pos=(5, 0), span=(2, 1), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.name_box, pos=(1, 1), span=(2, 1), flag=wx.SHAPED | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.type_box, pos=(3, 1), span=(2, 1), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.path_box, pos=(5, 1), span=(2, 1), flag=wx.SHAPED | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.order_box, pos=(0, 2), span=(7, 1), flag=wx.EXPAND | wx.ALL)
        sizer.Add(buttons, pos=(7, 0), span=(1, 3), flag=wx.EXPAND | wx.ALL)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableCol(2)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def change_template(self, event):
        self.order_box.Strings = datastore.templates[event.GetString()].keys()

    @property
    def name(self):
        return self.name_box.GetValue()
    @property
    def template(self):
        return self.type_box.GetValue()
    @property
    def path(self):
        return self.path_box.GetPath()
    @property
    def order(self):
        return self.order_box.Strings

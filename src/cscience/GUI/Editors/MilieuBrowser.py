"""
MilieuBrowser.py

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

import os
import wx
import wx.grid

from cscience import datastore
from cscience.GUI.Editors import MemoryFrame

class MilieuBrowser(MemoryFrame):
    
    framename = 'milieubrowswer'
    
    def __init__(self, parent):
        super(MilieuBrowser, self).__init__(parent, id=wx.ID_ANY, title='Paleobase Browser')

        self.menu_bar = wx.MenuBar()
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected paleobase items.")
        
        editMenu.Enable(wx.ID_COPY, False)
        
        self.menu_bar.Append(editMenu, "Edit")

        self.SetMenuBar(self.menu_bar)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)
        
        collectionsLabel = wx.StaticText(self, wx.ID_ANY, "Data Collections")
        self.collectionLabel = wx.StaticText(self, wx.ID_ANY, "Data Collection Type: <None>")
        
        self.collection = None        
        self.collections_list = wx.ListBox(self, wx.ID_ANY, choices=sorted(datastore.milieus), 
                                           style=wx.LB_SINGLE)

        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "No Collection Selected.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)

        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.selected_rows = set()

        self.ConfigureGrid()

        self.add_button = wx.Button(self, wx.ID_ANY, "Create Data Collection...")
                
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(collectionsLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.collections_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        
        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(self.collectionLabel)
        columnTwoSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.add_button, border=5, flag=wx.ALL)

        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL)
        
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.OnCreateCollection, self.add_button)
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.collections_list)

        self.collections_list.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)


    # list box controls do not deliver deselection events when in 'single selection' mode
    # but it is still possible for the user to clear the selection from such a list
    # as such, we need to monitor the LEFT_UP events for each of our list boxes and
    # check to see if the selection got cleared without us knowning about it
    # if so, we need to update the user interface appropriately
    # this code falls under the category of "THIS SUCKS!" It would be much cleaner to
    # just be informed of list deselection events
    def OnLeftUp(self, event):
        index = self.collections_list.GetSelection()
        if index == -1:
            self.collection = None
            self.ConfigureGrid()
            self.collectionLabel.SetLabel("Data Collection Type: <None>")
            self.Layout()
        event.Skip()

    def ConfigureGrid(self):
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        if not self.collection:
            self.grid.AppendRows(1)
            self.grid.AppendCols(1)
            self.grid.SetCellValue(0, 0, "No Collection Selected.")
            self.grid.SetRowLabelValue(0, "")
            self.grid.SetColLabelValue(0, "")
            self.grid.AutoSize()
        else:
            self.grid.AppendRows(len(self.collection))
            self.grid.AppendCols(len(self.template))

            for column, key in enumerate(self.template):
                self.grid.SetColLabelValue(column, key)
            
            for row, key in enumerate(sorted(self.collection.keys())):
                self.grid.SetRowLabelValue(row, "")                
                for col, subkey in enumerate(key):
                    self.grid.SetCellValue(row, col, str(subkey))
                #Iterate using the template to ensure ordering consistency.
                for col, att in enumerate(self.template.iter_nonkeys(), len(key)):
                    self.grid.SetCellValue(row, col, str(self.collection[key][att]))
            self.grid.AutoSize()
            
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def OnRangeSelect(self, event):

        start = event.GetTopLeftCoords()[0]
        stop = event.GetBottomRightCoords()[0]
        
        if event.Selecting():
            for i in range(start, stop + 1):
                self.selected_rows.add(i)
        else:
            for i in range(start, stop + 1):
                if i in self.selected_rows:
                    self.selected_rows.remove(i)
            
        editMenu = self.menu_bar.GetMenu(self.menu_bar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            editMenu.Enable(wx.ID_COPY, True)

    def OnCopy(self, event):
        indexes = sorted(list(self.selected_rows))

        cols = self.grid.GetNumberCols()
        
        result = ""
        
        for i in range(cols):
            result = result + self.grid.GetColLabelValue(i) + "\t"
            
        result = result[0:-1]
        result = result + os.linesep
        
        for row in indexes:
            for col in range(cols):
                result = result + self.grid.GetCellValue(row, col) + "\t"
            result = result[0:-1]
            result = result + os.linesep

        data = wx.TextDataObject()
        data.SetText(result)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def OnCreateCollection(self, event):
        dlg = CreateMilieu(self)
        dlg.ShowModal()
        if dlg.valid:
            if dlg.name in datastore.milieus:
                wx.MessageBox('Collection "%s" already exists!' % dlg.name, 
                        "Duplicate Collection", wx.OK | wx.ICON_INFORMATION)
            else:
                template = datastore.templates[dlg.template]
                #TODO: handle errors!
                coll = template.new_milieu(dlg.path)
                coll.name = dlg.name
                datastore.milieus.add(coll)
                self.collections_list.Set(sorted(datastore.milieus))
                datastore.data_modified = True
        dlg.Destroy()

    def OnSelect(self, event):
        name = self.collections_list.GetStringSelection()
        self.collection = datastore.milieus[name]
        self.template = self.collection.template
        self.collectionLabel.SetLabel("Data Collection Type: %s" % (self.template.name))
        self.grid.ClearSelection()
        self.ConfigureGrid()
        self.Layout()
        
        
class CreateMilieu(wx.Dialog):
    def __init__(self, parent):
        super(CreateMilieu, self).__init__(parent, wx.ID_ANY, 
                                               'Create Milieu')
        self.was_valid = None
        template_names = sorted(datastore.templates)

        name_label = wx.StaticText(self, wx.ID_ANY, "Milieu Name")
        type_label = wx.StaticText(self, wx.ID_ANY, "Based On")
        path_label = wx.StaticText(self, wx.ID_ANY, "Path to CSV File")

        self.name_box = wx.TextCtrl(self, wx.ID_ANY, size=(150, -1))
        self.type_box = wx.ComboBox(self, wx.ID_ANY, value=template_names[0], 
                choices=template_names, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.path_box = wx.FilePickerCtrl(self, wx.ID_ANY, wildcard='*.csv',
                message="Select a CSV File that contains data for this milieu")
        buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)

        sizer = wx.GridBagSizer(4, 3)
        sizer.Add(name_label, pos=(0, 0), border=10, 
                  flag=wx.ALIGN_RIGHT | wx.ALL)
        sizer.Add(type_label, pos=(1, 0), border=10, 
                  flag=wx.ALIGN_RIGHT | wx.ALL)
        sizer.Add(path_label, pos=(2, 0), border=10, 
                  flag=wx.ALIGN_RIGHT | wx.ALL)
        sizer.Add(self.name_box, pos=(0, 1), border=10, 
                  flag=wx.EXPAND | wx.ALL)
        sizer.Add(self.type_box, pos=(1, 1), border=10, 
                  flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.path_box, pos=(2, 1), border=10, 
                  flag=wx.EXPAND | wx.ALL)
        sizer.Add(buttons, pos=(3, 0), border=10, span=(1, 3),
                  flag=wx.EXPAND | wx.ALL)
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)
        sizer.Fit(self)

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
    def valid(self):
        #Note: ideally this should use proper validators/close event vetos,
        #but I can't seem to get those to work on this dialog. This compromise
        #seems reasonable under the circumstances.
        if self.was_valid is None:
            def invalid(error, title):
                wx.MessageBox(error, title, wx.OK | wx.ICON_INFORMATION)
                self.was_valid = False
        
            if self.GetReturnCode() == wx.ID_OK:
                if not self.name:
                    invalid('Milieu name not specified!', 
                            "Illegal Milieu Name")
                elif not self.template:
                    invalid('Template name not specified!', 
                            "Illegal Template Name")
                elif not self.path:
                    invalid('Problem with path name!', 
                            "Illegal Path Name")
                else:
                    self.was_valid = True
            else:
                self.was_valid = False
        return self.was_valid

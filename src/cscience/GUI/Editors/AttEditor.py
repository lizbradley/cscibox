"""
AttEditor.py

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

import wx
import wx.grid

from cscience import datastore
from cscience.framework import Attribute
from cscience.GUI import dialogs
from cscience.GUI.Editors import MemoryFrame

AddAttribute = dialogs.field_dialog('Attribute', 'Output')

class AttEditor(MemoryFrame):
    
    framename = 'atteditor'

    def __init__(self, parent):
        super(AttEditor, self).__init__(parent, id=wx.ID_ANY, title='Attribute Editor')
        
        self.statusbar = self.CreateStatusBar()        
        label = wx.StaticText(self, wx.ID_ANY, "Attribute Names")
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY, style=wx.LB_SINGLE)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "Waiting for Attribute Information to Load")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "Please Wait")
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.grid.DisableDragColMove()
        self.grid.DisableDragColSize()
        self.grid.DisableDragRowSize()
        self.grid.SetColFormatBool(2)

        self.ConfigureGrid()

        self.addButton = wx.Button(self, wx.ID_ANY, "Add Attribute...")
        self.editButton = wx.Button(self, wx.ID_ANY, "Edit Attribute...")
        self.removeButton = wx.Button(self, wx.ID_ANY, "Remove Attribute")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.editButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.removeButton, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, border=10, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT)
        sizer.Add(self.grid, border=10, flag=wx.EXPAND | wx.ALL, proportion=1)
        sizer.Add(buttonSizer, border=10, flag=wx.ALIGN_CENTER | wx.BOTTOM)

        self.SetSizer(sizer)
                        
        self.editButton.Disable()
        self.removeButton.Disable()

        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, self.editButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.removeButton)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnSelect, self.grid)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnSelect, self.grid)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
    def update_attribute(self, att_name='', att_type='', 
                         is_output=False, in_use=False, previous_att=None):
        dlg = AddAttribute(self, att_name, att_type, is_output, in_use)
        if dlg.ShowModal() == wx.ID_OK:
            if not dlg.field_name:
                return
            if dlg.field_name not in datastore.sample_attributes or dlg.field_name == previous_att:
                if previous_att:
                    del datastore.sample_attributes[previous_att]
                    
                datastore.sample_attributes.add(Attribute(dlg.field_name, 
                                            dlg.field_type, dlg.is_output))
                self.ConfigureGrid()
                self.grid.ClearSelection()
                
                row = datastore.sample_attributes.indexof(dlg.field_name)
                self.grid.MakeCellVisible(row, 0)
    
                self.removeButton.Disable()
                datastore.data_modified = True
            else:
                wx.MessageBox('Attribute "%s" already exists!' % dlg.field_name, 
                        "Duplicate Attribute", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def OnAdd(self, event):
        self.update_attribute()
        
    def OnEdit(self, event):        
        row = self.grid.GetSelectedRows()[0]       
        att = datastore.sample_attributes.getkeyat(row)        
        in_use, ignore = self.AttributeInUse(att)
        self.update_attribute(att.name, att.type_, att.output, in_use, att.name)
        
    def ConfigureGrid(self):
        
        self.grid.BeginBatch()
        
        numCols = 3
        numRows = len(datastore.sample_attributes)

        currentCols = self.grid.GetNumberCols()
        currentRows = self.grid.GetNumberRows()
        
        if numCols > currentCols:
            self.grid.AppendCols(numCols - currentCols)
        if numCols < currentCols:
            self.grid.DeleteCols(0, currentCols - numCols)
        if numRows > currentRows:
            self.grid.AppendRows(numRows - currentRows)
        if numRows < currentRows:
            self.grid.DeleteRows(0, currentRows - numRows)
        
        self.grid.SetColLabelValue(0, "Attribute")
        self.grid.SetColLabelValue(1, "Type")
        self.grid.SetColLabelValue(2, "Output Att?")

        for index, att in enumerate(datastore.sample_attributes):
            self.grid.SetRowLabelValue(index, "")
            self.grid.SetCellValue(index, 0, att.name)
            self.grid.SetCellValue(index, 1, att.type_)
            self.grid.SetCellValue(index, 2, att.output and "1" or "0")
                    
        self.grid.AutoSize()
        
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        

    def AttributeInUse(self, att):
        """
        Determine if an attribute is in use. An attribute is considered to
        be in use if:
        - it is marked as an output attribute
        - it is used by a view (that is not the 'All' view)
        - it is used by any sample
        
        A tuple of (in_use, 'Type of Use') is returned.
        """
        
        if datastore.sample_attributes[att].output:
            return (True, "Attribute In Use: Output Attribute")
            
        for view in datastore.views.itervalues():
            if view.name == "All":
                continue
            if att in view:
                return (True, "Attribute In Use: Used by View '%s'" % (view.name))
        
        for sample in datastore.sample_db.itervalues():
            if att in sample.all_properties():
                return (True, "Attribute In Use: Used by Sample '%s'" % (sample['id']))
                
        return (False, "")

    def OnSelect(self, event):
        self.Unbind(wx.grid.EVT_GRID_RANGE_SELECT, self.grid)
        self.grid.SelectRow(event.GetRow())
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        row = event.GetRow()
        if row != -1:
            att = datastore.sample_attributes.getkeyat(row)
            self.editButton.Enable()
            status, message = self.AttributeInUse(att)
            if not status:
                self.removeButton.Enable()
            else:
                self.removeButton.Disable()
            self.statusbar.SetStatusText(message)
        else:
            self.editButton.Disable()
            self.removeButton.Disable()

    def OnRangeSelect(self, event):
        self.Unbind(wx.grid.EVT_GRID_RANGE_SELECT, self.grid)
        self.grid.ClearSelection()
        self.editButton.Disable()
        self.removeButton.Disable()
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
    def OnRemove(self, event):
        rows = self.grid.GetSelectedRows()
        row = rows[0]
        att = datastore.sample_attributes.getkeyat(row)
        del datastore.sample_attributes[att]
        self.ConfigureGrid()
        self.grid.ClearSelection()
        self.editButton.Disable()
        self.removeButton.Disable()
        datastore.data_modified = True

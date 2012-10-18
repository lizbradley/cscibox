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

from ACE.Framework.Attributes import Attributes
from ACE.GUI.Dialogs.AddAttribute import AddAttribute

class AttEditor(wx.Frame):

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Attribute Editor')
        
        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusbar = self.CreateStatusBar()

        self.atts  = self.repoman.GetModel("Attributes")
        
        label     = wx.StaticText(self, wx.ID_ANY, "ACE Attribute Names")
        
        self.grid   = wx.grid.Grid(self, wx.ID_ANY, style=wx.LB_SINGLE)
        self.grid.CreateGrid(1,1)
        self.grid.SetCellValue(0,0, "Waiting for Attribute Information to Load")
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
        buttonSizer.Add(self.addButton,    border=5, flag=wx.ALL)
        buttonSizer.Add(self.editButton,    border=5, flag=wx.ALL)
        buttonSizer.Add(self.removeButton, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label,        border=10, flag=wx.ALIGN_LEFT|wx.TOP|wx.LEFT)
        sizer.Add(self.grid,    border=10, flag=wx.EXPAND|wx.ALL, proportion=1)
        sizer.Add(buttonSizer,  border=10, flag=wx.ALIGN_CENTER|wx.BOTTOM)

        self.SetSizer(sizer)
        self.Layout()
        self.SetMinSize((400, 300))
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/atteditor/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/atteditor/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)
                
        self.editButton.Disable()
        self.removeButton.Disable()

        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, self.editButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.removeButton)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnSelect, self.grid)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnSelect, self.grid)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self.repoman.AddWindow(self)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/atteditor/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()
        config.Write("windows/atteditor/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().attEditor = None
        del(self.GetParent().attEditor)
        self.Destroy()

    def OnAdd(self, event):
        dlg = AddAttribute(self, "", "", False, False)
        if dlg.ShowModal() == wx.ID_OK:
            name      = dlg.get_name()
            att_type  = dlg.get_type()
            is_output = dlg.is_output()
            if not name:
                return
            if name not in self.atts:
                self.atts.add(name, att_type, is_output)
                self.ConfigureGrid()
                self.grid.ClearSelection()
                
                row = self.atts.names().index(name)
                self.grid.MakeCellVisible(row, 0)

                self.removeButton.Disable()
                self.repoman.RepositoryModified()
                self.UpdateAllViewAdd(name)
            else:
                dialog = wx.MessageDialog(None, 'Attribute "' + name + '" already exists!', "Duplicate Attribute", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dlg.Destroy()
        
    def OnEdit(self, event):
        
        rows = self.grid.GetSelectedRows()
        row  = rows[0]
        
        att       = self.atts.names()[row]
        att_type  = self.atts.get_att_type(att)
        is_output = self.atts.is_output_att(att)
        
        in_use, ignore = self.AttributeInUse(att)
        
        previous_att = att
        
        dlg = AddAttribute(self, att, att_type, is_output, in_use)
        if dlg.ShowModal() == wx.ID_OK:
            name      = dlg.get_name()
            att_type  = dlg.get_type()
            is_output = dlg.is_output()
            if not name:
                return
            if name not in self.atts or name == previous_att:
                
                self.atts.remove(previous_att)
                self.UpdateAllViewRemove(previous_att)
                
                self.atts.add(name, att_type, is_output)
                self.ConfigureGrid()
                self.grid.ClearSelection()
                
                row = self.atts.names().index(name)
                self.grid.MakeCellVisible(row, 0)

                self.removeButton.Disable()
                self.repoman.RepositoryModified()
                self.UpdateAllViewAdd(name)
            else:
                dialog = wx.MessageDialog(None, 'Attribute "' + name + '" already exists!', "Duplicate Attribute", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dlg.Destroy()
        
    def ConfigureGrid(self):
        
        self.grid.BeginBatch()
        
        numCols   = 3
        numRows   = len(self.atts)

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

        index = 0
        for att in self.atts:
            self.grid.SetRowLabelValue(index, "")
            self.grid.SetCellValue(index, 0, att)
            self.grid.SetCellValue(index, 1, self.atts.get_att_type(att))
            if self.atts.is_output_att(att):
                self.grid.SetCellValue(index, 2, "1")
            else:
                self.grid.SetCellValue(index, 2, "0")
            index += 1
        
        self.grid.AutoSize()
        
        h,w = self.grid.GetSize()
        self.grid.SetSize((h+1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def UpdateAllViewAdd(self, value):
        # whenever the list of attributes changes
        # we need to update the view called "All"
        # we also need to notify the view editor
        # that this view has changed
        
        views = self.repoman.GetModel("Views")
        view  = views.get('All')
        view.add(value)

        viewEditor = self.GetParent().GetViewEditor()
        if viewEditor != None:
            viewEditor.UpdateView('All')

    def UpdateAllViewRemove(self, value):
        # whenever the list of attributes changes
        # we need to update the view called "All"
        # we also need to notify the view editor
        # that this view has changed

        views = self.repoman.GetModel("Views")
        view  = views.get('All')
        view.remove(value)

        viewEditor = self.GetParent().GetViewEditor()
        if viewEditor != None:
            viewEditor.UpdateView('All')

    def AttributeInUse(self, att):
        
        # determine if an attribute is being used
        # first check to see if its an output att
        # second check to see if a nuclide references it
        # third check to see if a view references it
        # fourth check to see if a sample references it
        # if any of these conditions is true, return True, otherwise False
        
        if self.atts.is_output_att(att):
            return (True, "Attribute In Use: Output Attribute")
            
        nuclides = self.repoman.GetModel("Nuclides")
        names    = nuclides.names()
        for name in names:
            nuclide = nuclides.get(name)
            if nuclide.contains(att):
                return (True, "Attribute In Use: Used by Nuclide '%s'" % (name))
        
        views = self.repoman.GetModel('Views')
        names = views.names()
        for name in names:
            if name == "All":
                continue
            view = views.get(name)
            if att in view:
                return (True, "Attribute In Use: Used by View '%s'" % (name))
        
        samples_db = self.repoman.GetModel("Samples")
        ids = samples_db.ids()
        for s_id in ids:
            sample = samples_db.get(s_id)
            if att in sample.all_properties():
                return (True, "Attribute In Use: Used by Sample '%s'" % (s_id))
                
        return (False, "")

    def OnSelect(self, event):
        self.Unbind(wx.grid.EVT_GRID_RANGE_SELECT, self.grid)
        self.grid.SelectRow(event.GetRow())
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        row = event.GetRow()
        if row != -1:
            att = self.atts.names()[row]
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
        row  = rows[0]
        att  = self.atts.names()[row]
        self.atts.remove(att)
        self.ConfigureGrid()
        self.grid.ClearSelection()
        self.editButton.Disable()
        self.removeButton.Disable()
        self.repoman.RepositoryModified()
        
        self.UpdateAllViewRemove(att)

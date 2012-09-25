"""
TemplateEditor.py

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

from ACE.framework import Template
from ACE.GUI.Dialogs.EditTemplateField import EditTemplateField

class TemplateEditor(wx.Frame):

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Template Editor')
        
        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusbar = self.CreateStatusBar()

        templatesLabel = wx.StaticText(self, wx.ID_ANY, "Templates")
        templateLabel = wx.StaticText(self, wx.ID_ANY, "Template")

        self.templates = self.repoman.GetModel("Templates")
        self.template = None
        
        self.templates_list = wx.ListBox(self, wx.ID_ANY, choices=self.templates.names(), style=wx.LB_SINGLE)
        
        self.addButton = wx.Button(self, wx.ID_ANY, "Add Template...")
        self.removeButton = wx.Button(self, wx.ID_ANY, "Delete Template")
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY, size=(400, 400))
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "No Template Selected.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "")
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        
        self.addFieldButton = wx.Button(self, wx.ID_ANY, "Add Field...")
        self.editFieldButton = wx.Button(self, wx.ID_ANY, "Edit Field...")
        self.removeFieldButton = wx.Button(self, wx.ID_ANY, "Delete Field")
        self.moveUp = wx.Button(self, wx.ID_ANY, "Move Up")
        self.moveDown = wx.Button(self, wx.ID_ANY, "Move Down")
                
        self.addFieldButton.Disable()
        self.editFieldButton.Disable()
        self.removeFieldButton.Disable()
        self.moveUp.Disable()
        self.moveDown.Disable()

        buttonSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer1.Add(self.addButton, border=5, flag=wx.ALL)
        buttonSizer1.Add(self.removeButton, border=5, flag=wx.ALL)
        
        buttonSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer2.Add(self.addFieldButton, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.editFieldButton, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.removeFieldButton, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.moveUp, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.moveDown, border=5, flag=wx.ALL)
        
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(templatesLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.templates_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnOneSizer.Add(buttonSizer1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(templateLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnTwoSizer.Add(buttonSizer2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)
        
        self.SetSizer(sizer)
        self.Layout()
        self.SetSize(self.GetBestSize())
        self.SetMinSize(self.GetSize())
        
        config = self.repoman.GetConfig()
        size = eval(config.Read("windows/templateeditor/size", repr(self.GetSize())))
        loc = eval(config.Read("windows/templateeditor/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)

        self.removeButton.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.removeButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddField, self.addFieldButton)
        self.Bind(wx.EVT_BUTTON, self.OnEditField, self.editFieldButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveField, self.removeFieldButton)
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, self.moveUp)
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, self.moveDown)
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.templates_list)

        self.templates_list.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInTemplates)
        
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        repoman.AddWindow(self)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/templateeditor/location", "(%d,%d)" % (x, y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/templateeditor/size", "(%d,%d)" % (width, height))
        self.Layout()

    def ConfigureGrid(self):
        
        self.grid.Unbind(wx.grid.EVT_GRID_SELECT_CELL)
        self.grid.Unbind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK)
        
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        if self.template is None:
            self.grid.AppendRows()
            self.grid.AppendCols()
            if self.in_use:
                self.grid.SetCellValue(0, 0, "Template is in use and cannot be edited.")
            else:
                self.grid.SetCellValue(0, 0, "No Template Selected.")
            self.grid.SetRowLabelValue(0, "")
            self.grid.SetColLabelValue(0, "")
        else:
            numRows = self.template.size()
            
            self.grid.AppendCols(3)
            self.grid.SetColLabelValue(0, "Name")
            self.grid.SetColLabelValue(1, "Type")
            self.grid.SetColLabelValue(2, "Is Key?")
            self.grid.SetColFormatBool(2)
            
            if numRows == 0:
                self.grid.AppendRows()
                self.grid.SetCellValue(0, 0, "Template has no defined fields.")
                self.grid.SetCellValue(0, 1, "")
                self.grid.SetCellValue(0, 2, "0")
                self.grid.SetRowLabelValue(0, "")
            else:
                self.grid.AppendRows(numRows)
                names = self.template.get_order()
                index = 0
                keys = self.template.get_keys()
                for name in names:
                    self.grid.SetCellValue(index, 0, name)
                    self.grid.SetCellValue(index, 1, self.template.get_field_type(name))
                    if name in keys:
                        self.grid.SetCellValue(index, 2, "1")
                    else:
                        self.grid.SetCellValue(index, 2, "0")
                    self.grid.SetRowLabelValue(index, "")
                    index += 1
                    
                self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridSelect)
                self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnGridLabelSelect)
                

        self.grid.ClearSelection()
        self.grid.AutoSize()
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().templateEditor = None
        del(self.GetParent().templateEditor)
        self.Destroy()

    def OnAdd(self, event):
        dialog = wx.TextEntryDialog(self, "Enter Template Name", "Template Entry Dialog", style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value != "":
                if not self.templates.contains(value):
                    template = Template(value)
                    self.templates.add(template)
                    self.templates_list.Set(self.templates.names())
                    self.removeButton.Disable()
                    self.template = None
                    self.in_use = False
                    self.addFieldButton.Disable()
                    self.editFieldButton.Disable()
                    self.removeFieldButton.Disable()
                    self.moveUp.Disable()
                    self.moveDown.Disable()
                    self.repoman.RepositoryModified()
                    self.statusbar.SetStatusText("")
                    self.ConfigureGrid()
                else:
                    dialog = wx.MessageDialog(None, 'Template "' + value + '" already exists!', "Duplicate Template", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Template name not specified!', "Illegal Template Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()
        
    def OnSelect(self, event):
        name = self.templates_list.GetStringSelection()
        
        self.ClearGrid()

        self.in_use = False
        collections = self.repoman.GetModel("Collections")
        names = collections.names()
        for collection_name in names:
            template = collections.get_template(collection_name)
            if template == name:
                self.in_use = True
                break
        
        if self.in_use:
            self.statusbar.SetStatusText("This template is in use and cannot be edited.")
            self.template = None
            self.addFieldButton.Enable(False)
            self.removeButton.Enable(False)
            
        else:
            self.statusbar.SetStatusText("")
            self.template = self.templates.get(name)
            self.addFieldButton.Enable(True)
            self.removeButton.Enable(True)
            
        self.ConfigureGrid()
        
    def ClearGrid(self):
        self.grid.ClearSelection()
        self.editFieldButton.Disable()
        self.removeFieldButton.Disable()
        self.moveUp.Disable()
        self.moveDown.Disable()
        
    def ConfigureGridButtonsForRow(self, row):
        self.grid.SelectRow(row)
        self.editFieldButton.Enable(True)
        self.removeFieldButton.Enable(True)
        if row != 0:
            self.moveUp.Enable(True)
        else:
            self.moveUp.Disable()
        if row != (self.template.size() - 1):
            self.moveDown.Enable()
        else:
            self.moveDown.Disable()

    def OnGridSelect(self, event):
        print "In OnGridSelect: %s" % event.GetRow()
        print "In OnGridSelect: %s" % event.GetCol()
        if self.template is not None:
            if self.template.size() > 0:
                self.ConfigureGridButtonsForRow(event.GetRow())
        else:
            self.ClearGrid()

    def OnGridLabelSelect(self, event):
        if event.GetCol() == -1:
            if self.template is not None:
                if self.template.size() > 0:
                    self.ConfigureGridButtonsForRow(event.GetRow())
        else:
            self.ClearGrid()
            
    def OnMoveUp(self, event):
        row = self.grid.GetSelectedRows()[0]
        self.template.move_up(row)
        self.ConfigureGrid()
        self.ConfigureGridButtonsForRow(row - 1)
        self.repoman.RepositoryModified()

    def OnMoveDown(self, event):
        row = self.grid.GetSelectedRows()[0]
        self.template.move_down(row)
        self.ConfigureGrid()
        self.ConfigureGridButtonsForRow(row + 1)
        self.repoman.RepositoryModified()

    # list box controls do not deliver deselection events when in 'single selection' mode
    # but it is still possible for the user to clear the selection from such a list
    # as such, we need to monitor the LEFT_UP events for each of our list boxes and
    # check to see if the selection got cleared without us knowning about it
    # if so, we need to update the user interface appropriately
    # this code falls under the category of "THIS SUCKS!" It would be much cleaner to
    # just be informed of list deselection events
    def OnLeftUpInTemplates(self, event):
        index = self.templates_list.GetSelection()
        if index == -1:
            self.template = None
            self.in_use = False
            self.removeButton.Disable()
            self.addFieldButton.Disable()
            self.editFieldButton.Disable()
            self.removeFieldButton.Disable()
            self.moveUp.Disable()
            self.moveDown.Disable()
            self.statusbar.SetStatusText("")
            self.ConfigureGrid()
        event.Skip()
    
    def OnRemove(self, event):
        name = self.templates_list.GetStringSelection()
        self.templates.remove(name)
        self.templates_list.Set(self.templates.names())
        self.template = None
        self.in_use = False
        self.removeButton.Disable()
        self.addFieldButton.Disable()
        self.repoman.RepositoryModified()
        self.ConfigureGrid()
        self.ClearGrid()

    def OnAddField(self, event):
        dlg = EditTemplateField(self, "", "", False)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.get_name()
            field_type = dlg.get_type()
            is_key = dlg.get_iskey()
            self.template.add_field(name, field_type.lower())
            if is_key:
                self.template.add_key(name)
            self.repoman.RepositoryModified()
            self.ConfigureGrid()
            self.ClearGrid()
        dlg.Destroy()
        
    def OnEditField(self, event):
        row = self.grid.GetSelectedRows()[0]
        prior_name = self.template.get_order()[row]
        prior_field_type = self.template.get_field_type(prior_name)
        prior_is_key = prior_name in self.template.get_keys()
        dlg = EditTemplateField(self, prior_name, prior_field_type.capitalize(), prior_is_key)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.get_name()
            field_type = dlg.get_type()
            is_key = dlg.get_iskey()
            if prior_is_key and not is_key:
                self.template.remove_key(prior_name)
            if name != prior_name:
                self.template.remove_field(prior_name)
                self.template.add_field(name, field_type.lower())
            else:
                if field_type.lower() != prior_field_type:
                    self.template.add_field(name, field_type.lower())
            if is_key:
                self.template.add_key(name)
            else:
                self.template.remove_key(name)
            self.repoman.RepositoryModified()
            self.ConfigureGrid()
            self.ConfigureGridButtonsForRow(row)
        dlg.Destroy()
        
    def OnRemoveField(self, event):
        row = self.grid.GetSelectedRows()[0]
        name = self.template.get_order()[row]
        self.template.remove_field(name)
        self.repoman.RepositoryModified()
        self.editFieldButton.Disable()
        self.removeFieldButton.Disable()
        self.moveUp.Disable()
        self.moveDown.Disable()
        self.ConfigureGrid()
        self.ClearGrid()

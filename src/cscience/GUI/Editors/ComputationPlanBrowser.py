"""
ComputationPlanBrowser.py

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
import os

from cscience import datastore
from cscience.GUI.Editors import MemoryFrame
from cscience.GUI.Util import grid
from cscience.GUI import events

class CplanGridTable(grid.UpdatingTable):
    def __init__(self, *args, **kwargs):
        self._plans = []
        self.names = []
        super(CplanGridTable, self).__init__(*args, **kwargs)

    @property
    def plans(self):
        return self._plans
    @plans.setter
    def plans(self, value):
        self._plans = value
        if value:
            names = set()
            for plan in value:
                names.update(plan.keys())
            names.remove('name')
            self.names = sorted(list(names))
        else:
            self.names = []
        self.reset_view()
        
    def raw_value(self, row, col):
        return str(self.plans[col][self.names[row]])
    def GetNumberRows(self):
        return len(self.names) or 1
    def GetNumberCols(self):
        return len(self.plans) or 1
    def GetValue(self, row, col):
        if not self.plans:
            return "Select one or more Computation Plans"
        return self.raw_value(row, col)
    def GetRowLabelValue(self, row):
        if not self.plans:
            return ''
        return self.names[row]
    def GetColLabelValue(self, col):
        if not self.plans:
            return "No Computation Plans Selected"
        return self.plans(col).name

class ComputationPlanBrowser(MemoryFrame):
    
    framename = 'cplanbrowser'
    
    def __init__(self, parent):
        super(ComputationPlanBrowser, self).__init__(parent, id=wx.ID_ANY, 
                                        title='Computation Plan Browser')
        menu_bar = wx.MenuBar()
        edit_menu = wx.Menu()
        copy_item = edit_menu.Append(wx.ID_COPY, "Copy\tCtrl-C", 
                                     "Copy selected collection items.")
        edit_menu.Enable(wx.ID_COPY, False)
        menu_bar.Append(edit_menu, "Edit")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.copy, copy_item)

        self.CreateStatusBar()
        
        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot("Computation Plans")
        self.tree.Expand(root)
        
        self.grid = grid.LabelSizedGrid(self, wx.ID_ANY)
        self.table = CplanGridTable(self.grid)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        
        self.update_tree()
        
        #self.add_button = wx.Button(self, wx.ID_ANY, "Create Computation Plan...")
        self.delete_button = wx.Button(self, wx.ID_ANY, "Delete Computation Plan...")
        
        self.delete_button.Disable()

        columnsizer = wx.BoxSizer(wx.HORIZONTAL)
        columnsizer.Add(self.tree, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnsizer.Add(self.grid, proportion=2, border=5, flag=wx.ALL | wx.EXPAND)

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        #buttonsizer.Add(self.add_button, border=5, flag=wx.ALL)
        buttonsizer.Add(self.delete_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnsizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonsizer, flag=wx.LEFT)
        self.SetSizer(sizer)
        
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.allow_copy, self.grid)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.enforce_selection_rules, self.tree)
        self.Bind(wx.EVT_BUTTON, self.delete_plan, self.delete_button)

    def allow_copy(self, event):
        menu_bar = self.GetMenuBar()
        edit = menu_bar.GetMenu(menu_bar.FindMenu("Edit"))
        edit.Enable(wx.ID_COPY, bool(self.grid.SelectedRowset))

    def copy(self, event):
        rowtext = ['\t'.join([plan.name for plan in self.table.plans])]
        for row in self.grid.SelectedRowset:
            rowtext.append('\t'.join([self.table.GetRowLabelValue(row)] +
                                     [self.table.raw_value(row, col) for col in 
                                      range(self.table.GetNumberCols())]))
        
        data = wx.TextDataObject()
        data.SetText(os.linesep.join(rowtext))
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        
    def on_repository_altered(self, event):
        if 'cplans' in event.changed:
            self.update_tree()
        event.Skip()
        
    def update_tree(self):
        root = self.tree.GetRootItem()
        self.tree.DeleteChildren(root)
        
        for experiment in datastore.computation_plans:
            item = self.tree.AppendItem(root, experiment.name)
            self.tree.SetPyData(item, experiment)
        
        self.tree.ExpandAll()
        self.tree.UnselectAll()
        
    def delete_plan(self, event):
        item = self.tree.GetSelections()[0]
        experiment = self.tree.GetItemPyData(item)
                
        updates = False
        for sample in datastore.sample_db.itervalues():
            try:
                del sample[experiment.name]
                updates = True
            except KeyError:
                pass
        if updates:
            events.post_change(self, 'samples')
            
        del datastore.computation_plans[experiment.name]
        events.post_change(self, 'cplans')
                
    def enforce_selection_rules(self, event):
        item = event.GetItem()
        if item.IsOk():
            self.delete_button.Disable()

            #allow selection of either the root (to select "everything") or
            #any subset of experiments desired.
            if item == self.tree.GetRootItem():
                if self.tree.IsSelected(item):
                    for node in self.tree.GetSelections():
                        if node != item:
                            self.tree.UnselectItem(node)
                objs = datastore.computation_plans.values()
            else:              
                objs = filter(None, [self.tree.GetItemPyData(it) for it in 
                                     self.tree.GetSelections()])
                
                if len(objs) == 1:
                    self.delete_button.Enable(True)

            self.grid.ClearSelection()
            self.table.plans = objs

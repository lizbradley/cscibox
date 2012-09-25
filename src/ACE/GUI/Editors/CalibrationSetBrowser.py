"""
CalibrationSetBrowser.py

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
import wx.lib.scrolledpanel

from ACE.framework import Group, Sample

class CalibrationSetBrowser(wx.Frame):
    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='Calibration Set Browser', size=(540, 380))

        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.menuBar = wx.MenuBar()
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected samples.")
        
        editMenu.Enable(wx.ID_COPY, False)
        
        self.menuBar.Append(editMenu, "Edit")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        self.objs = []
        
        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot("Calibration Sets")
        self.tree.Expand(root)
        
        viewLabel = wx.StaticText(self, wx.ID_ANY, "View:")
        self.selectedView = wx.ComboBox(self, wx.ID_ANY, value="All", choices=self.repoman.GetModel("Views").names(), style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "The current view has no attributes defined for it.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "Invalid View")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.selected_rows = set()
        
        self.ConfigureTree()
        self.ConfigureGrid()
        
        viewSizer = wx.BoxSizer(wx.HORIZONTAL)
        viewSizer.Add(viewLabel, border=5, flag=wx.ALL)
        viewSizer.Add(self.selectedView, border=5, flag=wx.ALL)
        
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(self.selectedView.GetSize(), border=5, flag=wx.ALL)
        columnOneSizer.Add(self.tree, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        
        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(viewSizer)
        columnTwoSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        
        self.SetSizer(sizer)
        self.SetMinSize((540, 380))
        self.SetSize((540, 380))
        self.Layout()
        
        config = self.repoman.GetConfig()
        size = eval(config.Read("windows/calibbrowser/size", repr(self.GetSize())))
        loc = eval(config.Read("windows/calibbrowser/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)

        self.Bind(wx.EVT_COMBOBOX, self.OnViewSelect, self.selectedView)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed, self.tree)

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.repoman.AddWindow(self)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/calibbrowser/location", "(%d,%d)" % (x, y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/calibbrowser/size", "(%d,%d)" % (width, height))
        self.Layout()

    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().calibrationBrowser = None
        del(self.GetParent().calibrationBrowser)
        self.Destroy()
        
    def OnRangeSelect(self, event):

        start = event.GetTopLeftCoords()[0]
        stop = event.GetBottomRightCoords()[0]
        
        if event.Selecting():
            # print "Selecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop + 1):
                self.selected_rows.add(i)
            # print "selected rows: %s" % self.selected_rows
        else:
            # print "DeSelecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop + 1):
                if i in self.selected_rows:
                    self.selected_rows.remove(i)
            # print "selected rows: %s" % self.selected_rows
            
        editMenu = self.menuBar.GetMenu(self.menuBar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            editMenu.Enable(wx.ID_COPY, True)

    def OnCopy(self, event):
        
        indexes = sorted(list(self.selected_rows))

        cols = self.grid.GetNumberCols()
        
        result = "\t"
        
        for i in range(cols):
            result = result + self.grid.GetColLabelValue(i) + "\t"
            
        result = result[0:-1]
        result = result + os.linesep
        
        for row in indexes:
            result = result + self.grid.GetRowLabelValue(row) + "\t"
            for col in range(cols):
                result = result + self.grid.GetCellValue(row, col) + "\t"
            result = result[0:-1]
            result = result + os.linesep

        data = wx.TextDataObject()
        data.SetText(result)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def ConfigureGrid(self):
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        view_name = self.selectedView.GetStringSelection()
        view = self.repoman.GetModel("Views").get(view_name)
        atts = view.atts()
        
        numCols = len(atts)
        
        if numCols == 0:
            self.grid.AppendRows(150)
            self.grid.AppendCols()
            self.grid.SetCellValue(0, 0, "The current view has no attributes defined for it.")
            for index in range(150):
                self.grid.SetRowLabelValue(index, "")
            self.grid.SetColLabelValue(0, "Invalid View")
            self.grid.AutoSize()
            return
        else:
            samples_db = self.repoman.GetModel("Samples")
            
            samples = [sample for sample in self.objs if isinstance(sample, Sample)]
            sets = [sample_set for sample_set in self.objs if isinstance(sample_set, Group)]
            for group in sets:
                members = group.members()
                for s_id, nuclide in members:
                    sample = samples_db.get(s_id)
                    sample.set_nuclide(nuclide)
                    samples.append(sample)
                                
            self.grid.AppendRows(len(samples))
            self.grid.AppendCols(numCols)
            self.maxName = ""
            for index in range(len(samples)):
                name = samples[index]['id']
                if len(name) > len(self.maxName):
                    self.maxName = name
                self.grid.SetRowLabelValue(index, name)
                
            extent = self.grid.GetTextExtent(self.maxName)
            width = extent[0]
            if width == 0:
                width = 50
            else:
                width += 25
            self.grid.SetRowLabelSize(width)

            index = 0
            for att in atts:
                self.grid.SetColLabelValue(index, att)
                index += 1

            for row in range(len(samples)):
                index = 0
                for att in atts:
                    self.grid.SetCellValue(row, index, str(samples[row][att]))
                    index += 1
                
            self.grid.AutoSize()
        
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def ConfigureTree(self):
        root = self.tree.GetRootItem()
        self.tree.DeleteChildren(root)
        
        groups = self.repoman.GetModel("Groups")
        samples_db = self.repoman.GetModel("Samples")
        
        sets = groups.calibration_sets(samples_db)
        for name in sets:
            group = groups.get(name)
            
            set_item = self.tree.AppendItem(root, name)
            self.tree.SetPyData(set_item, group)
            
            members = group.members()
            
            for s_id, nuclide in members:
                sample = samples_db.get(s_id)
                sample.set_nuclide(nuclide)
                item = self.tree.AppendItem(set_item, s_id)
                self.tree.SetPyData(item, sample)
        self.tree.Expand(root)
        self.tree.UnselectAll()

    def OnCollapsed(self, event):
        #print "OnCollapsed: ", self.tree.GetItemText(event.GetItem())
        items = self.tree.GetSelections()
        self.objs = [self.tree.GetItemPyData(item) for item in items]
        self.ConfigureGrid()

    def OnExpanded(self, event):
        #print "OnExpanded: ", self.tree.GetItemText(event.GetItem())
        pass

    def OnSelChanged(self, event):
        root = self.tree.GetRootItem()
        items = self.tree.GetSelections()
        
        item = event.GetItem()
        if item.IsOk():
            selected = self.tree.IsSelected(item)
            if selected:
                if item == root:
                    for node in items:
                        if node != root:
                            self.tree.UnselectItem(node)
                if self.tree.ItemHasChildren(item):
                    for node in items:
                        parent = self.tree.GetItemParent(node)
                        if parent == item:
                            self.tree.UnselectItem(node)
                else:
                    parent = self.tree.GetItemParent(item)
                    for node in items:
                        if node == parent:
                            self.tree.UnselectItem(parent)
                
            items = self.tree.GetSelections()
            self.objs = [self.tree.GetItemPyData(item) for item in items]
            
            self.grid.ClearSelection()
            
            self.ConfigureGrid()
        
    def OnViewSelect(self, event):
        self.ConfigureGrid()
        
    def UpdateViews(self):
        # get current view
        view_name = self.selectedView.GetStringSelection()
        # get list of views
        view_names = self.repoman.GetModel("Views").names()
        
        self.selectedView.Clear()
        for view in view_names:
            self.selectedView.Append(view)
        
        # if current view has been deleted, then switch to "All" view
        if not view_name in view_names:
            self.selectedView.SetStringSelection('All')
        else:
            self.selectedView.SetStringSelection(view_name)
            
        self.Layout()
        self.ConfigureGrid()
        
    def UpdateSets(self):
        self.objs = []
        self.ConfigureTree()
        self.ConfigureGrid()

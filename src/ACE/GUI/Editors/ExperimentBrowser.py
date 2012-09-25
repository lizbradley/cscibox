"""
ExperimentBrowser.py

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

from ACE.framework import Experiment

from ACE.GUI.Dialogs.ExperimentEditor import ExperimentEditor

from ACE.GUI.Util.ExperimentUtils import ExperimentUtils
from ACE.GUI.Util.FancyTextRenderer import FancyTextRenderer

class ExperimentBrowser(wx.Frame):
    
    report_order = ('nuclide', 'timestep', 'calibration', 'dating', 'calibration_set', 
                    'geomagneticLatitude', 'geographicScaling', 'geomagneticIntensity', 
                    'seaLevel', 'psi_mu_0', 'phi_mu_f0', 'slowMuonPerc', 
                    'post_calibrated_slowMuon', 'fastMuonPerc', 'post_calibrated_fastMuon', 
                    'psi_ca_0', 'psi_ca_uncertainty', 'psi_k_0', 'psi_k_uncertainty', 
                    'Pf_0', 'Pf_uncertainty', 'psi_spallation_nuclide', 
                    'psi_spallation_uncertainty', 'sample_size', 'probability', 'chi_square')
    
    @staticmethod
    def report_cmp(x, y):
        return cmp(ExperimentBrowser.report_order.index(x), ExperimentBrowser.report_order.index(y))

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Experiment Browser')
        
        self.repoman = repoman
        self.objs = []

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.menuBar = wx.MenuBar()
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected collection items.")
        
        editMenu.Enable(wx.ID_COPY, False)
        
        self.menuBar.Append(editMenu, "Edit")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        self.statusbar = self.CreateStatusBar()
        
        self.experiments = self.repoman.GetModel("Experiments")

        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot("Experiments")
        self.tree.Expand(root)
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "Select one or more Experiments")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "No Experiments Selected")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.grid.SetDefaultRenderer(FancyTextRenderer())
        
        ExperimentUtils.InstallGridHint(self.grid, ExperimentUtils.GetToolTipString)

        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.selected_rows = set()
        
        self.ConfigureTree()
        self.ConfigureGrid()
        
        self.addButton = wx.Button(self, wx.ID_ANY, "Create Experiment...")
        self.deleteButton = wx.Button(self, wx.ID_ANY, "Delete Experiment...")
        
        self.deleteButton.Disable()

        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(self.tree, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnSizer.Add(self.grid, proportion=2, border=5, flag=wx.ALL | wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.deleteButton, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, flag=wx.LEFT)

        self.SetSizer(sizer)
        self.SetMinSize((540, 380))
        self.SetSize((540, 380))
        self.Layout()
        
        config = self.repoman.GetConfig()
        size = eval(config.Read("windows/expbrowser/size", repr(self.GetSize())))
        loc = eval(config.Read("windows/expbrowser/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed, self.tree)
        
        self.Bind(wx.EVT_BUTTON, self.OnCreate, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, self.deleteButton)

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        repoman.AddWindow(self)
    
    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().expBrowser = None
        del(self.GetParent().expBrowser)
        self.Destroy()
    
    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/expbrowser/location", "(%d,%d)" % (x, y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/expbrowser/size", "(%d,%d)" % (width, height))
        self.Layout()

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
                value = self.grid.GetCellValue(row, col)
                # get rid of <FancyText>
                value = value[11:len(value)]
                # get rid of </FancyText>
                value = value[0:-12]
                
                while value.find("<sup>") != -1:
                    pos = value.find("<sup>")
                    value = value[0:pos] + value[pos + 5:len(value)]

                while value.find("</sup>") != -1:
                    pos = value.find("</sup>")
                    value = value[0:pos] + value[pos + 6:len(value)]
                
                result = result + value + "\t"
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

        if len(self.objs) == 0:
            self.grid.AppendRows(1)
            self.grid.AppendCols(1)
            self.grid.SetCellValue(0, 0, "Select one or more Experiments")
            self.grid.SetRowLabelValue(0, "")
            self.grid.SetColLabelValue(0, "No Experiments Selected")
        else:
            
            exps = self.objs[:]
           
            if not exps:
                self.grid.AppendRows(1)
                self.grid.AppendCols(1)
                self.grid.SetCellValue(0, 0, "Select one or more Experiments")
                self.grid.SetRowLabelValue(0, "")
                self.grid.SetColLabelValue(0, "No Experiments Selected")
            else:
                rowNames = set()
                numRows = 0
                for exp in exps:
                    rows = len(exp)
                    if rows > numRows:
                        numRows = rows
                    keys = exp.keys()
                    for key in keys:
                        rowNames.add(key)
            
                rowLabels = sorted(list(rowNames))
                rowLabels.remove('name')
                rowLabels.sort(ExperimentBrowser.report_cmp)
                
                displayLabels = [ExperimentUtils.display_name[item] for item in rowLabels]
            
                self.grid.AppendRows(len(rowLabels))
                self.grid.AppendCols(len(exps))
            
                maxName = ""
                index = 0
                for label in displayLabels:
                    if len(label) > len(maxName):
                        maxName = label
                    self.grid.SetRowLabelValue(index, label)
                    index += 1
                extent = self.grid.GetTextExtent(maxName)
                width = extent[0]
                if width == 0:
                    width = 50
                else:
                    width += 25
                self.grid.SetRowLabelSize(width)
            
                index = 0
                for exp in exps:
                    self.grid.SetColLabelValue(index, exp['name'])
                    index += 1
                
                row = 0
                for label in rowLabels:
                    col = 0
                    for exp in exps:
                        try:
                            self.grid.SetCellValue(row, col, "<FancyText>%s</FancyText>" % (ExperimentUtils.GetGridValue(exp, label)))
                        except Exception, e:
                            print e
                        col += 1
                    row += 1
            
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
        
        uncalItem = self.tree.AppendItem(root, "Uncalibrated")
        calItem = self.tree.AppendItem(root, "Calibrated")
        
        uncalibrated = {}
        calibrated = {}
        
        nucs = self.nuclides.names()
        for name in nucs:
            # only add a nuclide to the tree if it has experiments associated with it
            exps = self.experiments.experimentsWithNuclide(name)
            cal = [exp for exp in exps if self.experiments.get(exp).is_calibrated()]
            uncal = [exp for exp in exps if not self.experiments.get(exp).is_calibrated()]
            if len(uncal) > 0:
                item = self.tree.AppendItem(uncalItem, name)
                self.tree.SetPyData(item, name + ":uncalibrated")
                uncalibrated[name] = item
            if len(cal) > 0:
                item = self.tree.AppendItem(calItem, name)
                self.tree.SetPyData(item, name + ":calibrated")
                calibrated[name] = item
        
        for name in nucs:
            exps = self.experiments.experimentsWithNuclide(name)
            for exp_name in exps:
                experiment = self.experiments.get(exp_name)
                nuc_item = None
                if experiment.is_calibrated():
                    nuc_item = calibrated[name]
                else:
                    nuc_item = uncalibrated[name]
                item = self.tree.AppendItem(nuc_item, exp_name)
                self.tree.SetPyData(item, experiment)
        self.tree.ExpandAll()
        self.tree.UnselectAll()

    def OnCollapsed(self, event):
        items = self.tree.GetSelections()
        self.objs = [self.tree.GetItemPyData(item) for item in items]
        if len(items) == 0:
            self.deleteButton.Disable()
        self.grid.ClearSelection()
        self.ConfigureGrid()

    def OnExpanded(self, event):
        pass
        
    def OnCreate(self, event):
        dlg = ExperimentEditor(self, self.repoman)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValues()
            exp = Experiment(values['name'])
            del values['name']
            for key in values.keys():
                exp[key] = values[key]
            self.experiments.add(exp)
            self.objs = []
            self.grid.ClearSelection()
            self.ConfigureTree()
            self.ConfigureGrid()
            self.repoman.RepositoryModified()
        dlg.Destroy()
        
    def Level(self, item):
        if item == self.tree.GetRootItem():
            return 0
        return self.Level(self.tree.GetItemParent(item)) + 1
        
    def OnDelete(self, event):
        items = self.tree.GetSelections()
        item = items[0]
        experiment = self.tree.GetItemPyData(item)

        if experiment.is_calibrated():
            dialog = wx.MessageDialog(None, 'Warning: deleting this experiment will strip data from all samples processed by it. Do you still want to delete this experiment?', "Calibrated Experiment", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_NO:
                return
                
        samples_db = self.repoman.GetModel('Samples')
        ids = samples_db.ids()
        
        updates = False
        
        for s_id in ids:
            sample = samples_db.get(s_id)
            if experiment['nuclide'] in sample.nuclides():
                if experiment['name'] in sample.experiments(experiment['nuclide']):
                    sample.remove_experiment(experiment['nuclide'], experiment['name'])
                    updates = True
        
        if updates:
            browser = self.GetParent()
            browser.CreateVirtualSamples()
            browser.ConfigureFilter()
            browser.ConfigureSort()
            browser.ApplyFilter()
            browser.FilterCalibrationSamples()
            browser.ApplyTextSearchFilter()
            browser.ApplySort()
            browser.grid.ClearSelection()
            browser.ConfigureGrid()
        
        self.experiments.remove(experiment['name'])
        
        self.objs = []
        self.grid.ClearSelection()
        self.ConfigureTree()
        self.ConfigureGrid()
        
        self.repoman.RepositoryModified()
        
    def OnSelChanged(self, event):
        root = self.tree.GetRootItem()
        items = self.tree.GetSelections()
        
        item = event.GetItem()
        
        if item.IsOk():
            self.deleteButton.Disable()

            selected = self.tree.IsSelected(item)
            if selected:
                if item == root:
                    for node in items:
                        if node != root:
                            self.tree.UnselectItem(node)
                parent = self.tree.GetItemParent(item)
                if parent == root:
                    for node in items:
                        if node != item:
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
            self.objs = [item for item in self.objs if item is not None]
            
            if len(items) == 1:
                item = items[0]
                if self.Level(item) == 3:
                    self.deleteButton.Enable(True)
                    exp = self.objs[0]

            self.grid.ClearSelection()
            self.ConfigureGrid()

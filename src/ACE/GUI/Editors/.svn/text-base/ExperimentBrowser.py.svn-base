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
import thread

from ACE.Framework.Experiment      import Experiment
from ACE.Framework.Nuclide         import Nuclide

from ACE.GUI.Dialogs.WorkflowProgress          import WorkflowProgress
from ACE.GUI.Dialogs.DisplayCalibrationResults import DisplayCalibrationResults
from ACE.GUI.Dialogs.ExperimentEditor          import ExperimentEditor

from ACE.GUI.Events.ProgressEvents import WorkflowDoneEvent
from ACE.GUI.Events.ProgressEvents import EVT_WORKFLOW_DONE
from ACE.GUI.Events.ProgressEvents import CalibrationPlotEvent
from ACE.GUI.Events.ProgressEvents import EVT_CALIBRATION_PLOT

from ACE.GUI.Util.ExperimentUtils import ExperimentUtils
from ACE.GUI.Util.FancyTextRenderer import FancyTextRenderer

class RunCalibrationThread:
    def __init__(self, browser, dialog, repoman, experiment):
        self.browser = browser
        self.dialog  = dialog
        self.repoman = repoman
        self.experiment = experiment

    def Start(self):
        self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        pass

    def IsRunning(self):
        return self.running

    def Run(self):
        
        try:

            workflows    = self.repoman.GetModel("Workflows")
            factors      = self.repoman.GetModel("Factors")
            nuclides     = self.repoman.GetModel("Nuclides")
            collections  = self.repoman.GetModel("Collections")

            w = workflows.get(self.experiment["calibration"])

            w.set_factors(factors)
            w.set_collections(collections)
            w.set_nuclides(nuclides)

            current_samples = []

            samples_db   = self.repoman.GetModel('Samples')
            groups       = self.repoman.GetModel("Groups")
            group = groups.get(self.experiment["calibration_set"])
            members = group.members()
            for s_id, nuclide in members:
                sample  = samples_db.get(s_id)
                sample.set_nuclide(nuclide)
                sample.set_experiment(self.experiment['name'])
                current_samples.append(sample)

            w.execute(self.experiment, current_samples, self.dialog, self.browser)

            for s in current_samples:
                s.remove_experiment(self.experiment['nuclide'], self.experiment["name"])
                
            self.running = False

            if self.dialog.cancel:
                self.experiment.remove_calibration()
                self.browser.calButton.Enable()
                self.browser.deleteButton.Enable()
                return

        except Exception, e:
            print e
            self.running = False
        
        evt = WorkflowDoneEvent()
        wx.PostEvent(self.browser, evt)

class ExperimentBrowser(wx.Frame):
    
    report_order = []
    report_order.append('nuclide')
    report_order.append('timestep')
    report_order.append('calibration')
    report_order.append('dating')
    report_order.append('calibration_set')
    report_order.append('geomagneticLatitude')
    report_order.append('geographicScaling')
    report_order.append('geomagneticIntensity')
    report_order.append('seaLevel')
    report_order.append('psi_mu_0')
    report_order.append('phi_mu_f0')
    report_order.append('slowMuonPerc')
    report_order.append('post_calibrated_slowMuon')
    report_order.append('fastMuonPerc')
    report_order.append('post_calibrated_fastMuon')
    report_order.append('psi_ca_0')
    report_order.append('psi_ca_uncertainty')
    report_order.append('psi_k_0')
    report_order.append('psi_k_uncertainty')
    report_order.append('Pf_0')
    report_order.append('Pf_uncertainty')
    report_order.append('psi_spallation_nuclide')
    report_order.append('psi_spallation_uncertainty')
    report_order.append('sample_size')
    report_order.append('probability')
    report_order.append('chi_square')
    
    @staticmethod
    def report_cmp(x,y):
        return cmp(ExperimentBrowser.report_order.index(x), ExperimentBrowser.report_order.index(y))

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Experiment Browser')
        
        self.repoman = repoman
        self.objs = []

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.menuBar   = wx.MenuBar()
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected collection items.")
        
        editMenu.Enable(wx.ID_COPY, False)
        
        self.menuBar.Append(editMenu, "Edit")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        self.statusbar = self.CreateStatusBar()
        
        self.experiments = self.repoman.GetModel("Experiments")
        self.nuclides = self.repoman.GetModel("Nuclides")        

        self.tree   = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_MULTIPLE|wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot("Experiments")
        self.tree.Expand(root)
        
        self.grid   = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1,1)
        self.grid.SetCellValue(0,0, "Select one or more Experiments")
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
        
        self.addButton    = wx.Button(self, wx.ID_ANY, "Create Experiment...")
        self.calButton    = wx.Button(self, wx.ID_ANY, "Calibrate Experiment...")
        self.deleteButton = wx.Button(self, wx.ID_ANY, "Delete Experiment...")
        
        self.calButton.Disable()
        self.deleteButton.Disable()

        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(self.tree, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        columnSizer.Add(self.grid, proportion=2, border=5, flag=wx.ALL|wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.calButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.deleteButton, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, flag=wx.LEFT)

        self.SetSizer(sizer)
        self.SetMinSize((540, 380))
        self.SetSize((540, 380))
        self.Layout()
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/expbrowser/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/expbrowser/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed, self.tree)
        
        self.Bind(wx.EVT_BUTTON, self.OnCreate, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnCalibrate, self.calButton)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, self.deleteButton)

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(EVT_WORKFLOW_DONE, self.OnCalibrationDone)
        self.Bind(EVT_CALIBRATION_PLOT, self.OnCalibrationInfo)

        repoman.AddWindow(self)
    
    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().expBrowser = None
        del(self.GetParent().expBrowser)
        self.Destroy()
    
    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/expbrowser/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/expbrowser/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnRangeSelect(self, event):

        start = event.GetTopLeftCoords()[0]
        stop  = event.GetBottomRightCoords()[0]
        
        if event.Selecting():
            # print "Selecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop+1):
                self.selected_rows.add(i)
            # print "selected rows: %s" % self.selected_rows
        else:
            # print "DeSelecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop+1):
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
                    value = value[0:pos] + value[pos+5:len(value)]

                while value.find("</sup>") != -1:
                    pos = value.find("</sup>")
                    value = value[0:pos] + value[pos+6:len(value)]
                
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
            self.grid.SetCellValue(0,0, "Select one or more Experiments")
            self.grid.SetRowLabelValue(0, "")
            self.grid.SetColLabelValue(0, "No Experiments Selected")
        else:
            
            exps = [exp for exp in self.objs if isinstance(exp, Experiment)]
            nucs = [nuc for nuc in self.objs if not isinstance(nuc, Experiment)]
            for nuc in nucs:
                name, status = nuc.split(":")
                experiment_names = self.experiments.experimentsWithNuclide(name)
                if status == "calibrated":
                    experiment_names = [exp for exp in experiment_names if self.experiments.get(exp).is_calibrated()]
                else:
                    experiment_names = [exp for exp in experiment_names if not self.experiments.get(exp).is_calibrated()]
                for name in experiment_names:
                    exps.append(self.experiments.get(name))
                    
            if len(exps) == 0:
                self.grid.AppendRows(1)
                self.grid.AppendCols(1)
                self.grid.SetCellValue(0,0, "Select one or more Experiments")
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
        
        h,w = self.grid.GetSize()
        self.grid.SetSize((h+1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def ConfigureTree(self):
        root = self.tree.GetRootItem()
        self.tree.DeleteChildren(root)
        
        uncalItem = self.tree.AppendItem(root, "Uncalibrated")
        calItem   = self.tree.AppendItem(root, "Calibrated")
        
        uncalibrated = {}
        calibrated = {}
        
        nucs = self.nuclides.names()
        for name in nucs:
            # only add a nuclide to the tree if it has experiments associated with it
            exps = self.experiments.experimentsWithNuclide(name)
            cal    = [exp for exp in exps if self.experiments.get(exp).is_calibrated()]
            uncal  = [exp for exp in exps if not self.experiments.get(exp).is_calibrated()]
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
        self.objs  = [self.tree.GetItemPyData(item) for item in items]
        if len(items) == 0:
            self.calButton.Disable()
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
        
    def OnCalibrate(self, event):

        items        = self.tree.GetSelections()
        item         = items[0]
        experiment   = self.tree.GetItemPyData(item)
        
        samples_db   = self.repoman.GetModel('Samples')
        groups       = self.repoman.GetModel("Groups")
        group = groups.get(experiment["calibration_set"])
        members = group.members()

        max_age = 0

        for s_id, nuclide in members:
            sample  = samples_db.get(s_id)
            sample.set_nuclide(nuclide)
            if sample['independent age'] > max_age:
                max_age = sample['independent age']
        
        dialog = WorkflowProgress(self, "Calibrating Experiment '%s'" % (experiment['name']), len(members), max_age)
        dialog.Show()
        
        self.calButton.Disable()
        self.deleteButton.Disable()
        
        t = RunCalibrationThread(self, dialog, self.repoman, experiment)
        t.Start()

    def OnCalibrationInfo(self, event):
        self.last_calibration = {}
        self.last_calibration["RHS"] = event.data_rhs
        try:
            self.last_calibration["LHS"] = event.data_lhs
        except:
            self.last_calibration["LHS"] = None
            
        self.last_calibration["yhat"] = event.data_yhat
        self.last_calibration["Inv_calc_err"] = event.data_calc_err
        self.last_calibration["Inv_meas_err"] = event.data_meas_err
        
    def OnCalibrationDone(self, event):
        items        = self.tree.GetSelections()
        item         = items[0]
        experiment   = self.tree.GetItemPyData(item)
        
        try:
            dlg = DisplayCalibrationResults(self, self.last_calibration, experiment)
            if dlg.ShowModal() == wx.ID_OK:
                self.objs = []
                self.grid.ClearSelection()
                self.ConfigureTree()
                self.ConfigureGrid()
                self.repoman.RepositoryModified()
            else:
                experiment.remove_calibration()
                self.calButton.Enable()
                self.deleteButton.Enable()
            dlg.Destroy()
        except Exception, e:
            print e
        
    def Level(self, item):
        if item == self.tree.GetRootItem():
            return 0
        return self.Level(self.tree.GetItemParent(item))+1
        
    def OnDelete(self, event):
        items        = self.tree.GetSelections()
        item         = items[0]
        experiment   = self.tree.GetItemPyData(item)

        if experiment.is_calibrated():
            dialog = wx.MessageDialog(None, 'Warning: deleting this experiment will strip data from all samples processed by it. Do you still want to delete this experiment?', "Calibrated Experiment", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_NO:
                return
                
        samples_db = self.repoman.GetModel('Samples')
        ids        = samples_db.ids()
        
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
        root  = self.tree.GetRootItem()
        items = self.tree.GetSelections()
        
        item  = event.GetItem()
        
        if item.IsOk():
            self.calButton.Disable()
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
                    if not exp.is_calibrated():
                        self.calButton.Enable(True)

            self.grid.ClearSelection()
            self.ConfigureGrid()

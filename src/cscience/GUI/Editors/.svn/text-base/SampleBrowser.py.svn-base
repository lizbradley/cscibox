"""
SampleBrowser.py

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

import os
import thread
import time

from ACE.GUI.Dialogs.AboutBox               import AboutBox
from ACE.GUI.Dialogs.DisplayImportedSamples import DisplayImportedSamples
from ACE.GUI.Dialogs.WorkflowProgress       import WorkflowProgress

from ACE.GUI.Editors.AttEditor              import AttEditor
from ACE.GUI.Editors.CalibrationSetBrowser  import CalibrationSetBrowser
from ACE.GUI.Editors.CollectionBrowser      import CollectionBrowser
from ACE.GUI.Editors.ExperimentBrowser      import ExperimentBrowser
from ACE.GUI.Editors.NuclideEditor          import NuclideEditor
from ACE.GUI.Editors.FilterEditor           import FilterEditor
from ACE.GUI.Editors.GroupEditor            import GroupEditor

from ACE.GUI.Events.ProgressEvents import WorkflowDoneEvent
from ACE.GUI.Events.ProgressEvents import UpdateTotalSamples
from ACE.GUI.Events.ProgressEvents import EVT_WORKFLOW_DONE

from ACE.GUI.Util.SampleBrowserView        import SampleBrowserView
from ACE.GUI.Util.Graphing                 import Plot

from ACE.GUI.Dialogs.ExperimentSelector       import ExperimentSelector

from ACE.Framework.Sample                  import Sample
from ACE.Framework.Group                   import Group
from ACE.Framework.VirtualSample           import VirtualSample
from ACE.GUI.Editors.ViewEditor            import ViewEditor
from ACE.GUI.Editors.TemplateEditor        import TemplateEditor

from ACE.Framework import Attributes

import Calvin.argue

import pylab
import matplotlib.transforms
from numpy import arange, array
from scipy import ndimage

def sort_none_last(x,y):
    # print "SORTING: (%r,%r)" % (x[0], y[0])
    if x[0] is None and y[0] is None:
        return 0
    if x[0] is None:
        return 1
    if y[0] is None:
        return -1
    return cmp(x,y)

class RunDatingThread:
    def __init__(self, browser, dialog, repoman, experiment, samples):
        self.browser    = browser
        self.dialog     = dialog
        self.repoman    = repoman
        self.experiment = experiment
        self.samples    = samples

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

            w = workflows.get(self.experiment["dating"])

            w.set_factors(factors)
            w.set_collections(collections)
            w.set_nuclides(nuclides)

            w.execute(self.experiment, self.samples, self.dialog, self.browser)

            self.browser.importButton.Enable()
            self.browser.exportView.Enable()
            self.browser.applyExperiment.Enable()
            self.browser.calvinButton.Enable()
            self.browser.plotSort.Enable()
            
            if self.dialog.cancel:
                for s in self.samples:
                    s.remove_experiment(self.experiment['nuclide'], self.experiment['name'])
                    
                self.running = False
                
                return
            
            for s in self.samples:
                if s['id'] in self.browser.saturated:
                    s.remove_experiment(self.experiment['nuclide'], self.experiment['name'])
                else:
                    nuclide_ALL      = nuclides.get("ALL")
                    nuclide_specific = nuclides.get(self.experiment["nuclide"])
                    
                    atts = self.repoman.GetModel("Attributes")

                    atts_current = []
                    atts_current.extend(nuclide_ALL.required_atts())
                    atts_current.extend(nuclide_ALL.optional_atts())
                    atts_current.extend(nuclide_specific.required_atts())
                    atts_current.extend(nuclide_specific.optional_atts())
                    atts_current.extend(atts.output_atts())

                    atts = s.properties_for_experiment(self.experiment['nuclide'], self.experiment['name'])
                    for att in atts:
                        if not att in atts_current:
                            try:
                                s.remove(self.experiment['nuclide'], self.experiment['name'], att)
                            except:
                                pass

            self.running = False
        except Exception, e:
            print e
            self.running = False
        
        evt = WorkflowDoneEvent()
        wx.PostEvent(self.browser, evt)

class SampleBrowser(wx.Frame):
    def __init__(self, repoman):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title='ACE: Age Calculation Environment', size=(540, 380))
        self.CreateStatusBar()
        self.CreateMenus()
        self.repoman = repoman
        self.NCEP    = None
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/samplebrowser/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/samplebrowser/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetMinSize((540, 380))
        self.SetPosition(loc)
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.browser_view = SampleBrowserView(config)
        
        self.selected_rows = set()

    def CreateMenus(self):
        self.menuBar   = wx.MenuBar()

        fileMenu  = wx.Menu()
        aboutItem = fileMenu.Append(wx.ID_ABOUT, "About ACE", "View Credits")
        fileMenu.AppendSeparator()
        switchItem   = fileMenu.Append(wx.ID_OPEN, "Switch Repository\tCtrl-O", "Switch to a different ACE Repository")
        fileMenu.AppendSeparator()
        closeItem = fileMenu.Append(wx.ID_CLOSE, "Close Top Window\tCtrl-W", "Close the top window. Note: Closing last window will cause applicatin to quit.")
        fileMenu.AppendSeparator()
        saveItem   = fileMenu.Append(wx.ID_SAVE, "Save Repository\tCtrl-S", "Save changes to current ACE Repository")
        fileMenu.AppendSeparator()
        quitItem  = fileMenu.Append(wx.ID_EXIT, "Quit ACE\tCtrl-Q", "Quit ACE")
        
        fileMenu.Enable(wx.ID_SAVE, False)
        
        self.Bind(wx.EVT_MENU, self.OnAboutBox, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnSwitch, switchItem)
        self.Bind(wx.EVT_MENU, self.OnCloseTopWindow, closeItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected samples.")
        
        editMenu.Enable(wx.ID_COPY, False)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        toolMenu           = wx.Menu()
        attEditor          = toolMenu.Append(wx.ID_ANY, "Attribute Editor\tCtrl-1", "Edit the list of attributes that can appear on samples in ACE")
        viewEditor         = toolMenu.Append(wx.ID_ANY, "View Editor\tCtrl-2", "Edit the list of views that can filter the display of samples in ACE")
        nuclideEditor      = toolMenu.Append(wx.ID_ANY, "Nuclide Editor\tCtrl-3", "Edit the list of nuclides that can be analyzed by ACE")
        calibrationBrowser = toolMenu.Append(wx.ID_ANY, "Calibration Set Browser\tCtrl-4", "Browse Calibration Data Sets")
        templateEditor     = toolMenu.Append(wx.ID_ANY, "Template Editor\tCtrl-5", "Edit the list of templates that ACE supports")
        collectionBrowser  = toolMenu.Append(wx.ID_ANY, "Collection Browser\tCtrl-6", "Browse and Import Data Collections")
        experimentBrowser  = toolMenu.Append(wx.ID_ANY, "Experiment Browser\tCtrl-7", "Browse Existing Experiments and Create New Experiments")
        filterEditor       = toolMenu.Append(wx.ID_ANY, "Filter Editor\tCtrl-8", "Create and Edit ACE Filters for use in Sample Browser")
        groupEditor        = toolMenu.Append(wx.ID_ANY, "Group Editor\tCtrl-9", "Create and Edit Groups of Samples")
        
        self.Bind(wx.EVT_MENU, self.OnAttEditor, attEditor)
        self.Bind(wx.EVT_MENU, self.OnViewEditor, viewEditor)
        self.Bind(wx.EVT_MENU, self.OnNucEditor, nuclideEditor)
        self.Bind(wx.EVT_MENU, self.OnCalibrationBrowser, calibrationBrowser)
        self.Bind(wx.EVT_MENU, self.OnCollectionBrowser, collectionBrowser)
        self.Bind(wx.EVT_MENU, self.OnTemplateEditor, templateEditor)
        self.Bind(wx.EVT_MENU, self.OnExpBrowser, experimentBrowser)
        self.Bind(wx.EVT_MENU, self.OnFilterEditor, filterEditor)
        self.Bind(wx.EVT_MENU, self.OnGroupEditor, groupEditor)

        utilMenu           = wx.Menu()
        atFacItem          = utilMenu.Append(wx.ID_ANY, "Atmospheric Parameters")
        self.bpItem        = utilMenu.Append(wx.ID_ANY, "Multiple Nuclide Analysis")
        msfItem            = utilMenu.Append(wx.ID_ANY, "Snow Shielding")
        t30Item            = utilMenu.Append(wx.ID_ANY, "Topographic Shielding (30)")
        t45Item            = utilMenu.Append(wx.ID_ANY, "Topographic Shielding (45)")
        self.depthItem     = utilMenu.Append(wx.ID_ANY, "Production Rate Profile")
        
        self.Bind(wx.EVT_MENU, self.OnAttFac, atFacItem)
        self.Bind(wx.EVT_MENU, self.OnBananaPlot, self.bpItem)
        self.Bind(wx.EVT_MENU, self.OnSnowFactor, msfItem)
        self.Bind(wx.EVT_MENU, self.OnTopo30, t30Item)
        self.Bind(wx.EVT_MENU, self.OnTopo45, t45Item)
        self.Bind(wx.EVT_MENU, self.OnDepthProfile, self.depthItem)
        
        self.bpItem.Enable(False)
        self.depthItem.Enable(False)
        
        self.menuBar.Append(fileMenu, "File")
        self.menuBar.Append(editMenu, "Edit")
        self.menuBar.Append(toolMenu, "Tools")
        self.menuBar.Append(utilMenu, "Utilities")

        self.SetMenuBar(self.menuBar)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/samplebrowser/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/samplebrowser/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnAboutBox(self, event):
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnQuit(self, event):
        self.OnClose(event)
        self.Close()
        
    def OnSwitch(self, event):
        self.repoman.handleSwitch()
        if self.repoman.repo != None:
            self.SetTitle('ACE: Age Calculation Environment: ' + self.repoman.repo)
        
    def OnOpen(self, event):
        result = self.repoman.handleOpen()
        if result:
            self.CreateVirtualSamples()
            self.CreateSampleBrowser()
            self.ConfigureFilter()
            self.ConfigureSort()
            self.ApplyFilter()
            self.FilterCalibrationSamples()
            self.ApplyTextSearchFilter()
            self.ApplySort()
            self.ConfigureGrid()
        return result

    def OnClose(self, event):
        self.repoman.handleClose()
        self.ClearSampleBrowser()
        
    def OnCloseTopWindow(self, event):
        windows = wx.GetTopLevelWindows()
        window  = windows[len(windows)-1]
        window.Close()
        
    def OnSave(self, event):
        self.repoman.handleSave()
        if self.repoman.repo != None:
            self.SetTitle('ACE: Age Calculation Environment: ' + self.repoman.repo)

    def OnAttEditor(self, event):
        if hasattr(self, "attEditor") == False:
            self.attEditor = AttEditor(self, self.repoman)
            self.attEditor.Show()
        self.attEditor.Raise()
        
    def GetAttEditor(self):
        if hasattr(self, "attEditor"):
            return self.attEditor
        else:
            return None

    def OnCalibrationBrowser(self, event):
        if hasattr(self, "calibrationBrowser") == False:
            self.calibrationBrowser = CalibrationSetBrowser(self, self.repoman)
            self.calibrationBrowser.Show()
        self.calibrationBrowser.Raise()

    def GetCalibrationBrowser(self):
        if hasattr(self, "calibrationBrowser"):
            return self.calibrationBrowser
        else:
            return None

    def OnCollectionBrowser(self, event):
        if hasattr(self, "collectionBrowser") == False:
            self.collectionBrowser = CollectionBrowser(self, self.repoman)
            self.collectionBrowser.Show()
        self.collectionBrowser.Raise()

    def GetCollectionBrowser(self):
        if hasattr(self, "collectionBrowser"):
            return self.collectionBrowser
        else:
            return None

    def OnExpBrowser(self, event):
        if hasattr(self, "expBrowser") == False:
            self.expBrowser = ExperimentBrowser(self, self.repoman)
            self.expBrowser.Show()
        self.expBrowser.Raise()

    def GetExpBrowser(self):
        if hasattr(self, "expBrowser"):
            return self.expBrowser
        else:
            return None

    def OnNucEditor(self, event):
        if hasattr(self, "nucEditor") == False:
            self.nucEditor = NuclideEditor(self, self.repoman)
            self.nucEditor.Show()
        self.nucEditor.Raise()

    def GetNucEditor(self):
        if hasattr(self, "nucEditor"):
            return self.nucEditor
        else:
            return None

    def OnTemplateEditor(self, event):
        if hasattr(self, "templateEditor") == False:
            self.templateEditor = TemplateEditor(self, self.repoman)
            self.templateEditor.Show()
        self.templateEditor.Raise()

    def GetTemplateEditor(self):
        if hasattr(self, "templateEditor"):
            return self.templateEditor
        else:
            return None

    def OnViewEditor(self, event):
        if hasattr(self, "viewEditor") == False:
            self.viewEditor = ViewEditor(self, self.repoman)
            self.viewEditor.Show()
        self.viewEditor.Raise()

    def GetViewEditor(self):
        if hasattr(self, "viewEditor"):
            return self.viewEditor
        else:
            return None
        
    def OnFilterEditor(self, event):
        if hasattr(self, "filterEditor") == False:
            self.filterEditor = FilterEditor(self, self.repoman)
            self.filterEditor.Show()
        self.filterEditor.Raise()

    def GetFilterEditor(self):
        if hasattr(self, "filterEditor"):
            return self.filterEditor
        else:
            return None

    def OnGroupEditor(self, event):
        if hasattr(self, "groupEditor") == False:
            self.groupEditor = GroupEditor(self, self.repoman)
            self.groupEditor.Show()
        self.groupEditor.Raise()

    def OnAttFac(self, event):
        from ACE.GUI.Util.AtmosphericFactors import Calculator
        dlg = Calculator(self.repoman)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnBananaPlot(self, event):
        
        first  = sorted(list(self.selected_rows))[0]
        second = sorted(list(self.selected_rows))[1]
        
        first_sample  = self.displayed_samples[first]
        second_sample = self.displayed_samples[second]
        
        from ACE.GUI.Util.BananaPlot import Calculator
        dlg = Calculator(first_sample, second_sample)

    def OnSnowFactor(self, event):
        from ACE.GUI.Util.MeasuredSnowFactor import Calculator
        dlg = Calculator()
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnTopo30(self, event):
        from ACE.GUI.Util.TopographyFactor30 import Calculator
        dlg = Calculator()
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnTopo45(self, event):
        from ACE.GUI.Util.TopographyFactor45 import Calculator
        dlg = Calculator()
        dlg.ShowModal()
        dlg.Destroy()

    def OnDepthProfile(self, event):
        from ACE.GUI.Util.DepthProfile import Calculator
        index  = list(self.selected_rows)[0]
        sample = self.displayed_samples[index]
        dlg = Calculator(sample)
        
    def GetGroupEditor(self):
        if hasattr(self, "groupEditor"):
            return self.groupEditor
        else:
            return None

    def GetMenuBar(self):
        return self.menuBar
        
    def GetRepoMan(self):
        return self.repoman
        
    def OnCopy(self, event):
        indexes = sorted(list(self.selected_rows))
        samples = [self.displayed_samples[index] for index in indexes]
        
        view_name = self.browser_view.get_view()
        view      = self.repoman.GetModel("Views").get(view_name)
        atts      = view.atts()
        if "experiment" not in atts:
            atts.insert(0, "experiment")
        else:
            # insure that experiment is always first column in sample browser display
            atts.remove("experiment")
            atts.insert(0, "experiment")

        # do not need id appearing in columns, since id is used to label each row
        if "id" in atts:
            atts.remove("id")
        
        result = "\t"
        for att in atts:
            result = result + att + "\t"
        
        result = result[0:-1]
        result = result + os.linesep
        
        for sample in samples:
            result = result + sample['id'] + "\t"
            for att in atts:
                if isinstance(sample[att], float):
                    result = result + "%.2f" % (sample[att]) + "\t"
                else:
                    result = result + str(sample[att]) + "\t"
            result = result[0:-1]
            result = result + os.linesep

        data = wx.TextDataObject()
        data.SetText(result)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        
    def CreateVirtualSamples(self):
        self.samples = []
        samples_db = self.repoman.GetModel("Samples")
        ids = samples_db.ids()
        for id in ids:
            sample = samples_db.get(id)
            for nuclide in sample.nuclides():
                experiments = sample.experiments(nuclide)
                if len(experiments) > 1:
                    experiments.remove('input')
                for experiment in experiments:
                    self.samples.append(VirtualSample(sample, nuclide, experiment))

    def CreateSampleBrowser(self):
        self.DestroyChildren()
        self.CreateStatusBar()
        
        views = self.repoman.GetModel("Views")
        view_names = views.names()
        view_names.remove("All")
        view_names.insert(0, "All")
        
        viewLabel         = wx.StaticText(self, wx.ID_ANY, "View:")
        self.selectedView = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_view(), choices=view_names, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        
        filters      = self.repoman.GetModel("Filters")
        filter_names = filters.names()
        filter_names.insert(0, "<No Filter>")
        
        filterLabel         = wx.StaticText(self, wx.ID_ANY, "Filter:")
        self.selectedFilter = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_filter(), choices=filter_names, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        
        self.filterDescription = wx.StaticText(self, wx.ID_ANY, "No Filter Selected")
        self.includeCalSamplesBox  = wx.CheckBox(self, -1, "Include Calibration Samples")
        
        rowOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowOneSizer.Add(viewLabel, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.selectedView, border=5, flag=wx.ALL)
        rowOneSizer.Add(filterLabel, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.selectedFilter, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.filterDescription, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.includeCalSamplesBox, border=5, flag=wx.ALL)
        
        sortByLabel = wx.StaticText(self, wx.ID_ANY, "Sort by")
        self.primarySort = wx.ComboBox(self, wx.ID_ANY, value="Not Implemented", choices=["Not Implemented"], style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
        andByLabel = wx.StaticText(self, wx.ID_ANY, "and then by")
        self.secondarySort = wx.ComboBox(self, wx.ID_ANY, value="Not Implemented", choices=["Not Implemented"], style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
        self.sortDirection = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_direction(), choices=["Ascending", "Descending"], style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
        self.plotSort      = wx.Button(self, wx.ID_ANY, "Plot Sort Attributes...")
        
        rowTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowTwoSizer.Add(sortByLabel, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.primarySort, border=5, flag=wx.ALL)
        rowTwoSizer.Add(andByLabel, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.secondarySort, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.sortDirection, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.plotSort, border=5, flag=wx.ALL)

        searchLabel    = wx.StaticText(self, wx.ID_ANY, "Search:")
        self.searchBox = wx.TextCtrl(self, wx.ID_ANY, size=(300,-1))
        self.exactBox  = wx.CheckBox(self, -1, "Use Exact Match")
        
        rowThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowThreeSizer.Add(searchLabel, border=5, flag=wx.ALL)
        rowThreeSizer.Add(self.searchBox, border=5, flag=wx.ALL)
        rowThreeSizer.Add(self.exactBox, border=5, flag=wx.ALL)
        
        self.grid   = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1,1)
        self.grid.SetCellValue(0,0, "The current view has no attributes defined for it.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "Invalid View")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
                
        self.importButton    = wx.Button(self, wx.ID_ANY, "Import Samples...")
        self.applyExperiment = wx.Button(self, wx.ID_ANY, "Date Samples...")
        self.makeExperiment  = wx.Button(self, wx.ID_ANY, "Make Experiment...")
        self.calvinButton    = wx.Button(self, wx.ID_ANY, "Analyze Ages...")
        self.deleteSample    = wx.Button(self, wx.ID_ANY, "Delete Sample...")
        self.stripExperiment = wx.Button(self, wx.ID_ANY, "Strip Experiment...")
        self.exportView      = wx.Button(self, wx.ID_ANY, "Export Samples...")
        
        self.stripExperiment.Disable()
        self.deleteSample.Disable()
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.importButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.applyExperiment, border=5, flag=wx.ALL)
        buttonSizer.Add(self.makeExperiment, border=5, flag=wx.ALL)
        buttonSizer.Add(self.calvinButton, border=5, flag=wx.ALL)
        buttonSizer.Add(self.deleteSample, border=5, flag=wx.ALL)
        buttonSizer.Add(self.stripExperiment, border=5, flag=wx.ALL)
        buttonSizer.Add(self.exportView, border=5, flag=wx.ALL)
        
        columnSizer = wx.BoxSizer(wx.VERTICAL)
        columnSizer.Add(rowOneSizer, border=2, flag=wx.ALL|wx.EXPAND)
        columnSizer.Add(rowTwoSizer, border=2, flag=wx.ALL|wx.EXPAND)
        columnSizer.Add(rowThreeSizer, border=2, flag=wx.ALL|wx.EXPAND)
        columnSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        columnSizer.Add(buttonSizer, border=2, flag=wx.ALL)

        self.SetSizer(columnSizer)
        self.Layout()
        
        if self.repoman.repo != None:
            self.SetTitle('ACE: Age Calculation Environment: ' + self.repoman.repo)
        else:
            self.SetTitle('ACE: Age Calculation Environment')
        
        self.Bind(wx.EVT_COMBOBOX, self.OnViewSelect, self.selectedView)
        self.Bind(wx.EVT_COMBOBOX, self.OnFilterSelect, self.selectedFilter)
        self.Bind(wx.EVT_CHECKBOX, self.OnFilterCalibrationSamples, self.includeCalSamplesBox)
        self.Bind(wx.EVT_COMBOBOX, self.OnSortDirection, self.sortDirection)
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeSort, self.primarySort)
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeSort, self.secondarySort)
        self.Bind(wx.EVT_BUTTON, self.OnPlotSort, self.plotSort)
        self.Bind(wx.EVT_BUTTON, self.OnImportSamples, self.importButton)
        self.Bind(wx.EVT_BUTTON, self.OnExportView, self.exportView)
        self.Bind(wx.EVT_BUTTON, self.OnDating, self.applyExperiment)
        self.Bind(wx.EVT_BUTTON, self.OnExpBrowser, self.makeExperiment)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSample, self.deleteSample)
        self.Bind(wx.EVT_BUTTON, self.OnStripExperiment, self.stripExperiment)
        self.Bind(wx.EVT_TEXT, self.OnTextSearchUpdate, self.searchBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnTextSearchUpdate, self.exactBox)
        
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.Bind(wx.EVT_BUTTON, self.OnRunCalvin, self.calvinButton)
        
        self.Bind(EVT_WORKFLOW_DONE, self.OnDatingDone)

    def ConfigureFilter(self):
        filter_name = self.browser_view.get_filter()
        if filter_name == "<No Filter>":
            self.filterDescription.SetLabel("No Filter Selected")
        else:
            filters = self.repoman.GetModel("Filters")
            the_filter = filters.get(filter_name)
            self.filterDescription.SetLabel(the_filter.description())
        
    def ApplyFilter(self):
        self.displayed_samples = None
        filter_name = self.browser_view.get_filter()
        if filter_name == "<No Filter>":
            self.filtered_samples = list(self.samples)
        else:
            filters = self.repoman.GetModel("Filters")
            the_filter = filters.get(filter_name)
            self.filtered_samples = filter(the_filter.apply, self.samples)

    def FilterCalibrationSamples(self):
        if not self.includeCalSamplesBox.IsChecked(): 
            samples = []
            for sample in self.filtered_samples:
                if sample["independent age"] is None:
                    samples.append(sample)
            self.filtered_samples = samples

    def ApplyTextSearchFilter(self):
        value = self.searchBox.GetValue()
        
        if value != '':
            view_name = self.browser_view.get_view()
            view      = self.repoman.GetModel("Views").get(view_name)
            atts      = view.atts()
            
            # make sure we always search for experiment
            if "experiment" not in atts:
                atts.insert(0, "experiment")

            # make sure we always search for id
            if "id" not in atts:
                atts.insert(0, 'id')
                
            samples = []
            
            atts_db = self.repoman.GetModel("Attributes")
            
            if self.exactBox.IsChecked():
                samples_to_search = self.filtered_samples
            else:
                if self.displayed_samples is not None and len(value) > len(self.previous_query) and value.startswith(self.previous_query):
                    samples_to_search = self.displayed_samples
                else:
                    samples_to_search = self.filtered_samples
            
            for sample in samples_to_search:
                for att in atts:
                    if sample[att] is not None:
                        att_value = str(sample[att])
                        if self.exactBox.IsChecked():
                            if value == att_value:
                                samples.append(sample)
                                break
                        else:
                            if value in att_value:
                                samples.append(sample)
                                break
            self.displayed_samples = samples
            self.previous_query = value
        else:
            self.displayed_samples = self.filtered_samples
            self.previous_query = ''

    def ConfigureSort(self):
        view_name = self.browser_view.get_view()
        view      = self.repoman.GetModel("Views").get(view_name)
        atts      = view.atts()
        if "experiment" not in atts:
            atts.insert(0, "experiment")
        if "id" not in atts:
            atts.insert(0, "id")
            
        # previous_primary   = self.primarySort.GetStringSelection()
        # previous_secondary = self.secondarySort.GetStringSelection()

        previous_primary = self.browser_view.get_primary()
        previous_secondary = self.browser_view.get_secondary()
        
        self.primarySort.Clear()
        self.secondarySort.Clear()
        
        for att in atts:
            self.primarySort.Append(att)
            self.secondarySort.Append(att)
            
        if previous_primary in atts:
            self.primarySort.SetStringSelection(previous_primary)
        else:
            self.primarySort.SetStringSelection("id")
            self.browser_view.set_primary("id")
            
        if previous_secondary in atts:
            self.secondarySort.SetStringSelection(previous_secondary)
        else:
            self.secondarySort.SetStringSelection("experiment")
            self.browser_view.set_secondary("experiment")
        
    def ApplySort(self):
        # primarySort   = self.primarySort.GetStringSelection()
        # secondarySort = self.secondarySort.GetStringSelection()

        primarySort   = self.browser_view.get_primary()
        secondarySort = self.browser_view.get_secondary()
        
        samples       = []
        
        for sample in self.displayed_samples:
            samples.append((sample[primarySort], sample[secondarySort], sample))
            
        if self.GetSortDirection():
            samples.sort(reverse=True)
        else:
            samples.sort(cmp=sort_none_last)
        
        self.displayed_samples = [item[2] for item in samples]
        
    def OnTextSearchUpdate(self, event):
        self.ApplyTextSearchFilter()
        self.ConfigureGrid()
        
    def OnExportView(self, event):
        
        view_name = self.browser_view.get_view()
        view      = self.repoman.GetModel("Views").get(view_name)
        atts      = view.atts()
        
        if "experiment" in atts:
            atts.remove("experiment")
            
        if "id" in atts:
            atts.remove("id")
            
        atts.insert(0, "experiment")
        atts.insert(0, "id")
        
        rows = []
        
        # add header labels
        rows.append(atts)
        
        for sample in self.displayed_samples:
            row = []
            for att in atts:
                row.append(sample[att])
            rows.append(row)
        
        wildcard = "CSV Files (*.csv)|*.csv|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(self, message="Save view in ...", defaultDir=os.getcwd(), defaultFile="view.csv", wildcard=wildcard, style=wx.SAVE|wx.CHANGE_DIR|wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        
            import csv
        
            tmp = open(path, "wb")
        
            writer = csv.writer(tmp)
        
            writer.writerows(rows)
        
            tmp.flush()
            tmp.close()
            
            the_dir = os.path.dirname(path)
            os.chdir(the_dir)
            
        dlg.Destroy()

    def OnPlotSort(self, event):
        graph = Plot(self.displayed_samples, self.browser_view.get_primary(), 
                     self.browser_view.get_secondary())
        graph.showFigure()
        
    def ConfigureGrid(self):
        self.grid.BeginBatch()
        
        view_name = self.browser_view.get_view()
        view      = self.repoman.GetModel("Views").get(view_name)
        atts      = view.atts()
        if "experiment" not in atts:
            atts.insert(0, "experiment")
        else:
            # insure that experiment is always first column in sample browser display
            atts.remove("experiment")
            atts.insert(0, "experiment")

        # do not need id appearing in columns, since id is used to label each row
        if "id" in atts:
            atts.remove("id")
        
        numCols   = len(atts)
        numRows   = len(self.displayed_samples)

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
        
        # set row names and width
        maxName = ""
        for index in range(len(self.displayed_samples)):
            name = self.displayed_samples[index]["id"]
            if len(name) > len(maxName):
                maxName = name
            self.grid.SetRowLabelValue(index, name)
        extent = self.grid.GetTextExtent(maxName)
        width = extent[0]
        if width == 0:
            width = 50
        else:
            width += 20
        self.grid.SetRowLabelSize(width)
            
        # set column names
        index = 0
        maxNumberOfSpaces = 0
        maxHeight = 0
        for att in atts:
            att_value      = att.replace(" ", "\n")
            numberOfSpaces = att.count(" ")
            self.grid.SetColLabelValue(index, att_value)
            extent = self.grid.GetTextExtent(att_value)
            height = extent[1]
            if height > maxHeight:
                maxHeight = height
            if numberOfSpaces > maxNumberOfSpaces:
                maxNumberOfSpaces = numberOfSpaces
            index += 1
        height = maxHeight * (maxNumberOfSpaces + 1)
        height += 20
        self.grid.SetColLabelSize(height)
        
        for row in range(len(self.displayed_samples)):
            index = 0
            for att in atts:
                sample = self.displayed_samples[row]
                value  = sample[att]
                
                if isinstance(value, float):
                    self.grid.SetCellValue(row, index, "%.2f" % value)
                else:
                    self.grid.SetCellValue(row, index, str(value))
                index += 1
            
        self.grid.AutoSize()
        
        h,w = self.grid.GetSize()
        self.grid.SetSize((h+1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def ClearSampleBrowser(self):
        
        self.DestroyChildren()
        self.CreateStatusBar()
        
        text = wx.StaticText(self, wx.ID_ANY, "ACE")
        font = text.GetFont()
        font.SetPointSize(24)
        text.SetFont(font)
        
        sizer = wx.GridBagSizer(10, 10)
        sizer.Add(text, pos=(0,0), border=10, flag=wx.ALIGN_CENTER|wx.ALL)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)

        self.SetSizer(sizer)
        self.Layout()

        self.SetTitle('ACE: Age Calculation Environment')

    def OnImportSamples(self, event):
        dialog = wx.FileDialog(None, "Select a CSV File containing Samples to be Imported or Updated:", style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        path   = dialog.GetPath()
        dialog.Destroy()
        
        if result == wx.ID_OK:

            if not os.path.isfile(path):
                dialog = wx.MessageDialog(None, "Did not select a file.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return

            required_atts = ['nuclide', 'longitude', 'latitude', 'elevation', 'density', 'shielding factor', 'id']
            
            input  = open(path, "rU")
            header = input.readline().strip()
            
            if header is None or header == '':
                dialog = wx.MessageDialog(None, "Selected file is empty.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
                
            num = header.count(',')
            
            if num < 6:
                dialog = wx.MessageDialog(None, "Selected file is not a csv file.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
                
            fields = header.split(',')
            
            for index, field in enumerate(fields):
                if field[0] == '"' and field[-1] == '"':
                    fields[index] = field[1:-1]
                if field[0] == "'" and field[-1] == "'":
                    fields[index] = field[1:-1]
            
            check  = [item for item in fields if item in required_atts]
            
            if not (sorted(check) == sorted(required_atts)):
                check = set(check)
                required = set(required_atts)
                diff     = list(required.difference(check))
                diff_str = ""
                for att in diff:
                    diff_str = diff_str + att + ", "
                diff_str = diff_str[0:-2]
                dialog = wx.MessageDialog(None, "CSV file is missing fields for required attributes: %s"  % (diff_str), "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
                
            rows = []
            
            atts = self.repoman.GetModel("Attributes")
            
            try:
            
                for line in input:
                    values = line.strip().split(',')
                
                    for index, value in enumerate(values):
                        if value[0] == '"' and value[-1] == '"':
                            values[index] = value[1:-1]
                        if value[0] == "'" and value[-1] == "'":
                            values[index] = value[1:-1]
                
                    items  = zip(fields, values)
                
                    mapping = {}
                
                    for item in items:
                        key = item[0]
                        att_type = atts.get_att_type(key)

                        if att_type == Attributes.INTEGER:
                            mapping[key] = int(item[1])
                        elif att_type == Attributes.FLOAT:
                            mapping[key] = float(item[1])
                        elif att_type == Attributes.BOOLEAN:
                            mapping[key] = (item[1].lower() == 'yes' or item[1].lower() == 'true' or
                                            item[1] == '1')
                        elif att_type == Attributes.STRING:
                            mapping[key] = item[1]
                        else:
                            print "Unknown Attribute Type During Import: %s" % att_type
                
                    rows.append(mapping)
                    
            except AssertionError:
                dialog = wx.MessageDialog(None, "Unknown Attribute: %s" % key, "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
            except Exception, e:
                print e
            
            if len(rows) == 0:
                dialog = wx.MessageDialog(None, "CSV file contains no data.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
            
            nuclides = [item['nuclide'] for item in rows]
            
            if len(set(nuclides)) > 1:
                dialog = wx.MessageDialog(None, "CSV file contains samples with different nuclides. Each sample in CSV file should have the same nuclide.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
                
            nuclide_key = list(nuclides)[0]
        
            nuclides_db = self.repoman.GetModel("Nuclides")
        
            if not nuclides_db.contains(nuclide_key):
                dialog = wx.MessageDialog(None, "Unknown Nuclide specified in CSV file.", "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
        
            nuclide       = nuclides_db.get(nuclide_key)
            nuclideALL    = nuclides_db.get('ALL')
            required_atts = nuclide.required_atts()
            required_atts.extend(nuclideALL.required_atts())
            for att in fields:
                try:
                    required_atts.remove(att)
                except Exception:
                    pass
            
            if len(required_atts) > 0:
                dialog = wx.MessageDialog(None, "Samples in CSV file are missing required attributes: %s" % (required_atts), "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
                dialog.Destroy()
                return
            
            for att in fields:
                result = nuclide.contains(att)
                if not result:
                    result = nuclideALL.contains(att)
                if not result:
                    dialog = wx.MessageDialog(None, "Samples in CSV file contain an unknown attribute: %s" % (att), "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
                    dialog.Destroy()
                    return
            
            dialog = DisplayImportedSamples(self, os.path.basename(path), fields, rows)
            result = dialog.ShowModal()
            add_sample_set   = dialog.add_sample_set()
            sample_set_value = dialog.get_sample_set_name()
            add_source = dialog.add_source()
            source_value = dialog.get_source()
            create_group = dialog.create_group()
            dialog.Destroy()
            
            try:

                if result != wx.ID_OK:
                    return
            
                if add_sample_set:
                    for item in rows:
                        item['sample set'] = sample_set_value
            
                if add_source:
                    for item in rows:
                        item['source'] = source_value
                    
                if create_group:
                    group_name = rows[0]['sample set']
                
                    groups = self.repoman.GetModel("Groups")
                    if group_name not in groups:
                        new_group = Group(group_name)
                        for item in rows:
                            new_group.add(item['id'], item['nuclide'])
                        groups.add(new_group)
                    else:
                        dialog = wx.MessageDialog(None, "Group name '%s' already exists. Auto-creation of new group cancelled. Your samples will still be imported." % (group_name), "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                        dialog.ShowModal()
                        dialog.Destroy()
                
                imported_samples = []

                samples = self.repoman.GetModel('Samples')
            
                for item in rows:

                    target_id = item['id']
                    
                    s = None
                
                    index = 0
                    while s is None:
                        if target_id in samples:
                            s = samples.get(target_id)
                            if item['nuclide'] in s:
                                index += 1
                                target_id = "%s %d" % (item['id'], index)
                                s = None
                        else:
                            s = Sample()

                    item['id'] = target_id
                    
                    s.set_nuclide(item['nuclide'])
                    s.set_experiment('input')
                    
                    for att in item.keys():
                        s[att] = item[att]
                    
                    # generate climate data if needed
                    if 'default sea-level temperature' not in item.keys():
                        s['default sea-level temperature'] = self.CalculateSeaLevelTemperature(s)
                    
                    if 'default sea-level pressure' not in item.keys():
                        s['default sea-level pressure'] = self.CalculateSeaLevelPressure(s)
                
                    if 'default lapse rate' not in item.keys():
                        s['default lapse rate'] = self.CalculateLapseRate(s)
        
                    if target_id not in samples:
                        samples.add(s)
                    
                    imported_samples.append(target_id)

            except Exception, e:
                print e

            # copy csv file into repository's imports directory
            imports_dir = self.repoman.GetImportsPath()
            
            import shutil
            shutil.copy(path, imports_dir)

            dlg = wx.SingleChoiceDialog(self, 'The following samples were imported and/or updated:', 'Import Results', imported_samples, wx.OK|wx.CENTRE)
            dlg.ShowModal()
            dlg.Destroy()
            
            self.repoman.RepositoryModified()
            
            self.CreateVirtualSamples()
            self.ConfigureFilter()
            self.ConfigureSort()
            self.ApplyFilter()
            self.FilterCalibrationSamples()
            self.ApplyTextSearchFilter()
            self.ApplySort()
            self.ConfigureGrid()

    def OnRunCalvin(self, event):
        """
        Runs Calvin on all highlighted samples, or all samples if none are
        highlighted.
        """
        
        if len(self.selected_rows) == 0:
            samples = self.displayed_samples
        else:
            indexes = sorted(list(self.selected_rows))
            samples = [self.displayed_samples[index] for index in indexes]
        
        Calvin.argue.analyzeSamples(samples, self.repoman)

    def OnFilterSelect(self, event):
        self.browser_view.set_filter(self.selectedFilter.GetStringSelection())
        self.ConfigureFilter()
        self.ApplyFilter()
        self.FilterCalibrationSamples()
        self.ApplyTextSearchFilter()
        self.ApplySort()
        self.ConfigureGrid()

    def OnFilterCalibrationSamples(self, event):
        self.ApplyFilter()
        self.FilterCalibrationSamples()
        self.ApplyTextSearchFilter()
        self.ApplySort()
        self.ConfigureGrid()
 
    def OnViewSelect(self, event):
        self.browser_view.set_view(self.selectedView.GetStringSelection())
        self.ConfigureSort()
        self.ApplyTextSearchFilter()
        self.ApplySort()
        self.ConfigureGrid()

    def GetSortDirection(self):
        # return true for descending, else return false
        # this corresponds to the expected value for the reverse parameter of the sort() method
        if self.browser_view.get_direction() == "Descending":
            return True
        return False

    def OnSortDirection(self, event):
        self.browser_view.set_direction(self.sortDirection.GetStringSelection())
        self.ApplySort()
        self.ConfigureGrid()

    def OnChangeSort(self, event):
        self.browser_view.set_primary(self.primarySort.GetStringSelection())
        self.browser_view.set_secondary(self.secondarySort.GetStringSelection())
        self.ApplySort()
        self.ConfigureGrid()
        
    def UpdateViews(self):
        # get current view
        view_name = self.browser_view.get_view()
        # get list of views
        view_names = self.repoman.GetModel("Views").names()
        
        self.selectedView.Clear()
        for view in view_names:
            self.selectedView.Append(view)
        
        # if current view has been deleted, then switch to "All" view
        if not view_name in view_names:
            self.selectedView.SetStringSelection('All')
            self.browser_view.set_view('All')
        else:
            self.selectedView.SetStringSelection(view_name)
            
        self.ConfigureSort()
        self.ApplySort()
        self.ConfigureGrid()
        self.Layout()

    def UpdateFilters(self):
        # get current filter
        filter_name = self.browser_view.get_filter()
        # get list of filters
        filter_names = self.repoman.GetModel("Filters").names()

        self.selectedFilter.Clear()
        self.selectedFilter.Append('<No Filter>')
        for item in filter_names:
            self.selectedFilter.Append(item)

        # if current filter has been deleted, then switch to "None" filter
        if not filter_name in filter_names:
            self.selectedFilter.SetStringSelection('<No Filter>')
            self.browser_view.set_filter('<No Filter>')
        else:
            self.selectedFilter.SetStringSelection(filter_name)

        self.ConfigureFilter()
        self.ApplyFilter()
        self.FilterCalibrationSamples()
        self.ApplyTextSearchFilter()
        self.ApplySort()
        self.ConfigureGrid()
        self.Layout()

    def LoadClimateData(self):
        self.NCEP = pylab.load(self.repoman.GetClimateDataPath())
        self.TemperatureData = self.NCEP[73:0:-1,:]
        self.PressureData    = self.NCEP[146:73:-1,:];
        self.LapseRateData   = self.NCEP[219:146:-1,:]
        self.GlobalLat       = arange(90, -91, -2.5)
        self.GlobalLon       = arange(0, 361, 2.5)
        self.x_factor        = len(self.GlobalLat) - 1
        self.y_factor        = len(self.GlobalLon) - 1
        
    def CalculateLocalCoordinates(self, s):
        localX = (max(self.GlobalLat) - s['latitude']) * self.x_factor / (max(self.GlobalLat) - min(self.GlobalLat)) + 1
        localY = s['longitude'] / max(self.GlobalLon) * self.y_factor + 1
        return array([[localX],[localY]])
        
    def CalculateSeaLevelTemperature(self, s):
        if self.NCEP is None:
            self.LoadClimateData()
        localCoords = self.CalculateLocalCoordinates(s)
        AnnualMeanTemp = ndimage.map_coordinates(self.TemperatureData, localCoords)
        format = "%3.1f" % (float(AnnualMeanTemp))
        return float(format)

    def CalculateSeaLevelPressure(self, s):
        if self.NCEP is None:
            self.LoadClimateData()
        localCoords = self.CalculateLocalCoordinates(s)
        AnnualMeanSLP = ndimage.map_coordinates(self.PressureData, localCoords)
        format = "%3.1f" % (float(AnnualMeanSLP))
        return float(format)

    def CalculateLapseRate(self, s):
        if self.NCEP is None:
            self.LoadClimateData()
        localCoords = self.CalculateLocalCoordinates(s)
        AnnualMeanLapse = ndimage.map_coordinates(self.LapseRateData, localCoords)
        format = "%3.1f" % (float(AnnualMeanLapse*-1))
        return float(format)

    def OnDating(self, event):

        dlg = ExperimentSelector(self, self.displayed_samples, self.repoman)
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.selectedExperiment.GetStringSelection()
            current_samples = dlg.current_samples
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        experiments = self.repoman.GetModel("Experiments")
        experiment = experiments.get(selection)
        
        dialog = WorkflowProgress(self, "Applying Experiment '%s'" % (experiment['name']), len(current_samples), 100000)
        dialog.Show()

        self.importButton.Disable()
        self.exportView.Disable()
        self.applyExperiment.Disable()
        self.calvinButton.Disable()
        self.plotSort.Disable()

        self.saturated = []

        t = RunDatingThread(self, dialog, self.repoman, experiment, current_samples)
        t.Start()

    def OnDatingDone(self, event):

        if len(self.saturated) > 0:
            dlg = wx.SingleChoiceDialog(self, "The following samples could not be processed by the experiment due to saturation:", "Saturated Samples", self.saturated, wx.OK|wx.CENTRE)
            dlg.ShowModal()
            dlg.Destroy()

            self.saturated = None
        
        self.repoman.RepositoryModified()
        self.CreateVirtualSamples()
        self.ConfigureFilter()
        self.ConfigureSort()
        self.ApplyFilter()
        self.FilterCalibrationSamples()
        self.ApplyTextSearchFilter()
        self.ApplySort()
        self.ConfigureGrid()

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

        self.stripExperiment.Disable()
        self.deleteSample.Disable()
        self.depthItem.Enable(False)
        self.bpItem.Enable(False)

        menuBar  = self.GetMenuBar()
        editMenu = menuBar.GetMenu(menuBar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            self.stripExperiment.Enable()
            self.deleteSample.Enable()
            editMenu.Enable(wx.ID_COPY, True)
            
        if len(self.selected_rows) == 1:
            index  = list(self.selected_rows)[0]
            sample = self.displayed_samples[index]
            if sample['production rate total'] > 0:
                self.depthItem.Enable(True)
            
        if len(self.selected_rows) == 2:
            first  = sorted(list(self.selected_rows))[0]
            second = sorted(list(self.selected_rows))[1]
            
            first_sample  = self.displayed_samples[first]
            second_sample = self.displayed_samples[second]
            
            if first_sample.nuclide != second_sample.nuclide:
                if first_sample.experiment != "input" and second_sample.experiment != "input":
                    self.bpItem.Enable(True)
            
    def OnStripExperiment(self, event):
        
        indexes = sorted(list(self.selected_rows))
        samples = [self.displayed_samples[index] for index in indexes]
        
        dialog = wx.MessageDialog(None, 'This operation will strip the selected experiments from the selected samples. (Note: The input experiment cannot be deleted.) Are you sure you want to do this?', "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
        if dialog.ShowModal() == wx.ID_YES:
            for sample in samples:
                sample.remove_experiment()
        
            self.grid.ClearSelection()
            self.selected_rows = set()
            self.repoman.RepositoryModified()
            self.CreateVirtualSamples()
            self.ConfigureFilter()
            self.ConfigureSort()
            self.ApplyFilter()
            self.FilterCalibrationSamples()
            self.ApplyTextSearchFilter()
            self.ApplySort()
            self.ConfigureGrid()

    def OnDeleteSample(self, event):
        
        indexes = sorted(list(self.selected_rows))
        samples = [self.displayed_samples[index] for index in indexes]
        ids     = [sample['id'] for sample in samples]
        
        # eliminate duplicate ids
        ids     = sorted(list(set(ids)))
        
        # get calibration sets, loop through and make sure selected sample is not a member
        samples_db = self.repoman.GetModel("Samples")
        groups     = self.repoman.GetModel("Groups")
        names      = groups.names()
        
        for name in names:
            group = groups.get(name)
            g_ids = group.get_ids()
            ids   = [id for id in ids if id not in g_ids]
            
        if len(ids) == len(samples):
            explanation = ""
        else:
            explanation = ". Note: Some samples could not be deleted because they are members of groups."

        if len(ids) == 0:
            if len(samples) > 1:
                dialog = wx.MessageDialog(None, 'The selected samples are members of groups and cannot be deleted.', 'Cannot Delete Samples', wx.OK | wx.ICON_INFORMATION)
            else:
                dialog = wx.MessageDialog(None, 'The selected sample is a member of a group and cannot be deleted.', 'Cannot Delete Sample', wx.OK | wx.ICON_INFORMATION)                
            dialog.ShowModal()
        else:
            dialog = wx.MessageDialog(None, 'Are you sure that you want to delete the following samples: %s%s' % (ids, explanation), "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_YES:
                for id in ids:
                    samples_db.remove(id)
                self.grid.ClearSelection()
                self.selected_rows = set()
                self.repoman.RepositoryModified()
                self.CreateVirtualSamples()
                self.ConfigureFilter()
                self.ConfigureSort()
                self.ApplyFilter()
                self.FilterCalibrationSamples()
                self.ApplyTextSearchFilter()
                self.ApplySort()
                self.ConfigureGrid()

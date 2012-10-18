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

import os
import thread

from cscience import datastore
from cscience.GUI import events
from cscience.GUI.Editors import AttEditor, MilieuBrowser, ComputationPlanBrowser, \
            FilterEditor, GroupEditor, TemplateEditor, ViewEditor, MemoryFrame
from cscience.GUI.Util import SampleBrowserView, Plot
from cscience.framework import Group, Sample, VirtualSample

import calvin.argue

def sort_none_last(x, y):
    # print "SORTING: (%r,%r)" % (x[0], y[0])
    if x[0] is None and y[0] is None:
        return 0
    if x[0] is None:
        return 1
    if y[0] is None:
        return -1
    return cmp(x, y)

class RunDatingThread:
    def __init__(self, browser, dialog, experiment, samples):
        self.browser = browser
        self.dialog = dialog
        self.computation_plan = experiment
        self.samples = samples

    def Start(self):
        self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        pass

    def IsRunning(self):
        return self.running

    def Run(self):
        
        try:
            w = datastore.workflows[self.computation_plan['workflow']]

            w.execute(self.computation_plan, self.samples, self.dialog, self.browser)

            self.browser.importButton.Enable()
            self.browser.exportView.Enable()
            self.browser.applyExperiment.Enable()
            self.browser.calvinButton.Enable()
            self.browser.plotSort.Enable()
            
            if self.dialog.cancel:
                for s in self.samples:
                    del s.sample[self.computation_plan['name']]
                    
                self.running = False
                return
            
            for s in self.samples:
                if s['id'] in self.browser.saturated:
                    del s.sample[self.computation_plan['name']]
                else:
                    s.remove_exp_intermediates()

            self.running = False
        except Exception, e:
            self.running = False
        
        evt = events.WorkflowDoneEvent()
        wx.PostEvent(self.browser, evt)

class SampleBrowser(MemoryFrame):
    
    framename = 'samplebrowser'
    
    def __init__(self):
        super(SampleBrowser, self).__init__(parent=None, id=wx.ID_ANY, 
                                            title='CScience', size=(540, 380))
        
        #TODO: need an EVT_CLOSE handler for this guy (save repo offer)
        self.CreateStatusBar()
        self.CreateMenus()

        self.browser_view = SampleBrowserView()        
        self.selected_rows = set()

    def CreateMenus(self):
        self.menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        aboutItem = fileMenu.Append(wx.ID_ABOUT, "About CScience", "View Credits")
        fileMenu.AppendSeparator()
        switchItem = fileMenu.Append(wx.ID_OPEN, "Switch Repository\tCtrl-O", 
                                     "Switch to a different CScience Repository")
        fileMenu.AppendSeparator()
        saveItem = fileMenu.Append(wx.ID_SAVE, "Save Repository\tCtrl-S", 
                                   "Save changes to current CScience Repository")
        fileMenu.AppendSeparator()
        quitItem = fileMenu.Append(wx.ID_EXIT, "Quit CScience\tCtrl-Q", 
                                   "Quit CScience")
        
        fileMenu.Enable(wx.ID_SAVE, False)
        
        self.Bind(wx.EVT_MENU, self.show_about, aboutItem)
        self.Bind(wx.EVT_MENU, self.change_repository, switchItem)
        self.Bind(wx.EVT_MENU, self.save_repository, saveItem)
        self.Bind(wx.EVT_MENU, self.quit, quitItem)
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected samples.")
        
        editMenu.Enable(wx.ID_COPY, False)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        toolMenu = wx.Menu()
        filterEditor = toolMenu.Append(wx.ID_ANY, "Filter Editor\tCtrl-1", 
                "Create and Edit CScience Filters for use in the Sample Browser")
        viewEditor = toolMenu.Append(wx.ID_ANY, "View Editor\tCtrl-2", 
                "Edit the list of views that can filter the display of samples in CScience")
        toolMenu.AppendSeparator()
        attEditor = toolMenu.Append(wx.ID_ANY, "Attribute Editor\tCtrl-3", 
                "Edit the list of attributes that can appear on samples in CScience")
        toolMenu.AppendSeparator()
        groupEditor = toolMenu.Append(wx.ID_ANY, "Core Editor\tCtrl-4", 
                "Collate Samples Belonging to Specific Cores")
        toolMenu.AppendSeparator()
        templateEditor = toolMenu.Append(wx.ID_ANY, "Template Editor\tCtrl-5", 
                "Edit the list of templates for the CScience Paleobase")
        collectionBrowser = toolMenu.Append(wx.ID_ANY, "Milieu Browser\tCtrl-6", 
                "Browse and Import Paleobase Entries")
        toolMenu.AppendSeparator()
        computation_plan_browser = toolMenu.Append(wx.ID_ANY, "Computation Plan Browser\tCtrl-7", 
                "Browse Existing Computation Plans and Create New Computation Plans")
        
        def bind_editor(name, edclass, menuitem):
            hid_name = ''.join(('_', name))
            def del_editor(event, *args, **kwargs):
                setattr(self, hid_name, None)
            
            def create_editor():
                editor = getattr(self, hid_name, None)
                if not editor:
                    editor = edclass(self)
                    self.Bind(wx.EVT_CLOSE, del_editor, editor)
                    setattr(self, hid_name, editor)
                return editor
            
            def raise_editor(event, *args, **kwargs):
                editor = create_editor()
                editor.Show()
                editor.Raise()
            self.Bind(wx.EVT_MENU, raise_editor, menuitem)
            
        bind_editor('attribute_editor', AttEditor, attEditor)
        bind_editor('view_editor', ViewEditor, viewEditor)
        bind_editor('milieu_browser', MilieuBrowser, collectionBrowser)
        bind_editor('template_editor', TemplateEditor, templateEditor)
        bind_editor('cplan_browser', ComputationPlanBrowser, computation_plan_browser)
        bind_editor('filter_editor', FilterEditor, filterEditor)
        bind_editor('group_editor', GroupEditor, groupEditor)
        
        self.menuBar.Append(fileMenu, "File")
        self.menuBar.Append(editMenu, "Edit")
        self.menuBar.Append(toolMenu, "Tools")

        self.SetMenuBar(self.menuBar)

    def OnMove(self, event):
        x, y = event.GetPosition()
        wx.Config.Get().Write("windows/samplebrowser/location", "(%d,%d)" % (x, y))

    def OnSize(self, event):
        width, height = event.GetSize()
        wx.Config.Get().Write("windows/samplebrowser/size", "(%d,%d)" % (width, height))
        self.Layout()

    def show_about(self, event):
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def quit(self, event):
        self.close_repository()
        wx.Exit()
        
    def change_repository(self, event):
        self.close_repository()
        
        #Close all other editors, as the repository is changing...
        for window in self.Children:
            if window.IsTopLevel():
                window.Close()
                
        self.open_repository()
        self.SetTitle(' '.join(('CScience:', datastore.data_source)))

    def open_repository(self, repo_dir=None):
        if not repo_dir:
            dialog = wx.DirDialog(None, "Choose a Repository", 
                style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
            if dialog.ShowModal() == wx.ID_OK:
                repo_dir = dialog.GetPath()
                dialog.Destroy()
            else:
                #end the app, if the user doesn't want to open a repo dir
                self.Close()
                return
        elif not os.path.exists(repo_dir):
            raise datastore.RepositoryException('Previously saved repository no longer exists.')
        
        try:
            datastore.set_data_source(repo_dir)
        except Exception as e:
            import traceback
            print repr(e)
            print traceback.format_exc()
            raise datastore.RepositoryException('Error while loading selected repository.')
        else:
            self.CreateVirtualSamples()
            self.CreateSampleBrowser()
            self.ConfigureFilter()
            self.ConfigureSort()
            self.ApplyFilter()
            self.FilterCalibrationSamples()
            self.ApplyTextSearchFilter()
            self.ApplySort()
            self.ConfigureGrid()


    def close_repository(self):
        if datastore.data_modified:
            if wx.MessageBox('You have modified this repository. '
                    'Would you like to save your changes?', "Unsaved Changes", 
                    wx.YES_NO | wx.ICON_EXCLAMATION) == wx.YES:
                self.save_repository(None)
        #just in case, for now
        datastore.data_modified = False
        
    def save_repository(self, event):
        datastore.save_datastore()

    def GetMenuBar(self):
        return self.menuBar
        
    def OnCopy(self, event):
        indexes = sorted(list(self.selected_rows))
        samples = [self.displayed_samples[index] for index in indexes]
        
        view_name = self.browser_view.get_view()
        view = datastore.views[view_name]        
        #views are guaranteed to give attributes as id, then computation_plan, then
        #remaining atts in order when iterated.
        
        result = os.linesep.join(['\t'.join([
                    datastore.sample_attributes.format_value(att, sample[att]) 
                    for att in view]) for sample in samples])
        result = os.linesep.join(['\t'.join(view), result])
        
        data = wx.TextDataObject()
        data.SetText(result)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        
    def CreateVirtualSamples(self):
        self.samples = []
        for sample in datastore.sample_db.itervalues():
            self.samples.extend([VirtualSample(sample, experiment) 
                                 for experiment in sample if experiment != 'input'])

    def CreateSampleBrowser(self):
        self.DestroyChildren()
        self.CreateStatusBar()
        
        view_names = [name for name in datastore.views]
        
        viewLabel = wx.StaticText(self, wx.ID_ANY, "View:")
        self.selectedView = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_view(), 
                                        choices=view_names, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        
        filterLabel = wx.StaticText(self, wx.ID_ANY, "Filter:")
        self.selectedFilter = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_filter(), 
                        choices=['<No Filter>'] + sorted(datastore.filters.keys()), 
                        style=wx.CB_DROPDOWN | wx.CB_READONLY)
        
        self.filterDescription = wx.StaticText(self, wx.ID_ANY, "No Filter Selected")
        self.includeCalSamplesBox = wx.CheckBox(self, -1, "Include Calibration Samples")
        
        rowOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowOneSizer.Add(viewLabel, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.selectedView, border=5, flag=wx.ALL)
        rowOneSizer.Add(filterLabel, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.selectedFilter, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.filterDescription, border=5, flag=wx.ALL)
        rowOneSizer.Add(self.includeCalSamplesBox, border=5, flag=wx.ALL)
        
        sortByLabel = wx.StaticText(self, wx.ID_ANY, "Sort by")
        self.primarySort = wx.ComboBox(self, wx.ID_ANY, value="Not Implemented", choices=["Not Implemented"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        andByLabel = wx.StaticText(self, wx.ID_ANY, "and then by")
        self.secondarySort = wx.ComboBox(self, wx.ID_ANY, value="Not Implemented", choices=["Not Implemented"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.sortDirection = wx.ComboBox(self, wx.ID_ANY, value=self.browser_view.get_direction(), choices=["Ascending", "Descending"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.plotSort = wx.Button(self, wx.ID_ANY, "Plot Sort Attributes...")
        
        rowTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowTwoSizer.Add(sortByLabel, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.primarySort, border=5, flag=wx.ALL)
        rowTwoSizer.Add(andByLabel, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.secondarySort, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.sortDirection, border=5, flag=wx.ALL)
        rowTwoSizer.Add(self.plotSort, border=5, flag=wx.ALL)

        searchLabel = wx.StaticText(self, wx.ID_ANY, "Search:")
        self.searchBox = wx.TextCtrl(self, wx.ID_ANY, size=(300, -1))
        self.exactBox = wx.CheckBox(self, -1, "Use Exact Match")
        
        rowThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowThreeSizer.Add(searchLabel, border=5, flag=wx.ALL)
        rowThreeSizer.Add(self.searchBox, border=5, flag=wx.ALL)
        rowThreeSizer.Add(self.exactBox, border=5, flag=wx.ALL)
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "The current view has no attributes defined for it.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "Invalid View")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
                
        self.importButton = wx.Button(self, wx.ID_ANY, "Import Samples...")
        self.applyExperiment = wx.Button(self, wx.ID_ANY, "Date Samples...")
        self.makeExperiment = wx.Button(self, wx.ID_ANY, "Make Experiment...")
        self.calvinButton = wx.Button(self, wx.ID_ANY, "Analyze Ages...")
        self.deleteSample = wx.Button(self, wx.ID_ANY, "Delete Sample...")
        self.stripExperiment = wx.Button(self, wx.ID_ANY, "Strip Experiment...")
        self.exportView = wx.Button(self, wx.ID_ANY, "Export Samples...")
        
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
        columnSizer.Add(rowOneSizer, border=2, flag=wx.ALL | wx.EXPAND)
        columnSizer.Add(rowTwoSizer, border=2, flag=wx.ALL | wx.EXPAND)
        columnSizer.Add(rowThreeSizer, border=2, flag=wx.ALL | wx.EXPAND)
        columnSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnSizer.Add(buttonSizer, border=2, flag=wx.ALL)
        
        self.SetTitle('CScience')
        
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
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSample, self.deleteSample)
        self.Bind(wx.EVT_BUTTON, self.OnStripExperiment, self.stripExperiment)
        self.Bind(wx.EVT_TEXT, self.OnTextSearchUpdate, self.searchBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnTextSearchUpdate, self.exactBox)
        
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.Bind(wx.EVT_BUTTON, self.OnRunCalvin, self.calvinButton)
        
        self.Bind(events.EVT_WORKFLOW_DONE, self.OnDatingDone)

    def ConfigureFilter(self):
        filter_name = self.browser_view.get_filter()
        if filter_name == "<No Filter>":
            self.filterDescription.SetLabel("No Filter Selected")
        else:
            the_filter = datastore.filters[filter_name]
            self.filterDescription.SetLabel(the_filter.description())
        
    def ApplyFilter(self):
        self.displayed_samples = None
        filter_name = self.browser_view.get_filter()
        if filter_name == "<No Filter>":
            self.filtered_samples = list(self.samples)
        else:
            the_filter = datastore.filters[filter_name]
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
        
        if value:
            view_name = self.browser_view.get_view()                
            samples = []
            
            if self.exactBox.IsChecked():
                samples_to_search = self.filtered_samples
            else:
                if self.displayed_samples is not None and len(value) > len(self.previous_query) and value.startswith(self.previous_query):
                    samples_to_search = self.displayed_samples
                else:
                    samples_to_search = self.filtered_samples
            
            for sample in samples_to_search:
                for att in datastore.views[view_name]:
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
        #TODO: this is a hackkkkk
        view_name = self.browser_view.get_view()
        try:
            view = datastore.views[view_name]
        except KeyError:
            self.browser_view.set_view('All')
            view = datastore.views['All']
            
        # previous_primary   = self.primarySort.GetStringSelection()
        # previous_secondary = self.secondarySort.GetStringSelection()

        previous_primary = self.browser_view.get_primary()
        previous_secondary = self.browser_view.get_secondary()
        
        self.primarySort.Clear()
        self.secondarySort.Clear()
        
        for att in view:
            self.primarySort.Append(att)
            self.secondarySort.Append(att)
            
        if previous_primary in view or previous_primary == 'computation_plan':
            self.primarySort.SetStringSelection(previous_primary)
        else:
            self.primarySort.SetStringSelection("id")
            self.browser_view.set_primary("id")
            
        if previous_secondary in view or previous_secondary == 'id':
            self.secondarySort.SetStringSelection(previous_secondary)
        else:
            self.secondarySort.SetStringSelection("computation_plan")
            self.browser_view.set_secondary("computation_plan")
        
    def ApplySort(self):
        # primarySort   = self.primarySort.GetStringSelection()
        # secondarySort = self.secondarySort.GetStringSelection()

        primarySort = self.browser_view.get_primary()
        secondarySort = self.browser_view.get_secondary()
        
        samples = []
        
        for sample in self.displayed_samples:
            samples.append((sample[primarySort], sample[secondarySort], sample))
            
        samples.sort(cmp=sort_none_last, reverse=self.GetSortDirection())
        self.displayed_samples = [item[2] for item in samples]
        
    def OnTextSearchUpdate(self, event):
        self.ApplyTextSearchFilter()
        self.ConfigureGrid()
        
    def OnExportView(self, event):
        
        view_name = self.browser_view.get_view()
        view = datastore.views[view_name]
        # add header labels -- need to use iterator to get computation_plan/id correct
        rows = [att for att in view]
        rows.extend([[sample[att] for att in view] for sample in self.displayed_samples])
        
        wildcard = "CSV Files (*.csv)|*.csv|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(self, message="Save view in ...", defaultDir=os.getcwd(), defaultFile="view.csv", wildcard=wildcard, style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
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
        view = datastore.views[view_name]
        
        #id isn't a column here
        numCols = len(view) - 1
        numRows = len(self.displayed_samples)

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
        for att in view:
            if att == 'id':
                continue
            att_value = att.replace(" ", "\n")
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
        
        for row, sample in enumerate(self.displayed_samples):
            for index, att in enumerate(view, -1):
                if att == 'id':
                    continue
                value = sample[att]
                #TODO: use formatting happiness...
                if isinstance(value, float):
                    self.grid.SetCellValue(row, index, "%.2f" % value)
                else:
                    self.grid.SetCellValue(row, index, str(value))
            
        self.grid.AutoSize()
        
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()

    def OnImportSamples(self, event):
        dialog = wx.FileDialog(None,
                "Select a CSV File containing Samples to be Imported or Updated:",
                style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        path = dialog.GetPath()
        dialog.Destroy()
        
        def show_error(message):
            wx.MessageBox(message, "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
        
        if result == wx.ID_OK:
            if not os.path.isfile(path):
                return show_error("Did not select a file.")
            input = open(path, "rU")
            header = input.readline().strip()
            if not header:
                return show_error("Selected file is empty.")
               
            fields = header.strip().split(',')
            fields = [field.strip("\"' ") for field in fields]
            required_atts = set(['id']) 
            missing = required_atts - set(fields)
            if missing:
                return show_error("CSV file is missing fields for required attributes: %s" 
                                  % ', '.join(missing))
            
            rows = []
            index = 0
            
            for index, line in enumerate(input, 1):
                values = line.strip().split(',')
                values = [field.strip("\"' ") for field in values]
                items = zip(fields, values)
                try:
                    mapping = dict([(field, datastore.sample_attributes.convert_value(field, value)) 
                                    for field, value in items])
                    rows.append(mapping)
                except ValueError:
                    print "Incorrect type for some data on row %i!" % index
            if not rows:
                return show_error("CSV file contains no data.")
            
            dialog = DisplayImportedSamples(self, os.path.basename(path), fields, rows)
            if dialog.ShowModal() == wx.ID_OK:
                if dialog.sample_set_name:
                    for item in rows:
                        item['sample set'] = dialog.sample_set_name
                if dialog.source_name:
                    for item in rows:
                        item['source'] = dialog.source_name
                if dialog.create_group:
                    group_name = rows[0]['sample set']
                    if group_name not in datastore.sample_groups:
                        new_group = Group(group_name)
                        for item in rows:
                            new_group.add(item['id'])
                        datastore.sample_groups.add(new_group)
                    else:
                        show_error(("Group name '%s' already exists. " % group_name) + 
                                   "Auto-creation of new group cancelled. " + 
                                   "Your samples will still be imported.")
                       
                imported_samples = []
                for item in rows:
                    s = Sample('input', item)
                    datastore.sample_db.add(s)
                    imported_samples.append(s['id'])
    
                dlg = wx.SingleChoiceDialog(self,
                                'The following samples were imported and/or updated:',
                                'Import Results', imported_samples, wx.OK | wx.CENTRE)
                dlg.ShowModal()
                dlg.Destroy()
                
                datastore.data_modified = True
                
                self.CreateVirtualSamples()
                self.ConfigureFilter()
                self.ConfigureSort()
                self.ApplyFilter()
                self.FilterCalibrationSamples()
                self.ApplyTextSearchFilter()
                self.ApplySort()
                self.ConfigureGrid()
            dialog.Destroy()

    def OnRunCalvin(self, event):
        """
        Runs Calvin on all highlighted samples, or all samples if none are
        highlighted.
        """
        
        if not self.selected_rows:
            samples = self.displayed_samples
        else:
            indexes = list(self.selected_rows)
            samples = [self.displayed_samples[index] for index in indexes]
        
        calvin.argue.analyzeSamples(samples)

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
        
        self.selectedView.Clear()
        for view in datastore.views:
            self.selectedView.Append(view)
        
        # if current view has been deleted, then switch to "All" view
        if view_name not in datastore.views:
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
        self.selectedFilter.SetItems(['<No Filter>'] + 
                            sorted(datastore.filters.keys()))

        # if current filter has been deleted, then switch to "None" filter
        if filter_name not in datastore.filters:
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

    def OnDating(self, event):

        dlg = ExperimentSelector(self, self.displayed_samples)
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.selected_experiment.GetStringSelection()
            current_samples = dlg.current_samples
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        computation_plan = datastore.computation_plans[selection]
        
        dialog = WorkflowProgress(self, "Applying Computation '%s'" % (computation_plan.name), 
                                  len(current_samples), 100000)
        dialog.Show()

        self.importButton.Disable()
        self.exportView.Disable()
        self.applyExperiment.Disable()
        self.calvinButton.Disable()
        self.plotSort.Disable()

        self.saturated = []

        t = RunDatingThread(self, dialog, computation_plan, current_samples)
        t.Start()

    def OnDatingDone(self, event):

        if self.saturated:
            dlg = wx.SingleChoiceDialog(self, "The following samples could not be processed by the computation_plan due to saturation:", "Saturated Samples", self.saturated, wx.OK | wx.CENTRE)
            dlg.ShowModal()
            dlg.Destroy()

            self.saturated = None
        
        datastore.data_modified = True
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

        self.stripExperiment.Disable()
        self.deleteSample.Disable()

        menuBar = self.GetMenuBar()
        editMenu = menuBar.GetMenu(menuBar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            self.stripExperiment.Enable()
            self.deleteSample.Enable()
            editMenu.Enable(wx.ID_COPY, True)
            
        if len(self.selected_rows) == 1:
            index = list(self.selected_rows)[0]
            sample = self.displayed_samples[index]
            if sample['production rate total'] > 0:
                self.depthItem.Enable(True)
            
        if len(self.selected_rows) == 2:
            first = sorted(list(self.selected_rows))[0]
            second = sorted(list(self.selected_rows))[1]
            
            first_sample = self.displayed_samples[first]
            second_sample = self.displayed_samples[second]
            
            if first_sample.nuclide != second_sample.nuclide:
                if first_sample.computation_plan != "input" and second_sample.computation_plan != "input":
                    self.bpItem.Enable(True)
            
    def OnStripExperiment(self, event):
        
        indexes = list(self.selected_rows)
        samples = [self.displayed_samples[index] for index in indexes]
        
        dialog = wx.MessageDialog(None, 'This operation will strip all performed computations from the selected samples. (Note: Input cannot be deleted.) Are you sure you want to do this?', "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
        if dialog.ShowModal() == wx.ID_YES:
            for sample in samples:
                for exp in sample.keys():
                    if exp != 'input':
                        del sample[exp]
        
            self.grid.ClearSelection()
            self.selected_rows = set()
            datastore.data_modified = True
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
        ids = [sample['id'] for sample in samples]
        
        for group in datastore.sample_groups.itervalues():
            ids = [s_id for s_id in ids if s_id not in group]
            
        if len(ids) == len(samples):
            explanation = ""
        else:
            explanation = ". Note: Some samples could not be deleted because they are members of groups."

        if ids:
            if len(samples) > 1:
                dialog = wx.MessageDialog(None, 'The selected samples are members of groups and cannot be deleted.', 'Cannot Delete Samples', wx.OK | wx.ICON_INFORMATION)
            else:
                dialog = wx.MessageDialog(None, 'The selected sample is a member of a group and cannot be deleted.', 'Cannot Delete Sample', wx.OK | wx.ICON_INFORMATION)                
            dialog.ShowModal()
        else:
            dialog = wx.MessageDialog(None, 'Are you sure that you want to delete the following samples: %s%s' % (ids, explanation), "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_YES:
                for s_id in ids:
                    del datastore.sample_db[s_id]
                self.grid.ClearSelection()
                self.selected_rows = set()
                datastore.data_modified = True
                self.CreateVirtualSamples()
                self.ConfigureFilter()
                self.ConfigureSort()
                self.ApplyFilter()
                self.FilterCalibrationSamples()
                self.ApplyTextSearchFilter()
                self.ApplySort()
                self.ConfigureGrid()
                
                
                
class DisplayImportedSamples(wx.Dialog):
    def __init__(self, parent, csv_file, fields, rows):
        super(DisplayImportedSamples, self).__init__(parent, wx.ID_ANY, 'Import Samples')
        
        self.csv_file = csv_file
        
        headingLabel = wx.StaticText(self, wx.ID_ANY, 
                    "The following samples are contained in %s:" % self.csv_file)
        questionLabel = wx.StaticText(self, wx.ID_ANY, 
                    "Do you want to import these samples as displayed?")
        
        grid = self.create_grid(fields, rows)
        
        #panel for adding a "sample set" attribute.
        create_set_panel = wx.Panel(self)
        self.add_set_check = wx.CheckBox(create_set_panel, wx.ID_ANY, 
                                    "Add 'sample set' attribute with value: ")
        self.set_name_input = wx.TextCtrl(create_set_panel, wx.ID_ANY, size=(250, -1))
        self.set_name_input.Enable(self.add_set_check.IsChecked())
        set_sizer = wx.BoxSizer(wx.HORIZONTAL)
        set_sizer.Add(self.add_set_check, border=5, flag=wx.ALL)
        set_sizer.Add(self.set_name_input, border=5, flag=wx.ALL)
        create_set_panel.SetSizer(set_sizer)
        self.Bind(wx.EVT_CHECKBOX, self.on_add_sample_set, self.add_set_check)
        self.Bind(wx.EVT_TEXT, self.on_sampleset_name, self.set_name_input)
            
        self.create_group_check = wx.CheckBox(self, -1, 
                    "Auto-Create group with 'sample set' name and these samples")
        self.create_group_check.Enable('sample set' in fields)

        #panel for adding a source, if one doesn't already exist
        source_panel = wx.Panel(self)
        self.add_source_check = wx.CheckBox(source_panel, wx.ID_ANY, 
                                    "Add 'source' attribute with value: ")
        self.source_name_input = wx.TextCtrl(source_panel, wx.ID_ANY, size=(250, -1),
                                    value=self.csv_file)
        self.source_name_input.Enable(self.add_source_check.IsChecked())
        source_sizer = wx.BoxSizer(wx.HORIZONTAL)
        source_sizer.Add(self.add_source_check, border=5, flag=wx.ALL)
        source_sizer.Add(self.source_name_input, border=5, flag=wx.ALL)
        source_panel.SetSizer(source_sizer)
        self.Bind(wx.EVT_CHECKBOX, self.on_add_source, self.add_source_check)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(headingLabel, border=5, flag=wx.ALL)
        sizer.Add(grid, border=5, flag=wx.ALL)
        sizer.Add(create_set_panel)
        sizer.Add(self.create_group_check, border=5, flag=wx.ALL)
        sizer.Add(source_panel)
        sizer.Add(questionLabel, border=5, flag=wx.ALL | wx.ALIGN_CENTER)
        sizer.Add(btnsizer, border=5, flag=wx.ALL | wx.ALIGN_CENTER)

        create_set_panel.Show('sample set' not in fields)
        source_panel.Show('source' not in fields)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Center(wx.BOTH)

    def on_add_sample_set(self, event):
        self.set_name_input.Enable(event.Checked())
        if not event.Checked():
            self.create_group_check.SetValue(False)
            self.create_group_check.Enable(False)
            self.set_name_input.SetValue('')

    def on_add_source(self, event):
        self.source_name_input.Enable(event.Checked())
        if not event.Checked():
            self.source_name_input.SetValue(self.csv_file)

    def on_sampleset_name(self, event):
        value = bool(self.set_name_input.GetValue())
        self.create_group_check.Enable(value)
        if not value:
            self.create_group_check.SetValue(False)

    def create_grid(self, fields, rows):
        grid = wx.grid.Grid(self, wx.ID_ANY, size=(640, 480))
        grid.CreateGrid(len(rows), len(fields))
        grid.EnableEditing(False)

        max_spaces = 0
        max_height = 0
        for index, att in enumerate(fields):
            #force word boundaries to act as new-lines (more or less)
            display = att.replace(' ', '\n')
            max_spaces = max(att.count(' '), max_spaces)
            max_height = max(grid.GetTextExtent(display)[1], max_height)
            grid.SetColLabelValue(index, display)            
        height = max_height * (max_spaces + 1) + 20
        grid.SetColLabelSize(height)

        # fill out grid with values
        for row_index, sample in enumerate(rows):
            for col_index, att in enumerate(fields):
                grid.SetCellValue(row_index, col_index, str(sample[att]))                
               
        grid.AutoSize()
        return grid
            
    @property
    def sample_set_name(self):
        return self.add_set_check.IsChecked() and self.set_name_input.GetValue()
    @property
    def source_name(self):
        return self.add_source_check.IsChecked() and self.source_name_input.GetValue()
    @property
    def create_group(self):
        return self.create_group_check.IsChecked()
    
    
class ExperimentSelector(wx.Dialog):

    def __init__(self, parent, samples):
        super(ExperimentSelector, self).__init__(parent, id=wx.ID_ANY, 
                                    title="Experiment/Sample Selector")

        self.samples = samples

        label1 = wx.StaticText(self, wx.ID_ANY, "Apply Experiment")
        label2 = wx.StaticText(self, wx.ID_ANY, "To Samples:")
        
        self.selected_experiment = wx.ComboBox(self, wx.ID_ANY, 
                value="<SELECT EXPERIMENT>", 
                choices=["<SELECT EXPERIMENT>"] + sorted(datastore.computation_plans.keys()), 
                style=wx.CB_DROPDOWN | wx.CB_READONLY)
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label1, border=5, flag=wx.ALL)
        row_sizer.Add(self.selected_experiment, border=5, flag=wx.ALL)

        self.ok_btn = wx.Button(self, wx.ID_OK)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer = wx.StdDialogButtonSizer()
        btnsizer.AddButton(self.ok_btn)
        btnsizer.AddButton(cancel_btn)
        btnsizer.Realize()
        self.ok_btn.Disable()

        self.base_ids = list(set([str(sample['id']) for sample in self.samples]))
        self.sample_list = wx.ListBox(self, wx.ID_ANY, choices=self.base_ids, 
                                  style=wx.LB_SINGLE | wx.LB_SORT)

        column_sizer = wx.BoxSizer(wx.VERTICAL)
        column_sizer.Add(row_sizer, border=5, flag=wx.ALL)
        column_sizer.Add(label2, border=5, flag=wx.ALL)
        column_sizer.Add(self.sample_list, proportion=1, border=5, flag=wx.ALL)
        column_sizer.Add(btnsizer, border=10, flag=wx.ALL)
        
        self.Bind(wx.EVT_COMBOBOX, self.experiment_selected, self.selected_experiment)
        #HACK -- we want a listbox that can scroll but can't have items selected
        #within; unselecting selected items instantly seems to be the only way
        #given by wx to do this :P
        self.Bind(wx.EVT_LISTBOX, self.unselect_list, self.sample_list)

        self.SetSizer(column_sizer)
        self.Layout()
        self.Center()
        
    def unselect_list(self, event):
        self.sample_list.DeselectAll()
        
    def experiment_selected(self, event):
        selected = self.selected_experiment.GetSelection()
        if selected == 0:
            self.sample_list.Set(self.base_ids)
            if self.base_ids:
                self.sample_list.SetFirstItem(0)
            self.ok_btn.Disable()
        else:
            experiment = self.selected_experiment.GetStringSelection()
            
            self.current_samples = []
            for vsample in self.samples:
                if experiment not in vsample.experiments():
                    vsample.computation_plan = experiment
                    self.current_samples.append(vsample)
                    
            self.ok_btn.Enable(bool(self.current_samples))
            ids = set([str(sample['id']) for sample in self.current_samples])
            self.sample_list.Set(list(ids))
            if ids > 0:
                self.sample_list.SetFirstItem(0)
                
                
class WorkflowProgress(wx.Dialog):
    def __init__(self, parent, title, num_samples, maxAge):
        super(WorkflowProgress, self).__init__(parent, wx.ID_ANY, title)
        
        self.bar = wx.Gauge(self, wx.ID_ANY, range=maxAge)
        self.progress = wx.StaticText(self, wx.ID_ANY, 
                        "%4d of %4d Samples Processed" % (0, num_samples))
        self.time = wx.StaticText(self, wx.ID_ANY, "Time Step: 0")
        self.num_samples = num_samples
        self.button = wx.Button(self, wx.ID_CANCEL)
        self.cancel = False
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bar, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self.progress, border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.time, border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.button, border=5, flag=wx.ALIGN_CENTER | wx.ALL)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()
        self.MakeModal(True)

        self.Bind(events.EVT_UPDATE_TIME, self.set_time)
        self.Bind(events.EVT_UPDATE_PROGRESS, self.set_progress)
        self.Bind(events.EVT_UPDATE_RANGE, self.set_range)
        self.Bind(events.EVT_UPDATE_SAMPLES, self.set_total_samples)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button)

    def set_time(self, evt):
        self.bar.SetValue(getattr(evt, 'progress', evt.time))
        self.time.SetLabel("Time Step: %d" % evt.time)
        self.Layout()
    
    def set_progress(self, evt):
        self.progress.SetLabel("%4d of %4d Samples Processed" % 
                               (evt.num_completed, self.num_samples))
        if evt.num_completed == self.num_samples:
            self.MakeModal(False)
            wx.FutureCall(2000, self.Close)
        self.Layout()
        
    def set_range(self, evt):
        self.bar.SetRange(evt.max_value)
        self.Layout()
        
    def set_total_samples(self, evt):
        self.num_samples = evt.num_samples
        self.progress.SetLabel("%4d of %4d Samples Processed" % (0, evt.num_samples))
        self.Layout()
        
    def on_cancel(self, event):
        self.cancel = True
        self.MakeModal(False)
        wx.FutureCall(1000, self.Close)


about_text = '''<html>
    <body bgcolor="white">
        <center>
            <h1>ACE: Age Calculation Environment</h1>
            <h2>Version 1.0</h2>
            <h3>http://ace.hwr.arizona.edu</h3>
            <table>
                <tr>
                    <th align="center" colspan="2">Contributors</th>
                </tr>
                <tr>
                    <td>Kenneth M. Anderson</td>
                    <td>Laura Rassbach</td>
                </tr>
                <tr>
                    <td>Elizabeth Bradley</td>
                    <td>Evan Sheehan</td>
                </tr>
                <tr>
                    <td>William Van Lepthien</td>
                    <td>Marek Zreda</td>
                </tr>
                <tr>
                    <td align="center" colspan="2">Chris Zweck</td>
                </td>
            </table>
            <p>This software is based upon work sponsored by the NSF under 
               Grant Number ATM-0325812 and Grant Number ATM-0325929.</p>
            <p>Copyright &copy; 2007-2009 University of Colorado. 
               All rights reserved.</p>
        </center>
    </body>
</html>'''

class AboutBox(wx.Dialog):
    
    def __init__(self, parent):
        super(AboutBox, self).__init__(parent, wx.ID_ANY, 'About ACE')

        html = wx.html.HtmlWindow(self)
        html.SetPage(about_text)
        link = wx.lib.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, "ACE Website", 
                                              URL="http://ace.hwr.arizona.edu")
        button = wx.Button(self, wx.ID_OK)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(link, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()




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

from cscience import datastore
from cscience.GUI import events
from cscience.GUI.Editors import AttEditor, MilieuBrowser, ComputationPlanBrowser, \
            FilterEditor, GroupEditor, TemplateEditor, ViewEditor, MemoryFrame
from cscience.GUI.Util import SampleBrowserView, Plot, grid
from cscience.framework import Group, Sample, VirtualSample

import calvin.argue

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

            self.browser.button_panel.Enable()
            self.browser.plot_sort.Enable()
            
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

class SampleGridTable(grid.UpdatingTable):
    def __init__(self, *args, **kwargs):
        self._samples = []
        #The samples shown get updated when the view is updated (since text
        #search is redone), so this doesn't need to be a property to re-draw.
        self.view = []
        super(SampleGridTable, self).__init__(*args, **kwargs)

    @property
    def samples(self):
        return self._samples
    @samples.setter
    def samples(self, value):
        self._samples = value
        self.reset_view()
        
    def GetNumberRows(self):
        return len(self.samples) or 1
    def GetNumberCols(self):
        return (len(self.view) or 2) - 1
    def GetValue(self, row, col):
        if not self.view:
            return "The current view has no attributes defined for it."
        elif not self.samples:
            return ''
        return str(self.samples[row][self.view[col+1]])
    def GetRowLabelValue(self, row):
        if not self.samples:
            return ''
        return self.samples[row]['id']
    def GetColLabelValue(self, col):
        if not self.view:
            return "Invalid View"
        return self.view[col+1].replace(' ', '\n')

class SampleBrowser(MemoryFrame):
    
    framename = 'samplebrowser'
    
    def __init__(self):
        super(SampleBrowser, self).__init__(parent=None, id=wx.ID_ANY, 
                                            title='CScience', size=(540, 380))
        
        self.browser_view = SampleBrowserView()        
        self.selected_rows = set()

        self.CreateStatusBar()
        self.create_menus()
        self.create_widgets()
        
        self.Bind(events.EVT_WORKFLOW_DONE, self.OnDatingDone)
        self.Bind(events.EVT_REPO_CHANGED, self.repo_changed)
        self.Bind(wx.EVT_CLOSE, self.quit)

    def create_menus(self):
        menu_bar = wx.MenuBar()

        #Build File menu
        #Note: on a mac, the 'Quit' option is moved for platform nativity automatically
        file_menu = wx.Menu()
        item = file_menu.Append(wx.ID_OPEN, "Switch Repository\tCtrl-O", 
                                     "Switch to a different CScience Repository")
        self.Bind(wx.EVT_MENU, self.change_repository, item)
        file_menu.AppendSeparator()
        item = file_menu.Append(wx.ID_SAVE, "Save Repository\tCtrl-S", 
                                   "Save changes to current CScience Repository")
        self.Bind(wx.EVT_MENU, self.save_repository, item)
        file_menu.AppendSeparator()
        item = file_menu.Append(wx.ID_EXIT, "Quit CScience\tCtrl-Q", 
                                   "Quit CScience")
        self.Bind(wx.EVT_MENU, self.quit, item)
        
        edit_menu = wx.Menu()
        item = edit_menu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected samples.")
        self.Bind(wx.EVT_MENU, self.OnCopy, item)
        
        tool_menu = wx.Menu()
        def bind_editor(name, edclass, menuname, tooltip):
            menuitem = tool_menu.Append(wx.ID_ANY, menuname, tooltip)
            hid_name = ''.join(('_', name))
            def del_editor(event, *args, **kwargs):
                setattr(self, hid_name, None)
            
            def create_editor():
                editor = getattr(self, hid_name, None)
                if not editor:
                    #TODO: fix this hack!
                    editor = getattr(edclass, edclass.__name__.rpartition('.')[2])(self)
                    self.Bind(wx.EVT_CLOSE, del_editor, editor)
                    setattr(self, hid_name, editor)
                return editor
            
            def raise_editor(event, *args, **kwargs):
                editor = create_editor()
                editor.Show()
                editor.Raise()
            self.Bind(wx.EVT_MENU, raise_editor, menuitem)
            return menuitem
        
        bind_editor('filter_editor', FilterEditor, "Filter Editor\tCtrl-1", 
                "Create and Edit CScience Filters for use in the Sample Browser")
        bind_editor('view_editor', ViewEditor, "View Editor\tCtrl-2", 
                "Edit the list of views that can filter the display of samples in CScience")
        tool_menu.AppendSeparator()
        bind_editor('attribute_editor', AttEditor, "Attribute Editor\tCtrl-3", 
                "Edit the list of attributes that can appear on samples in CScience")
        tool_menu.AppendSeparator()
        bind_editor('group_editor', GroupEditor, "Core Editor\tCtrl-4", 
                "Group and Collate Samples Belonging to Specific Cores")
        tool_menu.AppendSeparator()
        bind_editor('template_editor', TemplateEditor, "Template Editor\tCtrl-5", 
                "Edit the list of templates for the CScience Paleobase")
        bind_editor('milieu_browser', MilieuBrowser, "Milieu Browser\tCtrl-6", 
                "Browse and Import Paleobase Entries")
        tool_menu.AppendSeparator()
        bind_editor('cplan_browser', ComputationPlanBrowser, "Computation Plan Browser\tCtrl-7", 
                "Browse Existing Computation Plans and Create New Computation Plans")
         
        help_menu = wx.Menu()
        item = help_menu.Append(wx.ID_ABOUT, "About CScience", "View Credits")
        self.Bind(wx.EVT_MENU, self.show_about, item)
        
        #Disable save unless changes are made
        file_menu.Enable(wx.ID_SAVE, False)
        #Disable copy when no rows are selected
        edit_menu.Enable(wx.ID_COPY, False)
        
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(tool_menu, "&Tools")
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)
        
    def create_action_buttons(self):  
        self.button_panel = wx.Panel(self, wx.ID_ANY)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        imp_button = wx.Button(self.button_panel, wx.ID_ANY, "Import Samples...")
        self.Bind(wx.EVT_BUTTON, self.OnImportSamples, imp_button)
        button_sizer.Add(imp_button, border=5, flag=wx.ALL)
        
        calc_button = wx.Button(self.button_panel, wx.ID_APPLY, "Do Calculations...")
        self.Bind(wx.EVT_BUTTON, self.OnDating, calc_button)
        button_sizer.Add(calc_button, border=5, flag=wx.ALL)
        
        calv_button = wx.Button(self.button_panel, wx.ID_ANY, "Analyze Ages...")
        self.Bind(wx.EVT_BUTTON, self.OnRunCalvin, calv_button)
        button_sizer.Add(calv_button, border=5, flag=wx.ALL)
        
        self.del_button = wx.Button(self.button_panel, wx.ID_DELETE, "Delete Sample...")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSample, self.del_button)
        button_sizer.Add(self.del_button, border=5, flag=wx.ALL)
        self.del_button.Disable()
        
        self.strip_button = wx.Button(self.button_panel, wx.ID_ANY, "Strip Calculated Data...")
        self.Bind(wx.EVT_BUTTON, self.OnStripExperiment, self.strip_button)
        button_sizer.Add(self.strip_button, border=5, flag=wx.ALL)
        self.strip_button.Disable()
        
        exp_button = wx.Button(self.button_panel, wx.ID_ANY, "Export Samples...")
        self.Bind(wx.EVT_BUTTON, self.OnExportView, exp_button)
        button_sizer.Add(exp_button, border=5, flag=wx.ALL)
        
        self.button_panel.SetSizer(button_sizer)      
        return self.button_panel
        
    def create_widgets(self):
        #NOTE: we can stick these in a panel if needed to prevent them showing
        #up while asking to open the repository.
        self.selected_view = wx.ComboBox(self, wx.ID_ANY, choices=['All'],
                                         style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.selected_filter = wx.ComboBox(self, wx.ID_ANY, choices=['<No Filter>'],
                                           style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.filter_desc = wx.StaticText(self, wx.ID_ANY, "No Filter Selected")
        self.Bind(wx.EVT_COMBOBOX, self.OnViewSelect, self.selected_view)
        self.Bind(wx.EVT_COMBOBOX, self.OnFilterSelect, self.selected_filter)
        
        self.sselect_prim = wx.ComboBox(self, wx.ID_ANY, choices=["Not Sorted"], 
                                style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.sselect_sec = wx.ComboBox(self, wx.ID_ANY, choices=["Not Sorted"], 
                                style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.sdir_select = wx.ComboBox(self, wx.ID_ANY, 
                    value=self.browser_view.get_direction(), 
                    choices=["Ascending", "Descending"], 
                    style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.plot_sort = wx.Button(self, wx.ID_ANY, "Plot Sort Attributes...")
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeSort, self.sselect_prim)
        self.Bind(wx.EVT_COMBOBOX, self.OnChangeSort, self.sselect_sec)
        self.Bind(wx.EVT_COMBOBOX, self.OnSortDirection, self.sdir_select)
        self.Bind(wx.EVT_BUTTON, self.OnPlotSort, self.plot_sort)
        
        self.search_box = wx.TextCtrl(self, wx.ID_ANY, size=(300, -1))
        self.exact_box = wx.CheckBox(self, wx.ID_ANY, "Use Exact Match")
        self.Bind(wx.EVT_TEXT, self.OnTextSearchUpdate, self.search_box)
        self.Bind(wx.EVT_CHECKBOX, self.OnTextSearchUpdate, self.exact_box)
        
        self.grid = grid.LabelSizedGrid(self, wx.ID_ANY)
        self.table = SampleGridTable(self.grid)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.create_action_buttons()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, "View:"), border=5, flag=wx.ALL)
        row_sizer.Add(self.selected_view, border=5, flag=wx.ALL)
        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Filter:"), border=5, flag=wx.ALL)
        row_sizer.Add(self.selected_filter, border=5, flag=wx.ALL)
        row_sizer.Add(self.filter_desc, border=5, flag=wx.ALL)
        sizer.Add(row_sizer, flag=wx.EXPAND)
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Sort by"), border=5, flag=wx.ALL)
        row_sizer.Add(self.sselect_prim, border=5, flag=wx.ALL)
        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, "and then by"), border=5, flag=wx.ALL)
        row_sizer.Add(self.sselect_sec, border=5, flag=wx.ALL)
        row_sizer.Add(self.sdir_select, border=5, flag=wx.ALL)
        row_sizer.Add(self.plot_sort, border=5, flag=wx.ALL)
        sizer.Add(row_sizer, flag=wx.EXPAND)
        
        sizer.Add(self.grid, proportion=1, flag=wx.EXPAND)
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Search:"), border=5, flag=wx.ALL)
        row_sizer.Add(self.search_box, border=5, flag=wx.ALL)
        row_sizer.Add(self.exact_box, border=5, flag=wx.ALL)
        sizer.Add(row_sizer, flag=wx.EXPAND)
        
        sizer.Add(self.button_panel)
        self.SetSizer(sizer)

    def show_about(self, event):
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def quit(self, event):
        self.close_repository()
        wx.Exit()
        
    def repo_changed(self, event):
        """
        Used to cause the File->Save Repo menu option to be enabled only if
        there is new data to save.
        """
        self.GetMenuBar().Enable(wx.ID_SAVE, event.unsaved)
        
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
            self.selected_view.SetItems([v for v in datastore.views])
            self.selected_view.SetStringSelection(self.browser_view.get_view())
            
            self.selected_filter.SetItems(['<No Filter>'] + sorted(datastore.filters.keys()))
            self.selected_filter.SetStringSelection(self.browser_view.get_filter())
            
            self.show_new_samples()

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
            
    def show_new_samples(self):
        self.samples = []
        for sample in datastore.sample_db.itervalues():
            self.samples.extend([VirtualSample(sample, experiment) 
                                 for experiment in sample if experiment != 'input'])
        
        self.filter_samples()
        
    def filter_samples(self):
        self.displayed_samples = None
        filter_name = self.browser_view.get_filter()
        try:
            filt = datastore.filters[filter_name]
        except KeyError:
            self.browser_view.set_filter('<No Filter>')
            self.selected_filter.SetStringSelection('<No Filter>')
            self.filter_desc.SetLabel('No Filter Selected')
            filtered_samples = self.samples[:]
        else:
            self.filter_desc.SetLable(filt.description())
            filtered_samples = filter(filt.apply, self.samples)
        self.search_samples(filtered_samples)

    def search_samples(self, filtered_samples=[]):
        value = self.search_box.GetValue()
        
        if value:
            if not self.exact_box.IsChecked() and self.displayed_samples and \
               self.previous_query in value:
                samples_to_search = self.displayed_samples
            else:
                samples_to_search = filtered_samples
            
            self.previous_query = value
            view = datastore.views[self.browser_view.get_view()]
            self.displayed_samples = [s for s in samples_to_search if 
                                s.search(value, view, self.exact_box.IsChecked())]
        else:
            self.displayed_samples = filtered_samples
            self.previous_query = ''
        self.display_samples()
        
    def display_samples(self):        
        def sort_none_last(x, y):
            def cp_none(x, y):
                if x is None and y is None:
                    return 0
                elif x is None:
                    return 1
                elif y is None:
                    return -1
                else:
                    return cmp(x, y)
            for a, b in zip(x, y):
                val = cp_none(a, b)
                if val:
                    return val
            return 0
        
        self.displayed_samples.sort(cmp=sort_none_last, 
                            key=lambda s: (s[self.browser_view.get_primary()], 
                                           s[self.browser_view.get_secondary()]), 
                            reverse=self.GetSortDirection())
        
        self.table.view = datastore.views['All']#datastore.views[self.browser_view.get_view()]
        self.table.samples = self.displayed_samples
        #self.Layout() ?
        
    def OnTextSearchUpdate(self, event):
        self.search_samples()
        
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
                self.show_new_samples()
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
        self.browser_view.set_filter(self.selected_filter.GetStringSelection())
        self.filter_samples()
 
    def OnViewSelect(self, event):
        view_name = self.selected_view.GetStringSelection()
        try:
            view = datastore.views[view_name]
        except KeyError:
            view_name = 'All'
            view = datastore.views['All']
            self.selected_view.SetStringSelection('All')
        self.browser_view.set_view(view_name)
        
        self.sselect_prim.SetItems(view)
        self.sselect_sec.SetItems(view)

        previous_primary = self.browser_view.get_primary()
        previous_secondary = self.browser_view.get_secondary()
            
        if previous_primary in view:
            self.sselect_prim.SetStringSelection(previous_primary)
        else:
            self.sselect_prim.SetStringSelection("id")
            self.browser_view.set_primary("id")
            
        if previous_secondary in view:
            self.sselect_sec.SetStringSelection(previous_secondary)
        else:
            self.sselect_sec.SetStringSelection("computation_plan")
            self.browser_view.set_secondary("computation_plan")
        
        self.filter_samples()

    def GetSortDirection(self):
        # return true for descending, else return false
        # this corresponds to the expected value for the reverse parameter of the sort() method
        if self.browser_view.get_direction() == "Descending":
            return True
        return False

    def OnSortDirection(self, event):
        self.browser_view.set_direction(self.sdir_select.GetStringSelection())
        self.display_samples()

    def OnChangeSort(self, event):
        self.browser_view.set_primary(self.sselect_prim.GetStringSelection())
        self.browser_view.set_secondary(self.sselect_sec.GetStringSelection())
        self.display_samples()
        
    def UpdateViews(self):
        # get current view
        view_name = self.browser_view.get_view()
        # get list of views
        
        self.selected_view.Clear()
        for view in datastore.views:
            self.selected_view.Append(view)
        
        # if current view has been deleted, then switch to "All" view
        # fires an event for sample re-display, woo.
        if view_name not in datastore.views:
            self.selected_view.SetValue('All')
        else:
            self.selected_view.SetValue(view_name)

    def UpdateFilters(self):
        # get current filter
        filter_name = self.browser_view.get_filter()
        # get list of filters
        self.selected_filter.SetItems(['<No Filter>'] + 
                            sorted(datastore.filters.keys()))

        # if current filter has been deleted, then switch to "None" filter
        if filter_name not in datastore.filters:
            self.selected_filter.SetValue('<No Filter>')
        else:
            self.selected_filter.SetValue(filter_name)

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

        self.button_panel.Disable()
        self.plot_sort.Disable()
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
        self.show_new_samples()

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

        self.strip_button.Disable()
        self.del_button.Disable()

        menuBar = self.GetMenuBar()
        editMenu = menuBar.GetMenu(menuBar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            self.strip_button.Enable()
            self.del_button.Enable()
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
            self.show_new_samples()

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
                self.show_new_samples()
                
                
                
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




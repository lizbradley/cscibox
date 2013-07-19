"""
CoreBrowser.py

* Copyright (c) 2006-2015, University of Colorado.
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
import wx.lib.itemspicker
import wx.lib.delayedresult
from wx.lib.agw import aui
from wx.lib.agw import persist

import os
import csv
import quantities as pq

from cscience import datastore
from cscience.GUI import events, icons
from cscience.GUI.Editors import AttEditor, MilieuBrowser, ComputationPlanBrowser, \
            FilterEditor, TemplateEditor, ViewEditor
from cscience.GUI.Util import PlotWindow, grid
from cscience.framework import Core, Sample, UncertainQuantity

import calvin.argue
        

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
#         print('row',row,'col',col+1,'type',type(self.samples[row][self.view[col+1]]))
        return str(self.samples[row][self.view[col+1]])
    def GetRowLabelValue(self, row):
        if not self.samples:
            return ''
        return self.samples[row]['depth']
    def GetColLabelValue(self, col):
        if not self.view:
            return "Invalid View"
        return self.view[col+1].replace(' ', '\n')
    
class PersistBrowserHandler(persist.TLWHandler):
    
    def __init__(self, *args, **kwargs):
        super(PersistBrowserHandler, self).__init__(*args, **kwargs)
    
    def GetKind(self):
        return 'CoreBrowser'
    
    def Save(self):
        #save window settings
        super(PersistBrowserHandler, self).Save()
        browser, obj = self._window, self._pObject
        
        #save app data
        obj.SaveValue('repodir', datastore.data_source)
        obj.SaveValue('core_name', browser.core and browser.core.name)
        obj.SaveValue('view_name', browser.view and browser.view.name)
        obj.SaveValue('filter_name', browser.filter and browser.filter.name)
        obj.SaveValue('sorting_options', (browser.sort_primary, browser.sort_secondary,
                                          browser.sortdir_primary, browser.sortdir_secondary))
    
    def Restore(self):
        #restore window settings
        super(PersistBrowserHandler, self).Restore()
        browser, obj = self._window, self._pObject

        #restore app data
        repodir = obj.RestoreValue('repodir')
        browser.open_repository(repodir, False)  
        
        #we want the view, filter, etc to be set before the core is,
        #to reduce extra work.
        viewname = obj.RestoreValue('view_name')
        browser.set_view(viewname)
        
        filtername = obj.RestoreValue('filter_name')
        browser.set_filter(filtername)
        
        sorting = obj.RestoreValue('sorting_options')
        if sorting:
            ps, ss, pd, sd = sorting
            #TODO: get directions displaying properly...
            browser.set_psort(ps)
            browser.set_ssort(ss)
        
        corename = obj.RestoreValue('core_name')
        browser.select_core(corename=corename)
        browser.Show(True)
        

class CoreBrowser(wx.Frame):
    
    framename = 'samplebrowser'
    
    def __init__(self):
        super(CoreBrowser, self).__init__(parent=None, id=wx.ID_ANY, 
                                          title='CScience', size=(540, 380))
        
        #hide the frame until the initial repo is loaded, to prevent flicker.
        self.Show(False)
        self.SetName(self.framename)
        persist.PersistenceManager.Get().Register(self, PersistBrowserHandler)

        self.core = None
        self.view = None
        self.filter = None
        
        self.sort_primary = 'depth'
        self.sort_secondary = 'computation plan'
        self.sortdir_primary = False
        self.sortdir_secondary = False
        self.view_name = 'All'
        self.filter_name = 'None'
        
        self.samples = []
        self.displayed_samples = []
        
        self._mgr = aui.AuiManager(self, 
                    agwFlags=aui.AUI_MGR_DEFAULT & ~aui.AUI_MGR_ALLOW_FLOATING)
        self.SetMinSize(wx.Size(400, 300))

        self.CreateStatusBar()
        self.create_menus()
        self.create_widgets()
        
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        self.Bind(wx.EVT_CLOSE, self.quit)
        
    def GetKind(self):
        return 'CoreBrowser'

    def create_menus(self):
        menu_bar = wx.MenuBar()

        #Build File menu
        #Note: on a mac, the 'Quit' option is moved for platform nativity automatically
        file_menu = wx.Menu()
        
        item = file_menu.Append(wx.ID_ANY, "Import Samples",
                                "Import data from a csv file (Excel).")
        self.Bind(wx.EVT_MENU, self.import_samples,item)
        item = file_menu.Append(wx.ID_ANY, "Export Samples",
                                "Export currently displayed data to a csv file (Excel).")
        self.Bind(wx.EVT_MENU, self.OnExportView,item)
        file_menu.AppendSeparator()
        
        item = file_menu.Append(wx.ID_DELETE, "Delete Sample",
                                "Remove highlighted data entirely from the repository.")
        self.Bind(wx.EVT_MENU, self.OnDeleteSample,item)
        
        item = file_menu.Append(wx.ID_CLEAR, "Strip Calculated Data",
                                "Remove all calculated data from the highlighted samples (input data will remain).")
        self.Bind(wx.EVT_MENU,self.OnStripExperiment,item)
        file_menu.AppendSeparator()
        
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
        bind_editor('template_editor', TemplateEditor, "Template Editor\tCtrl-4", 
                "Edit the list of templates for the CScience Paleobase")
        bind_editor('milieu_browser', MilieuBrowser, "Milieu Browser\tCtrl-5", 
                "Browse and Import Paleobase Entries")
        tool_menu.AppendSeparator()
        bind_editor('cplan_browser', ComputationPlanBrowser, "Computation Plan Browser\tCtrl-6", 
                "Browse Existing Computation Plans and Create New Computation Plans")
         
        help_menu = wx.Menu()
        item = help_menu.Append(wx.ID_ABOUT, "About CScience", "View Credits")
        self.Bind(wx.EVT_MENU, self.show_about, item)
        
        #Disallow save unless there's something to save :)
        file_menu.Enable(wx.ID_SAVE, False)
        #Disable copy, delete, and clear-data when no rows are selected
        edit_menu.Enable(wx.ID_COPY, False)
        file_menu.Enable(wx.ID_DELETE, False)
        file_menu.Enable(wx.ID_CLEAR, False)
        
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(tool_menu, "&Tools")
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)
                
    def create_toolbar(self):
        #TODO: Get some more informative icons for toolbar buttons.
        self.toolbar = aui.AuiToolBar(self, wx.ID_ANY, 
                                      agwStyle=aui.AUI_TB_HORZ_TEXT |
                                      aui.AUI_TB_PLAIN_BACKGROUND)
        
        self.selected_core = wx.Choice(self.toolbar, id=wx.ID_ANY, 
                            choices=['No Core Selected'])
        self.toolbar.AddControl(self.selected_core)
        self.toolbar.AddSeparator()
        
        self.selected_view_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.selected_view_id, 'View Attributes', 
            wx.ArtProvider.GetBitmap(icons.ART_VIEW_ATTRIBUTES, wx.ART_TOOLBAR, (16, 16)))
        self.toolbar.SetToolDropDown(self.selected_view_id, True)
        self.selected_filter_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.selected_filter_id, 'Filter Samples', 
            wx.ArtProvider.GetBitmap(icons.ART_FILTER, wx.ART_TOOLBAR, (16, 16)))
        self.toolbar.SetToolDropDown(self.selected_filter_id, True)
        self.search_box = wx.SearchCtrl(self.toolbar, wx.ID_ANY, size=(150,-1), 
                                        style=wx.TE_PROCESS_ENTER)
        self.toolbar.AddSeparator()
        
        self.do_calcs_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.do_calcs_id,"", 
                                  wx.ArtProvider.GetBitmap(icons.ART_CALC, wx.ART_TOOLBAR, (16, 16)),
                                  short_help_string="Do Calculations")
        self.analyze_ages_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.analyze_ages_id, "",
                                   wx.ArtProvider.GetBitmap(icons.ART_ANALYZE_AGE, wx.ART_TOOLBAR, (16, 16)),
                                   short_help_string="Analyze Ages")
        self.plot_samples_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.plot_samples_id, '',
                                   wx.ArtProvider.GetBitmap(icons.ART_GRAPH, wx.ART_TOOLBAR, (16, 16)),
                                   short_help_string="Graph Data")
        self.toolbar.AddSeparator()
        
        self.toolbar.AddStretchSpacer()
        search_menu = wx.Menu()
        self.exact_box = search_menu.AppendCheckItem(wx.ID_ANY, 'Use Exact Match')
        self.search_box.SetMenu(search_menu)
        #TODO: bind cancel button to evt :)
        self.search_box.ShowCancelButton(True)
        self.toolbar.AddControl(self.search_box)
        
        def get_view_menu():
            menu = wx.Menu()
            #TODO: sorting? or not needed?
            for view in datastore.views.keys():
                item = menu.AppendRadioItem(wx.ID_ANY, view)
                if self.view and self.view.name == view:
                    item.Check()
            return menu, self.set_view
        def get_filter_menu():
            menu = wx.Menu()
            item = menu.AppendRadioItem(wx.ID_ANY, '<No Filter>')
            if not self.filter:
                item.Check()
            for filt in sorted(datastore.filters.keys()):
                item = menu.AppendRadioItem(wx.ID_ANY, filt)
                if self.filter and self.filter.name == filt:
                    item.Check()
            return menu, self.set_filter
        
        def tb_menu(menumaker):
            def on_popup(event):
                if (event.IsDropDownClicked() or 
                    (event.tool_id is self.selected_view_id) or 
                    (event.tool_id is self.selected_filter_id)):
                    self.toolbar.SetToolSticky(event.Id, True)
                    
                    menu, callback = menumaker()
                    def menu_pick(event):
                        item = menu.FindItemById(event.Id)
                        callback(item.Label)
                    menu.Bind(wx.EVT_MENU, menu_pick)
                    
                    rect = self.toolbar.GetToolRect(event.Id)
                    pt = self.toolbar.ClientToScreen(rect.GetBottomLeft())
                    pt = self.ScreenToClient(pt)
                    self.PopupMenu(menu, pt)
                    
                    self.toolbar.SetToolSticky(event.Id, False)
                    menu.Destroy()
            return on_popup
        
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, tb_menu(get_view_menu), 
                  id=self.selected_view_id)
        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, tb_menu(get_filter_menu), 
                  id=self.selected_filter_id)
        self.Bind(wx.EVT_TOOL, self.OnDating, id=self.do_calcs_id)
        self.Bind(wx.EVT_TOOL, self.OnRunCalvin, id=self.analyze_ages_id)
        self.Bind(wx.EVT_TOOL, self.do_plot, id=self.plot_samples_id)
        self.Bind(wx.EVT_CHOICE, self.select_core, self.selected_core)
        self.Bind(wx.EVT_TEXT, self.update_search, self.search_box)
        self.Bind(wx.EVT_MENU, self.update_search, self.exact_box)
        
        self.toolbar.Realize()
        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('btoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))
            
    def create_widgets(self):
        #TODO: save & load these values using the AUI stuff...        
        self.create_toolbar()
        
        self.grid = grid.LabelSizedGrid(self, wx.ID_ANY)
        self.table = SampleGridTable(self.grid)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.grid_statusbar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.grid_statusbar)
        self.grid_statusbar.SetFieldsCount(4)
        self.INFOPANE_SORT_FIELD = 0
        self.INFOPANE_COL_FILT_FIELD = 1
        self.INFOPANE_ROW_FILT_FIELD = 2
        self.INFOPANE_SEARCH_FIELD = 3
        self.grid_statusbar.SetStatusWidths([-1, -1, -1, -1])
        #TODO: Use unicode for fancy up and down arrows.
        self.grid_statusbar.SetStatusText("Sorting by " + self.sort_primary + (" (^)." if self.grid.IsSortOrderAscending() else " (v)."),self.INFOPANE_SORT_FIELD)
            
        def OnSortColumn(event):
            self.sort_secondary = self.sort_primary
            self.sortdir_secondary = self.sortdir_primary
            self.sortdir_primary = self.grid.IsSortOrderAscending()
            self.sort_primary = self.view[self.grid.GetSortingColumn()+1]
            self.grid_statusbar.SetStatusText("Sorting by " + self.sort_primary + (" (^)." if self.grid.IsSortOrderAscending() else " (v)."),self.INFOPANE_SORT_FIELD)
            self.display_samples()

        self.grid.Bind(wx.grid.EVT_GRID_COL_SORT, OnSortColumn)
        
        self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Name('thegrid').CenterPane())
        self._mgr.Update()

    def show_about(self, event):
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def quit(self, event):
        persist.PersistenceManager.Get().SaveAndUnregister(self)
        self.close_repository()
        wx.Exit()
        
    def on_repository_altered(self, event):
        """
        Used to cause the File->Save Repo menu option to be enabled only if
        there is new data to save.
        """
        if 'views' in event.changed:
            view_name = self.view.name
            if view_name not in datastore.views:
                # if current view has been deleted, then switch to "All" view
                self.set_view('All')
            elif event.value and view_name == event.value:
                #if the current view has been updated, display new data as
                #appropriate
                self.set_view(view_name)
        elif 'filters' in event.changed:
            if self.filter:
                filter_name = self.filter.name
                # if current filter has been deleted, then switch to "None" filter
                if filter_name not in datastore.filters:
                    self.set_filter(None)
                elif event.value and filter_name == event.value:
                        #if we changed the currently selected filter, we should
                        #re-filter the current view.
                    self.set_filter(filter_name)
        else:
            #TODO: select new core on import, & stuff.
            self.refresh_samples()
        print 'got event!'
        datastore.data_modified = True
        self.GetMenuBar().Enable(wx.ID_SAVE, True)
        event.Skip()
        
    def change_repository(self, event):
        self.close_repository()
        
        #Close all other editors, as the repository is changing...
        for window in self.Children:
            if window.IsTopLevel():
                window.Close()
                
        self.open_repository()
        self.SetTitle(' '.join(('CScience:', datastore.data_source)))

    def open_repository(self, repo_dir=None, manual=True):
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
            self.selected_core.SetItems(sorted(datastore.cores.keys()) or
                                        ['No Cores -- Import Samples to Begin'])
            self.selected_core.SetSelection(0)
            if manual:
                self.select_core()
                self.Raise()

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
        samples = [self.displayed_samples[index] for index in self.grid.SelectedRowset]
        view = self.view     
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

    def refresh_samples(self):
        self.samples = []
        if self.core is not None:
            for vc in self.core.virtualize():
                self.samples.extend(vc)
        self.filter_samples()
        
    def filter_samples(self):
        self.displayed_samples = None
        if self.filter:
            filtered_samples = filter(self.filter.apply, self.samples)
        else:
            filtered_samples = self.samples[:]
        self.search_samples(filtered_samples)

    def search_samples(self, samples_to_search=[]):
        value = self.search_box.GetValue()
        if value:
            self.previous_query = value
            self.displayed_samples = [s for s in samples_to_search if 
                                s.search(value, self.view, self.exact_box.IsChecked())]
        else:
            self.displayed_samples = samples_to_search
            self.previous_query = ''
        self.display_samples()
        
    def display_samples(self):     
        def reversing_sorter(*directions):
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
                for a, b, d in zip(x, y, directions):
                    val = cp_none(a, b)
                    if val:
                        return val * (-1 if d else 1)
                return 0
            return sort_none_last
        
        self.displayed_samples.sort(cmp=reversing_sorter(self.sortdir_primary, 
                                                         self.sortdir_secondary), 
                            key=lambda s: (s[self.sort_primary], 
                                           s[self.sort_secondary]))
        self.table.view = self.view
        self.table.samples = self.displayed_samples
        
    def update_search(self, event):
        value = self.search_box.GetValue()
        if value and not self.exact_box.IsChecked() and \
           self.displayed_samples and self.previous_query in value:
            self.search_samples(self.displayed_samples)
        else:
            #unless all of the above is true, we may have previously-excluded
            #samples showing up in the search result. Since this is possible,
            #we need to start from the filtered set again, not the displayed set.
            #TODO: can keep a self.filtered_samples around 
            #to save a little work here.
            self.filter_samples()
        if (value):
            self.grid_statusbar.SetStatusText("Searched with parameters: " + self.search_box.GetValue(),self.INFOPANE_SEARCH_FIELD)
        else:
            self.grid_statusbar.SetStatusText("",self.INFOPANE_SEARCH_FIELD)
        
    def OnExportView(self, event):
        # add header labels -- need to use iterator to get computation_plan/id correct
        rows = [att for att in self.view]
        rows.extend([[sample[att] for att in self.view] 
                     for sample in self.displayed_samples])
        
        wildcard = "CSV Files (*.csv)|*.csv|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(self, message="Save view in ...", defaultDir=os.getcwd(), defaultFile="view.csv", wildcard=wildcard, style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()        
            tmp = open(path, "wb")
            writer = csv.writer(tmp)
            writer.writerows(rows)
        
            tmp.flush()
            tmp.close()
            
            the_dir = os.path.dirname(path)
            os.chdir(the_dir)
            
        dlg.Destroy()

    def do_plot(self, event):
        if(len(self.displayed_samples)>0):
            pw = PlotWindow(self, self.displayed_samples)
            pw.Show()
            pw.Raise()
        else:
            wx.MessageBox("Nothing to plot.", "Operation Cancelled", 
                                  wx.OK | wx.ICON_INFORMATION)
        
    def import_samples(self, event):
        dialog = wx.FileDialog(None,
                "Please select a CSV File containing Samples to be Imported or Updated:",
                defaultDir=os.getcwd(), wildcard="CSV Files (*.csv)|*.csv|All Files|*.*",
                style=wx.OPEN | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        path = dialog.GetPath()
        #destroy the dialog now so no problems happen on early return
        dialog.Destroy()
        
        if result == wx.ID_OK:
            with open(path, 'rU') as input_file:
                #allow whatever sane csv formats we can manage, here
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(input_file.read(1024))
                dialect.skipinitialspace = True
                input_file.seek(0)
                
                reader = csv.DictReader(input_file, dialect=dialect)
                if not reader.fieldnames:
                    wx.MessageBox("Selected file is empty.", "Operation Cancelled", 
                                  wx.OK | wx.ICON_INFORMATION)
                    return
                #strip extra spaces, since that was apparently a problem before?
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                   
                if 'depth' not in reader.fieldnames:
                    wx.MessageBox("Selected file is missing the required attribute 'depth'.", 
                                  "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                    return
                
                rows = []
                for index, line in enumerate(reader, 1):
                    #do appropriate type conversions...
                    for key, value in line.iteritems():
                        '''
                        TODO: Right now the try/catch block below produces a useless error if there's a column label 
                        (attribute) in the CSV that hasn't been added in the attribute editor. What this error really
                        means is that the program doesn't know what type of data the column is. So we could either
                        assume it's a string or, better yet, ask the user.
                        '''
                        
                        '''
                        TODO: move the error parsing stuff to here, so that all Sample's __init__ has to do
                        is copy the dictionary again. Probably by making sample_attributes.convert_value return a Quantity if appropriate.
                        '''
                        try:
                            line[key] = datastore.sample_attributes.convert_value(key, value)
                        except ValueError:
                            wx.MessageBox("%s on row %i has an incorrect type."
                                "Please update the csv file and try again." % (key, index),
                                "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                            return
                        except KeyError:
                            wx.MessageBox("%s not found in the attribute editor."% (key))
                            return
                        
                    rows.append(line)
                if not rows:
                    wx.MessageBox("Selected file appears to contain no data.", 
                                  "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                    return
                
                dialog = DisplayImportedSamples(self, os.path.basename(path), 
                                                reader.fieldnames, rows)
                if dialog.ShowModal() == wx.ID_OK:
                    if dialog.source_name:
                        for item in rows:
                            item['source'] = dialog.source_name
                    cname = dialog.core_name
                    core = datastore.cores.get(cname, None)
                    if core is None:
                        core = Core(cname)               
                        datastore.cores[cname] = core            
                    for item in rows:
                        '''
                        Start Hack
                        Long term, we should have some kind of intelligent, user
                        specified way to associate one column of uncertainty
                        with another column in the csv. For know, your column
                        header for uncertainty must have the same name, but with 
                        ' Error' added at the end.
                        '''
                        #Convert the raw list of label/values to a 
                        #list of label/quantities with uncertainties parsed.
                        used_keys = set()
                        parsed_dict = {}
                        for key in item:
                            find_val = key.find('Error')
                            if find_val > 0:
                                assoc_key = key[0:find_val].rstrip()
                                unit = datastore.sample_attributes.get_unit(assoc_key)
                                parsed_dict[assoc_key] = UncertainQuantity(
                                                            item[assoc_key],
                                                            unit,
                                                            item[key])
                                used_keys = used_keys | set((key, assoc_key))
                        for key in item:
                            if key not in used_keys:
                                unit = datastore.sample_attributes.get_unit(key)
                                parsed_dict[key] = pq.Quantity(item[key], unit)
                        '''
                        End Hack
                        '''
                        s = Sample('input', parsed_dict)
                        core.add(s)
        
                    wx.MessageBox('Core %s imported/updated' % cname, "Import Results",
                                  wx.OK | wx.CENTRE)
                    events.post_change(self, 'samples')
                    self.selected_core.SetItems(sorted(datastore.cores.keys()))
                    self.select_core()
                dialog.Destroy()

    def OnRunCalvin(self, event):
        """
        Runs Calvin on all highlighted samples, or all samples if none are
        highlighted.
        """
        
        if not self.grid.SelectedRowset:
            samples = self.displayed_samples
        else:
            indexes = list(self.grid.SelectedRowset)
            samples = [self.displayed_samples[index] for index in indexes]
        
        calvin.argue.analyzeSamples(samples)
        
    def select_core(self, event=None, corename=None):
        #ensure the selector shows the right core
        if not event and not self.selected_core.SetStringSelection(unicode(corename)):
            self.selected_core.SetSelection(0)
        try:
            self.core = datastore.cores[self.selected_core.GetStringSelection()]
        except KeyError:
            self.core = None
        self.refresh_samples()

    def set_filter(self, filter_name):
        try:
            self.filter = datastore.filters[filter_name]
        except KeyError:
            self.filter = None
            self.grid_statusbar.SetStatusText("",self.INFOPANE_ROW_FILT_FIELD)
        else:
            self.grid_statusbar.SetStatusText("Using " + str(filter_name) + " filter for rows.",self.INFOPANE_ROW_FILT_FIELD)
        self.filter_samples()
 
    def set_view(self, view_name):
        try:
            self.view = datastore.views[view_name]
        except KeyError:
            view_name = 'All'
            self.grid_statusbar.SetStatusText("",self.INFOPANE_COL_FILT_FIELD)
            self.view = datastore.views['All']
        else:
            if(view_name != 'All'):
                self.grid_statusbar.SetStatusText("Using " + view_name + " filter for columns.",self.INFOPANE_COL_FILT_FIELD)
        previous_primary = self.sort_primary
        previous_secondary = self.sort_secondary
            
        if previous_primary not in self.view:
            self.sort_primary = 'depth'
            
        if previous_secondary not in self.view:
            self.sort_secondary = 'computation plan'        
            
        self.filter_samples()
        
    def set_psort(self, sort_name):
        #TODO: Needs to tell the grid what the sorting column is.
        self.toolbar.Realize()
        self.sort_primary = sort_name
        self.display_samples()
        
    def set_ssort(self, sort_name):
        #TODO: Needs to tell the grid what the sorting column is.
        self.toolbar.Realize()
        self.sort_secondary = sort_name
        self.display_samples()
        
    def OnDating(self, event):
        dlg = ComputationDialog(self, self.core)
        ret = dlg.ShowModal()
        plan = dlg.plan
        # depths = dlg.depths
        dlg.Destroy()
        if ret != wx.ID_OK:
            return
        computation_plan = datastore.computation_plans[plan]
        workflow = datastore.workflows[computation_plan['workflow']]
        vcore = self.core.new_computation(plan)
        aborting = wx.lib.delayedresult.AbortEvent()
        
        #self.plotbutton.Disable()
        
        dialog = WorkflowProgress(self, "Applying Computation '%s'" % plan)
        wx.lib.delayedresult.startWorker(self.OnDatingDone, workflow.execute, 
                                  wargs=(computation_plan, vcore, aborting),
                                  cargs=(plan, self.core, dialog))
        if dialog.ShowModal() != wx.ID_OK:
            aborting.set()
            self.core.strip_experiment(plan)
        dialog.Destroy()

    def OnDatingDone(self, dresult, planname, core, dialog):
        try:
            result = dresult.get()
        except Exception as exc:
            core.strip_experiment(planname)
            print exc
            import traceback
            print traceback.format_exc()
            wx.MessageBox("There was an error running the requested computation."
                          " Please contact support.")
        else:
            dialog.EndModal(wx.ID_OK)
            print 'posting event!!'
            events.post_change(self, 'samples')
        finally:
            pass
            #self.plotbutton.Enable()
        
    def OnStripExperiment(self, event):
        
        indexes = list(self.grid.SelectedRowset)
        samples = [self.displayed_samples[index] for index in indexes]
        
        dialog = wx.MessageDialog(None, 'This operation will strip all performed computations from the selected samples. (Note: Input cannot be deleted.) Are you sure you want to do this?', "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
        if dialog.ShowModal() == wx.ID_YES:
            for sample in samples:
                for exp in sample.keys():
                    if exp != 'input':
                        del sample[exp]
        
            self.grid.ClearSelection()
            events.post_change(self, 'samples')

    def OnDeleteSample(self, event):
        
        indexes = self.grid.SelectedRowset
        samples = [self.displayed_samples[index] for index in indexes]
        ids = [sample['id'] for sample in samples]
        
        dialog = wx.MessageDialog(None, 'Are you sure that you want to delete the following samples: %s' % (ids), "Are you sure?", wx.YES_NO | wx.ICON_EXCLAMATION)
        if dialog.ShowModal() == wx.ID_YES:
            for s_id in ids:
                del self.core[depth]
            self.grid.ClearSelection()
            events.post_change(self, 'samples')                
                
                
class DisplayImportedSamples(wx.Dialog):
    class CorePanel(wx.Panel):
        def __init__(self, parent, default_name=''):
            super(DisplayImportedSamples.CorePanel, self).__init__(parent, 
                                    style=wx.TAB_TRAVERSAL | wx.BORDER_SIMPLE)
            
            self.new_core = wx.RadioButton(self, wx.ID_ANY, 'Create new core', 
                                       style=wx.RB_GROUP)
            self.existing_core = wx.RadioButton(self, wx.ID_ANY, 'Add to existing core')
            
            self.new_panel = wx.Panel(self, size=(300, -1))
            self.core_name = wx.TextCtrl(self.new_panel, wx.ID_ANY, default_name)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self.new_panel, wx.ID_ANY, 'Core Name:'),
                        border=5, flag=wx.ALL)
            sz.Add(self.core_name, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
            self.new_panel.SetSizer(sz)
            
            self.exis_panel = wx.Panel(self, size=(300, -1))
            cores = datastore.cores.keys()
            if not cores:
                self.existing_core.Disable()
            else:
                self.core_select = wx.ComboBox(self.exis_panel, wx.ID_ANY, cores[0],
                                               choices=cores,
                                               style=wx.CB_READONLY)
                sz = wx.BoxSizer(wx.HORIZONTAL)
                sz.Add(wx.StaticText(self.exis_panel, wx.ID_ANY, 'Select Core:'),
                        border=5, flag=wx.ALL)
                sz.Add(self.core_select, border=5, proportion=1, 
                       flag=wx.ALL | wx.EXPAND)
                self.exis_panel.SetSizer(sz)
            
            rsizer = wx.BoxSizer(wx.HORIZONTAL)
            rsizer.Add(self.new_core, border=5, flag=wx.ALL)
            rsizer.Add(self.existing_core, border=5, flag=wx.ALL)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(rsizer, flag=wx.EXPAND)
            sizer.Add(self.new_panel, border=5, flag=wx.ALL)
            sizer.Add(self.exis_panel, border=5, flag=wx.ALL)
            self.SetSizer(sizer)
            
            self.Bind(wx.EVT_RADIOBUTTON, self.on_coretype, self.new_core)
            self.Bind(wx.EVT_RADIOBUTTON, self.on_coretype, self.existing_core)
            self.exis_panel.Hide()
            self.new_core.SetValue(True)
            
        def on_coretype(self, event):
            self.new_panel.Show(self.new_core.GetValue())
            self.exis_panel.Show(self.existing_core.GetValue())
            self.Layout()
            
        #TODO: add validation!
        @property
        def name(self):
            if self.existing_core.GetValue():
                return self.core_select.GetValue()
            else:
                return self.core_name.GetValue()
    
    def __init__(self, parent, csv_file, fields, rows):
        super(DisplayImportedSamples, self).__init__(parent, wx.ID_ANY, 'Import Samples')
        
        #remove file extension
        name = csv_file.rsplit('.', 1)[0]
        grid = self.create_grid(fields, rows)
        
        self.core_panel = DisplayImportedSamples.CorePanel(self, name)
        #panel for adding a source, if one doesn't already exist
        source_panel = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SIMPLE)
        self.add_source_check = wx.CheckBox(source_panel, wx.ID_ANY, 
                                    "Add 'source' attribute with value: ")
        self.source_name_input = wx.TextCtrl(source_panel, wx.ID_ANY, size=(250, -1),
                                    value=name)
        self.source_name_input.Enable(self.add_source_check.IsChecked())
        source_sizer = wx.BoxSizer(wx.HORIZONTAL)
        source_sizer.Add(self.add_source_check, border=5, flag=wx.ALL)
        source_sizer.Add(self.source_name_input, border=5, flag=wx.ALL)
        source_panel.SetSizer(source_sizer)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                    "The following samples are contained in %s:" % csv_file),
                  border=5, flag=wx.ALL)
        sizer.Add(grid, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self.core_panel, border=5, flag=wx.ALL)
        sizer.Add(source_panel, border=5, flag=wx.ALL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                    "Do you want to import these samples as displayed?"), 
                  border=5, flag=wx.ALL | wx.ALIGN_CENTER)
        sizer.Add(btnsizer, border=5, flag=wx.ALL | wx.ALIGN_CENTER)

        source_panel.Show('source' not in fields)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Center(wx.BOTH)

    def create_grid(self, fields, rows):
        g = grid.LabelSizedGrid(self, wx.ID_ANY)
        g.CreateGrid(len(rows), len(fields))
        g.EnableEditing(False)
        for index, att in enumerate(fields):
            g.SetColLabelValue(index, att.replace(' ', '\n'))            
        
        # fill out grid with values
        for row_index, sample in enumerate(rows):
            g.SetRowLabelValue(row_index, str(sample['depth']))
            for col_index, att in enumerate(fields):
                g.SetCellValue(row_index, col_index, str(sample[att]))                
               
        g.AutoSize()
        return g
    
    @property
    def core_name(self):
        return self.core_panel.name
    @property
    def source_name(self):
        return (self.add_source_check.IsChecked() and 
                self.source_name_input.GetValue())
    
    
class ComputationDialog(wx.Dialog):

    def __init__(self, parent, core):
        super(ComputationDialog, self).__init__(parent, id=wx.ID_ANY, 
                                    title="Run Computations")

        self.core = core
        #TODO: exclude plans already run on this core...
        self.planchoice = wx.Choice(self, wx.ID_ANY, 
                choices=["<SELECT PLAN>"] + 
                         sorted(datastore.computation_plans.keys()))
        #TODO: sorting is a bit ew atm, see what I can do?
        self.alldepths = [str(d) for d in sorted(self.core.keys())]
        #TODO: do we want to allow exclusion on computation plans, or not really?
        #self.depthpicker = wx.lib.itemspicker.ItemsPicker(self, wx.ID_ANY,
        #        choices=self.alldepths, 
        #        label='At Depths:', selectedLabel='Exclude Depths:',
        #        ipStyle=wx.lib.itemspicker.IP_REMOVE_FROM_CHOICES)
        #self.depthpicker.add_button_label = "- Exclude ->"
        #self.depthpicker.remove_button_label = "<- Include -"
        
        bsz = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        
        sizer = wx.GridBagSizer(10, 10)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Apply Plan"), (0, 0))
        sizer.Add(self.planchoice, (0, 1), flag=wx.EXPAND)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'To Core "%s"' % self.core.name), 
                  (1, 0), (1, 2))
        #sizer.Add(self.depthpicker, (2, 0), (1, 2), flag=wx.EXPAND)
        sizer.Add(bsz, (3, 1), flag=wx.ALIGN_RIGHT)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)
        self.Center()
        
        self.okbtn = self.FindWindowById(self.AffirmativeId)
        self.okbtn.Disable()
        self.Bind(wx.EVT_CHOICE, self.plan_selected, self.planchoice)

    def plan_selected(self, event):
        self.okbtn.Enable(bool(self.planchoice.GetSelection()))
        
    @property
    def plan(self):
        return self.planchoice.GetStringSelection()
    
    @property
    def depths(self):
        #TODO: fix this if some samples can be excluded...
        return self.alldepths
                
class WorkflowProgress(wx.Dialog):
    def __init__(self, parent, title):
        super(WorkflowProgress, self).__init__(parent, wx.ID_ANY, title)
        
        #TODO: make this a real progress bar...
        self.bar = wx.Gauge(self, wx.ID_ANY)
        button = wx.Button(self, wx.ID_CANCEL, 'Abort')
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bar, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(button, border=5, flag=wx.ALIGN_CENTER | wx.ALL)
        
        self.SetSizer(sizer)

        self.Bind(events.EVT_WORKFLOW_DONE, self.on_finish)
        self.Bind(wx.EVT_TIMER, lambda evt: self.bar.Pulse())
        self.timer = wx.Timer(self)
        self.timer.Start(100)

    def Destroy(self):
        self.timer.Stop()
        return super(WorkflowProgress, self).Destroy()

    def on_finish(self, event):
        self.EndModal(wx.ID_OK)


class AboutBox(wx.Dialog):
    
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
    
    def __init__(self, parent):
        super(AboutBox, self).__init__(parent, wx.ID_ANY, 'About ACE')

        html = wx.html.HtmlWindow(self)
        html.SetPage(AboutBox.about_text)
        link = wx.lib.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, "ACE Website", 
                                              URL="http://ace.hwr.arizona.edu")
        button = wx.Button(self, wx.ID_OK)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(link, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()




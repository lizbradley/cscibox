"""
CoreBrowser.py

* All rights reserved.
* Redistribution and use in source and binary forms, with or without
*
* modification, are permitted provided that the following conditions are met:
* Copyright (c) 2006-2015, University of Colorado.
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
import quantities as pq
import time

import wx
import sys
import traceback
import pymongo
import pymongo.errors
import wx.wizard
import wx.grid
import wx.lib.itemspicker
import wx.lib.dialogs
# import wx.lib.delayedresult # TODO fix multi-threading bug

from wx.lib.agw import aui
from wx.lib.agw import persist
import wx.lib.agw.hypertreelist as htreelist
try:
    from agw import customtreectrl as ctreectrl
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as ctreectrl

from cscience import datastore
from cscience.GUI import events, icons, io
from cscience.GUI.Editors import AttEditor, MilieuBrowser, ComputationPlanBrowser, \
            TemplateEditor, ViewEditor
from cscience.GUI import grid, graph

from cscience.framework import datastructures

import calvin.argue

datastore = datastore.Datastore()


#TODO: get it so this table can be loaded without pulling all the data from the db!
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
        col_name = self.view[col+1]
        if col_name == 'run':
            #special display case for run: show the user-defined display
            #name instead of the internal name
            run = datastore.runs[self.samples[row]['run']]
            return run.display_name
        try:
            return datastore.sample_attributes.display_value(col_name, 
                                             self.samples[row][col_name])
        except AttributeError:
            return unicode(self.samples[row][col_name])
    def GetRowLabelValue(self, row):
        if not self.samples:
            return ''
        return self.samples[row]['depth']
    def GetColLabelValue(self, col):
        if not self.view:
            return "Invalid View"
        try:
            unit_str = datastore.sample_attributes[self.view[col+1]].unit
        except KeyError:
            unit_str = ''
        col_lab = self.view[col+1].replace(' ', '\n')
        if unit_str != '' and unit_str != 'dimensionless':
            return ('%s\n(%s)'%(col_lab, unit_str))
        else:
            return col_lab

class PersistBrowserHandler(persist.TLWHandler):

    #TODO: runs here

    def __init__(self, *args, **kwargs):
        super(PersistBrowserHandler, self).__init__(*args, **kwargs)

    def GetKind(self):
        return 'CoreBrowser'

    def Save(self):
        #save window settings
        super(PersistBrowserHandler, self).Save()
        browser, obj = self._window, self._pObject

        #save app data
        obj.SaveValue('core_name', browser.core and browser.core.name)
        obj.SaveValue('view_name', browser.view and browser.view.name)
        obj.SaveValue('sorting_options', (browser.sort_primary, browser.sort_secondary,
                                          browser.sortdir_primary, browser.sortdir_secondary))

    def Restore(self):
        #restore window settings
        super(PersistBrowserHandler, self).Restore()
        browser, obj = self._window, self._pObject

        if sys.platform.startswith('win'):
            wx.MessageBox("This is a standalone application, there is no installation necessary. "
                          "All the data files are stored in your home directory, in the folder 'cscibox'.",
                          "Windows Information")

        #restore app data
        try:
            browser.open_repository()
        except datastore.RepositoryException as exc:
            # need to CallAfter or something to handle the splash screen, here?
            wx.MessageBox("Could not open the repository specified in the config file.\n"
                          "Please confirm that your database is online and correctly "
                          "specified in config.py, then restart CScience",
                          "Repository Error")
            wx.SafeYield(None, True)
            browser.Close()
            return False

        #we want the view, run, etc to be set before the core is,
        #to reduce extra work.
        try:
            viewname = obj.RestoreValue('view_name')
        except SyntaxError:
            # The 'RestoreValue' method should return false if it's unable to find the value.
            #For some reason it's throwing a syntax Error. This emulates the expected behavior.
            viewname = False

        try:
            browser.set_view(viewname)
        except KeyError:
            browser.set_view('All')

        sorting = obj.RestoreValue('sorting_options')
        if sorting:
            ps, ss, pd, sd = sorting
            #TODO: get directions displaying properly...
            browser.set_psort(ps)
            browser.set_ssort(ss)

        try:
            corename = obj.RestoreValue('core_name')
        except SyntaxError:
            #TODO: figure out how a bad corename got stored.
            corename = ""
        browser.Show(True)
        wx.CallAfter(browser.select_core, corename=corename)



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
        self.model = None

        self.sort_primary = 'depth'
        self.sort_secondary = 'run'
        self.sortdir_primary = False
        self.sortdir_secondary = False
        self.view_name = 'All'

        self.samples = []
        self.displayed_samples = []

        try:
            self.connection = pymongo.MongoClient("localhost", 27017)['repository']
        except pymongo.errors.ConnectionFailure as e:
            print "Mongo Connection Failed.  Is mongod running?"
            self.Close()

        self._mgr = aui.AuiManager(self,
                    agwFlags=aui.AUI_MGR_DEFAULT & ~aui.AUI_MGR_ALLOW_FLOATING)
        self.SetMinSize(wx.Size(400, 300))

        self.CreateStatusBar()
        self.create_menus()
        self.create_widgets()

        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        self.Bind(wx.EVT_CLOSE, self.quit)

    @property
    def SelectedSamples(self):
        return [self.samples[idx] for idx in self.grid.SelectedRows]

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

        item = file_menu.Append(wx.ID_ANY, "Import LiPD",
                                "Import data from the LiPD format (select the json file).")
        self.Bind(wx.EVT_MENU, self.import_LiPD,item)

        item = file_menu.Append(wx.ID_ANY, "Export Samples",
                                "Export currently displayed data to a csv file (Excel).")
        self.Bind(wx.EVT_MENU, self.export_samples_csv,item)

        item = file_menu.Append(wx.ID_ANY, "Export LiPD",
                                "Export currently displayed data to LiPD format.")
        self.Bind(wx.EVT_MENU, self.export_samples_LiPD,item)

        item = file_menu.Append(wx.ID_ANY, "Delete Core",
                                "Delete currently displayed data from database.")
        self.Bind(wx.EVT_MENU, self.delete_samples,item)

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

        bind_editor('view_editor', ViewEditor, "View Editor\tCtrl-1",
                "Edit the list of views that restrict columns shown in the grid below")
        bind_editor('attribute_editor', AttEditor, "Attribute Editor\tCtrl-2",
                "Edit the list of columns that can ever appear in the grid below")
        tool_menu.AppendSeparator()
        bind_editor('template_editor', TemplateEditor, "Template Editor\tCtrl-3",
                "Edit the list of templates for the CScience Paleobase")
        bind_editor('milieu_browser', MilieuBrowser, "Supporting Data Sets\tCtrl-4",
                "Browse and Import Paleobase Entries")
        tool_menu.AppendSeparator()
        bind_editor('cplan_browser', ComputationPlanBrowser, "Computation Plan Browser\tCtrl-5",
                "Browse Existing Computation Plans and Create New Computation Plans")

        help_menu = wx.Menu()
        item = help_menu.Append(wx.ID_ABOUT, "About CScience", "View Credits")
        self.Bind(wx.EVT_MENU, self.show_about, item)

        #Disallow save unless there's something to save :)
        file_menu.Enable(wx.ID_SAVE, False)
        #Disable copy, delete, and clear-data when no rows are selected
        edit_menu.Enable(wx.ID_COPY, False)

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
        self.search_box = wx.SearchCtrl(self.toolbar, wx.ID_ANY, size=(150,-1),
                                        style=wx.TE_PROCESS_ENTER)
        self.toolbar.AddSeparator()

        self.do_calcs_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.do_calcs_id,"Computations",
                                  wx.ArtProvider.GetBitmap(icons.ART_CALC, wx.ART_TOOLBAR, (16, 16)),
                                  short_help_string="Do Calculations")
        #self.analyze_ages_id = wx.NewId()
        #self.toolbar.AddSimpleTool(self.analyze_ages_id, "",
        #                           wx.ArtProvider.GetBitmap(icons.ART_ANALYZE_AGE, wx.ART_TOOLBAR, (16, 16)),
        #                           short_help_string="Analyze Ages")
        self.plot_samples_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.plot_samples_id, 'Plotting',
                                   wx.ArtProvider.GetBitmap(icons.ART_GRAPH, wx.ART_TOOLBAR, (16, 16)),
                                   short_help_string="Graph Data")

        self.toolbar.AddStretchSpacer()
        search_menu = wx.Menu()
        self.exact_box = search_menu.AppendCheckItem(wx.ID_ANY, 'Use Exact Match')
        self.search_box.SetMenu(search_menu)
        #TODO: bind cancel button to evt :)
        self.search_box.ShowCancelButton(True)
        self.toolbar.AddControl(self.search_box)


        def popup_views(event):
            if (event.IsDropDownClicked() or
                (event.tool_id is self.selected_view_id)):
                self.toolbar.SetToolSticky(event.Id, True)

                menu = wx.Menu()
                #TODO: sorting? or not needed?
                for view in datastore.views.keys():
                    item = menu.AppendRadioItem(wx.ID_ANY, view)
                    if self.view and self.view.name == view:
                        item.Check()
                def menu_pick(event):
                    item = menu.FindItemById(event.Id)
                    self.set_view(item.Label)
                menu.Bind(wx.EVT_MENU, menu_pick)

                rect = self.toolbar.GetToolRect(event.Id)
                pt = self.toolbar.ClientToScreen(rect.GetBottomLeft())
                pt = self.ScreenToClient(pt)
                self.PopupMenu(menu, pt)

                self.toolbar.SetToolSticky(event.Id, False)
                menu.Destroy()

        self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, popup_views,
                  id=self.selected_view_id)
        self.Bind(wx.EVT_TOOL, self.OnDating, id=self.do_calcs_id)
        #self.Bind(wx.EVT_TOOL, self.OnRunCalvin, id=self.analyze_ages_id)
        self.Bind(wx.EVT_TOOL, self.do_plot, id=self.plot_samples_id)
        self.Bind(wx.EVT_CHOICE, self.select_core, self.selected_core)
        self.Bind(wx.EVT_TEXT, self.update_search, self.search_box)
        self.Bind(wx.EVT_MENU, self.update_search, self.exact_box)

        self.toolbar.Realize()
        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('btoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))

    def build_grid(self):
        self.grid = grid.LabelSizedGrid(self, wx.ID_ANY, corner_label='Depth')

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
        self.grid_statusbar.SetStatusText("Sorting by " + self.sort_primary + (" (^)." if
                            self.grid.IsSortOrderAscending() else " (v)."),self.INFOPANE_SORT_FIELD)


        '''The c++ code that really runs wx checks if a sorting column is not wx.NOT_FOUND before
        setting a sorting indicator or changing the sort order. Since the index of our depth column is -1
        and so is wx.NOT_FOUND, there's no way to set the grid's sort order. Thus, the hack below with
        the optional 'ascend' parameter.'''
        def OnSortColumn(event, ascend=None):
            if type(ascend) is bool:
                new_sort_dir = ascend
            else:
                new_sort_dir = self.grid.IsSortOrderAscending()

            new_sort_primary = self.view[self.grid.GetSortingColumn()+1]
            if self.sort_primary != new_sort_primary:
                self.sort_secondary = self.sort_primary
                self.sortdir_secondary = self.sortdir_primary
            self.sort_primary = new_sort_primary
            self.grid.sort_dir = new_sort_dir
            self.sortdir_primary = new_sort_dir

            self.grid_statusbar.SetStatusText("Sorting by " + self.sort_primary + (" (v)." if
                                        new_sort_dir else " (^)."),self.INFOPANE_SORT_FIELD)
            self.display_samples()

        def OnLabelLeftClick(event):
            '''Since the top left corner (the top of the depth column) doesn'get
            sorting events, I'm reproducing what EVT_GRID_COL_SORT does on the other columns,
            setting the sorting column and order as appropriate and then manually calling OnSortColumn'''
            if event.GetRow() == -1 and event.GetCol() == -1:
                if self.grid.IsSortingBy(event.GetCol()):
                    ascend = not self.sortdir_primary
                else:
                    ascend = True
                self.grid.SetSortingColumn(event.GetCol(), ascending=ascend)
                OnSortColumn(event, ascend=ascend)
            else:
                event.Skip()

        self.grid.Bind(wx.grid.EVT_GRID_COL_SORT, OnSortColumn)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, OnLabelLeftClick)

        self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Name('thegrid').CenterPane())

    def build_right_splitter(self):
        splitter = wx.SplitterWindow(self)
        #panel = wx.Panel(splitter, style=wx.RAISED_BORDER)
        self.htreelist = htreelist.HyperTreeList(splitter, size=(300,300), style=wx.RAISED_BORDER)

        self.htreelist.AddColumn("Core/Run")
        self.htreelist.AddColumn("Attribute")
        self.htreelist.AddColumn("Value")

        self.runlist = ctreectrl.CustomTreeCtrl(splitter, size=(300,300),
                style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.RAISED_BORDER)
        self.runlist.AddRoot('Runs')

        def right_click_run(evt):
            evt.Skip()
            evt_item = evt.GetItem()
            run = self.runlist.GetPyData(evt_item)

            if run:
                renameid = wx.NewId()
                rerunid = wx.NewId()
                menu = wx.Menu()
                menu.Append(rerunid, "Rerun with different parameters")
                menu.Append(renameid, "Rename")
                #menu.Append(RUNS_PANEL_DELETE_ID, "Delete")

                def edit_item(evt):
                    self.runlist.EditLabel(evt_item)

                def rerun_item(evt):
                    print 'go rerun go', run

                wx.EVT_MENU(menu, rerunid, rerun_item)
                wx.EVT_MENU(menu, renameid, edit_item)
                #wx.EVT_MENU(menu, RUNS_PANEL_DELETE_ID, self.on_delete_item)

                self.runlist.PopupMenu(menu, evt.GetPoint())
                menu.Destroy()

        def on_edit_end(evt):
            if not evt.IsEditCancelled():
                item = self.runlist.GetPyData(evt.GetItem())
                item.user_name = evt.GetLabel()
                events.post_change(self, 'runs', item.name)


        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, right_click_run)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, on_edit_end)
        self.Bind(ctreectrl.EVT_TREE_ITEM_CHECKED, self.show_by_runs)
        #self.Bind(wx.EVT_TREE_DELETE_ITEM, self.on_delete_item)

        splitter.SplitHorizontally(self.runlist, self.htreelist, 200)
        try:
            splitter.SetSashInvisible(False)
        except AttributeError:
            pass

        splitter.Fit()
        pane = self._mgr.AddPane(splitter, aui.AuiPaneInfo().
                         Name("MDNotebook").Right().Layer(1).Position(1).
                         MinimizeButton(False).CloseButton(False))


    def create_widgets(self):
        self.create_toolbar()
        self.build_grid()
        self.build_right_splitter()

        self._mgr.Update()

    def OnLabelRightClick(self, click_event):

        if click_event.GetRow() == -1: #Make sure this is a column label
            menu = wx.Menu()
            ids = {}
            att = self.view[click_event.GetCol()+1]
            old_unit = datastore.sample_attributes.get_unit(att)
            def OnColumnMenuSelect(menu_event):
                new_unit = ids[menu_event.GetId()]
                for sample in self.samples:
                    sample[att].units = new_unit
                self.display_samples()

            for unit in datastructures.get_conv_units(old_unit):
                id = wx.NewId()
                ids[id] = unit
                menu.Append(id, unit)
                wx.EVT_MENU( menu, id, OnColumnMenuSelect)
            self.grid.PopupMenu(menu, click_event.GetPosition())
            menu.Destroy()

    def show_about(self, event):
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()

    def quit(self, event):
        persist.PersistenceManager.Get().SaveAndUnregister(self)
        quit = self.close_repository()
        if quit == wx.YES or quit == wx.NO:
            wx.Exit()

    def on_repository_altered(self, event):
        """
        Used to cause the File->Save Repo menu option to be enabled only if
        there is new data to save.
        Also handles various widget updates on app-wide changes
        """

        if 'runs' in event.changed:
            self.update_runs()
            self.table.reset_view()
        elif 'view' in event.changed:
            view_name = self.view.name
            if view_name not in datastore.views:
                # if current view has been deleted, then switch to "All" view
                self.set_view('All')
            elif event.value and view_name == event.value:
                #if the current view has been updated, display new data as
                #appropriate
                self.set_view(view_name)
        elif event.GetEventObject() != self:
            self.refresh_samples()
        datastore.data_modified = True
        self.GetMenuBar().Enable(wx.ID_SAVE, True)
        event.Skip()

    def open_repository(self):
        try:
            datastore.load_from_config()
        except Exception as exc:
            import traceback
            print repr(exc)
            print traceback.format_exc()

            raise datastore.RepositoryException()
        else:
            self.selected_core.SetItems(sorted(datastore.cores.keys()) or
                                        ['No Cores -- Import Samples to Begin'])
            self.selected_core.SetSelection(0)

    def close_repository(self):
        if datastore.data_modified:
            close = wx.MessageBox('You have modified this repository. '
                'Would you like to save your changes?', "Unsaved Changes",
                wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION | wx.NO_DEFAULT)
            if close == wx.YES:
                self.save_repository()
            return close
        return wx.YES

    def save_repository(self, event=None):
        try:
            datastore.save_datastore()
        except Exception as exc:
            msg = "We're sorry, something went wrong trying to save the repository. " +\
                  "Please copy the text below, then close and re-open CScience. Your repository " +\
                  "will be reverted to its previous saved state. \n\n\n\n\n\n\n******DEBUG******\n\n" + \
                  traceback.format_exc()
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Saving Error")
            dlg.ShowModal()
            #get rid of nag, if it was going to come up
            datastore.data_modified = False


    def OnCopy(self, event):
        samples = [self.displayed_samples[index] for index in self.grid.SelectedRows]
        view = self.view
        #views are guaranteed to give attributes as id, then run, then
        #remaining atts in order when iterated.
        result = os.linesep.join(['\t'.join([
                    datastore.sample_attributes.display_value(att, sample[att])
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
        self.show_by_runs()

    def show_by_runs(self, evt=None):
        self.displayed_samples = None
        selected_runs = [self.runlist.GetPyData(item).name for item in
                         self.runlist.GetRootItem().GetChildren() if
                         self.runlist.IsItemChecked(item)]
        if not selected_runs:
            # if none are selected, default to all.
            sample_set = self.samples[:]
        else:
            sample_set = [sam for sam in self.samples if sam.run in selected_runs]
        self.search_samples(sample_set)

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
        self.update_metadata()

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
            self.show_by_runs()
        if (value):
            self.grid_statusbar.SetStatusText("Searched with parameters: " +
                        self.search_box.GetValue(),self.INFOPANE_SEARCH_FIELD)
        else:
            self.grid_statusbar.SetStatusText("",self.INFOPANE_SEARCH_FIELD)

    def update_runs(self):
        selected = [self.runlist.GetPyData(item).name for item in
                    self.runlist.GetRootItem().GetChildren() if
                    self.runlist.IsItemChecked(item)]
        self.runlist.DeleteAllItems()
        newroot = self.runlist.AddRoot('Runs')

        if not self.core:
            self.runlist.AppendItem(newroot, 'Select a Core to see its Runs')
            return

        runset = [datastore.runs[run] for run in self.core.vruns]
        if not runset:
            self.runlist.AppendItem(newroot, 'No Runs Exist for This Core')
            return

        runset.sort(key=lambda run: run.created_time, reverse=True)
        selected = filter(lambda run: run in runset, selected)

        for run in runset:
            run_id = self.runlist.AppendItem(newroot, run.display_name, ct_type=1)
            self.runlist.SetPyData(run_id, run)
            self.runlist.AppendItem(run_id, 'Computation Plan "%s"' % run.computation_plan)
            self.runlist.AppendItem(run_id, 'Run at: %s' % run.str_time)
            if run.rundata:
                paramid = self.runlist.AppendItem(run_id, 'Parameters')
                for param in sorted(run.rundata.keys()):
                    self.runlist.AppendItem(paramid, '%s given as: %s' % (str(param), str(run.rundata[param])))
            #TODO: run parameters here.
            if not selected or run.name in selected:
                #CheckItem2 avoids sending item-check events
                self.runlist.CheckItem2(run_id)
            #have to expand as we go so we get just the items at the level we want
            self.runlist.Expand(run_id)
        self.runlist.Expand(newroot)

    def update_metadata(self):
        # update metada for display
        if not self.core:
            return

        self.htreelist.DeleteAllItems()
        root = self.htreelist.AddRoot(self.core.name)

        # only display data for currently visible computation plans
        displayedRuns = set([i.run for i in self.displayed_samples])
        
        def showval(parent, name, val):
            attribute = self.htreelist.AppendItem(parent, '')
            self.htreelist.SetPyData(attribute, None)
            self.htreelist.SetItemText(attribute, name, 1)
            self.htreelist.SetItemText(attribute, 
                        datastore.core_attributes.display_value(name, val), 2)

        for run, values in self.core.properties.iteritems():
            if run not in displayedRuns:
                continue
            parent = self.htreelist.AppendItem(root, datastore.runs[run].display_name)
            if values.get('Required Citations', None):
                showval(parent, 'Required Citations', values['Required Citations'])
            for attname, value in values.iteritems():
                #TODO: do we want to force iteration order on core attributes as
                #it is on sample attributes so this doesn't have to happen here?
                if attname == 'Required Citations':
                    continue
                showval(parent, attname, value)

        self.htreelist.ExpandAll()


    def do_plot(self, event):
        if self.displayed_samples:
            pw = graph.PlotWindow(self, self.displayed_samples, self.view)
            pw.Show()
            pw.Raise()
        else:
            wx.MessageBox("Nothing to plot.", "Operation Cancelled",
                                  wx.OK | wx.ICON_INFORMATION)


    def import_samples(self, event):
        importwizard = io.ImportWizard(self)
        if importwizard.RunWizard():
            events.post_change(self, 'samples')
            self.selected_core.SetItems(sorted(datastore.cores.keys()))
            if importwizard.swapcore:
                self.grid_statusbar.SetStatusText("",self.INFOPANE_ROW_FILT_FIELD)
                self.set_view('All')
                self.select_core(corename=importwizard.corename)
            else:
                self.selected_core.SetStringSelection(self.core.name)
            if importwizard.saverepo:
                self.save_repository()

        importwizard.Destroy()

    def import_LiPD(self,event):
        importwizard = io.ImportWizard(self,True)
        if importwizard.RunWizard(True):
            events.post_change(self, 'samples')
            self.selected_core.SetItems(sorted(datastore.cores.keys()))
            if importwizard.swapcore:
                self.grid_statusbar.SetStatusText("",self.INFOPANE_ROW_FILT_FIELD)
                self.set_view('All')
                self.select_core(corename=importwizard.corename)
            else:
                self.selected_core.SetStringSelection(self.core.name)
            if importwizard.saverepo:
                self.save_repository()

        importwizard.Destroy()

    def export_samples_csv(self, event):
        return io.export_samples(self.displayed_samples)

    def export_samples_LiPD(self, event):
        wx.MessageBox('LiPD Export Not Yet Implemented.  Check back soon!')
        return io.export_samples(self.view, self.displayed_samples, self.model, LiPD = True)

    def delete_samples(self, event):
        if len(self.selected_core.GetItems())==1:
            for key in self.selected_core.GetItems():
                if key=='No Cores -- Import Samples to Begin':
                    wx.MessageBox('No cores to delete.', 'Delete Core', wx.OK | wx.ICON_INFORMATION)
                else:
                    dlg = DeleteCore(self)

                    ret = dlg.ShowModal()
                    dlg.Destroy()
                    if ret==wx.ID_OK:
                        self.selected_core.Delete(self.selected_core.GetSelection())
                        if len(self.selected_core.GetItems())==0:
                            self.selected_core.SetItems(['No Cores -- Import Samples to Begin'])

                        datastore.cores.delete_core(self.core)
                        self.select_core()
        else:
            dlg = DeleteCore(self)

            ret = dlg.ShowModal()
            dlg.Destroy()
            if ret==wx.ID_OK:
                self.selected_core.Delete(self.selected_core.GetSelection())
                if len(self.selected_core.GetItems())==0:
                    self.selected_core.SetItems(['No Cores -- Import Samples to Begin'])

                datastore.cores.delete_core(self.core)
                self.select_core()

    def OnRunCalvin(self, event):
        """
        Runs Calvin on all highlighted samples, or all samples if none are
        highlighted.
        """
        samples = self.displayed_samples

        """if not self.grid.SelectedRows:
            samples = self.displayed_samples
        else:
            indexes = list(self.grid.SelectedRows)
            samples = [self.displayed_samples[index] for index in indexes]"""

        calvin.argue.analyze_samples(samples)

    def select_core(self, event=None, corename=None):
        #ensure the selector shows the right core
        if not event and not self.selected_core.SetStringSelection(unicode(corename)):
            self.selected_core.SetSelection(0)
        try:
            self.core = datastore.cores[self.selected_core.GetStringSelection()]
            self.core.force_load()
        except KeyError:
            self.core = None
        self.update_runs()
        self.refresh_samples()

    def set_view(self, view_name):
        try:
            self.view = datastore.views[view_name]
        except KeyError:
            view_name = 'All'
            self.grid_statusbar.SetStatusText("",self.INFOPANE_COL_FILT_FIELD)
            self.view = datastore.views['All']
        else:
            if(view_name != 'All'):
                self.grid_statusbar.SetStatusText("Using " + view_name + " view for columns.",self.INFOPANE_COL_FILT_FIELD)
            else:
                self.grid_statusbar.SetStatusText("Showing all columns.",self.INFOPANE_COL_FILT_FIELD)
        previous_primary = self.sort_primary
        previous_secondary = self.sort_secondary

        if previous_primary not in self.view:
            self.sort_primary = 'depth'

        if previous_secondary not in self.view:
            self.sort_secondary = 'run'

        self.show_by_runs()

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

    def OnDating(self, event=None):
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
        self.SetCursor(wx.HOURGLASS_CURSOR)
        computation_progress = wx.ProgressDialog("Computation Progress", "info", maximum = 10,
                parent=self, style = 0
                    | wx.PD_APP_MODAL
                    | wx.PD_CAN_ABORT
                    #| wx.PD_CAN_SKIP
                    #| wx.PD_ELAPSED_TIME
                    | wx.PD_ESTIMATED_TIME
                    | wx.PD_REMAINING_TIME
                    | wx.PD_AUTO_HIDE)

        #TODO: as workflows become more interactive, it becomes less and less
        #sensible to perform all computation (possibly any computation) in its
        #own thread, as we'll be continuing to demand user attention throughout

        #leaving in some way to abort would be useful, so we should consider
        #how to do that; the issue is that wxpython leaks memory when you try
        #to construct windows in a new thread, which is yuck. So all of this
        #should be reconsidered in light of interactive-type workflows.

        #see http://stackoverflow.com/questions/13654559/how-to-thread-wxpython-progress-bar
        #for some further information
        #wx.lib.delayedresult.startWorker(self.OnDatingDone, workflow.execute,
        #                          cargs=(plan, dialog),
        #                          wargs=(computation_plan, vcore, aborting))

        try:
            workflow.execute(computation_plan, vcore, computation_progress)
        except:
            msg = "We're sorry, something went wrong while running that computation. " +\
                  "Please tell someone appropriate!\n\n\n\n\n\n\n******DEBUG******\n\n" + \
                  traceback.format_exc()
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Computation Error")
            dlg.ShowModal()
            raise
        else:
            (keepGoing, skip) = computation_progress.Update(10, "Computation finished successfully. ")
            computation_progress.Destroy()
            datastore.runs.add(vcore.partial_run)
            events.post_change(self, 'runs', vcore.partial_run.name)
            events.post_change(self, 'samples')
            #most recent run will always be 1st child
            self.runlist.CheckItem2(self.runlist.GetRootItem().GetChildren()[0])
            self.set_view('Data For "%s"' % plan)

            wx.CallAfter(wx.MessageBox, "Computation finished successfully. "
                                        "Results are now displayed in the main window.")

class ComputationDialog(wx.Dialog):

    def __init__(self, parent, core):
        super(ComputationDialog, self).__init__(parent, id=wx.ID_ANY,
                                    title="Run Computations")

        self.core = core
        self.planchoice = wx.Choice(self, wx.ID_ANY,
                choices=["<SELECT PLAN>"] +
                         sorted(datastore.computation_plans.keys()))
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


class DeleteCore(wx.Dialog):
    def __init__(self, parent):
        super(DeleteCore, self).__init__(parent, id=wx.ID_ANY,
                                    title="Delete Core")
        self.parent = parent
        self.button = wx.Button(self, -1, pos=(10,130), label="Export")
        self.Bind(wx.EVT_BUTTON, self.parent.export_samples_csv, self.button)
        self.button1 = wx.Button(self, wx.ID_OK, pos=(300,130), label="Yes")
        self.button2 = wx.Button(self, wx.ID_CANCEL, pos=(390,130), label="No")
        self.dialog = wx.StaticText(self, -1, "Do you really want to delete this core?")
        self.dialog1 = wx.StaticText(self, -1, "If not, click below to export the core.")
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button, 1, wx.ALL, 5)
        self.sizer.Add(self.button1, 1, wx.ALL,5)
        self.sizer.Add(self.button2, 1, wx.ALL, 5)
        self.topsizer.Add(self.dialog, 0, wx.ALL, 5)
        self.topsizer.Add(self.dialog1, 0, wx.ALL, 5)
        self.topsizer.Add(self.sizer,0,wx.ALL, 5)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout
        self.Show(True)

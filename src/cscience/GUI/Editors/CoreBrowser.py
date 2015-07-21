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

import wx
import sys
import traceback
import wx.wizard
import wx.grid
import wx.lib.itemspicker
import wx.lib.dialogs
# import wx.lib.delayedresult # TODO fix multi-threading bug

from wx.lib.agw import aui
from wx.lib.agw import persist
import wx.lib.agw.hypertreelist as HTL

import os
import quantities as pq

from cscience import datastore
from cscience.GUI import events, icons, io, coremetadata
from cscience.GUI.Editors import AttEditor, MilieuBrowser, ComputationPlanBrowser, \
            FilterEditor, TemplateEditor, ViewEditor
from cscience.GUI import grid, graph

from cscience.framework import samples, Core, Sample, UncertainQuantity

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
        if col >= 0:
            try:
                return self.samples[row][self.view[col+1]].unitless_str()
            except AttributeError:
                return str(self.samples[row][self.view[col+1]])
        else:
            return str(self.samples[row][self.view[col+1]])
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
        obj.SaveValue('filter_name', browser.filter and browser.filter.name)
        obj.SaveValue('sorting_options', (browser.sort_primary, browser.sort_secondary,
                                          browser.sortdir_primary, browser.sortdir_secondary))

    def Restore(self):
        #restore window settings
        super(PersistBrowserHandler, self).Restore()
        browser, obj = self._window, self._pObject

        if sys.platform.startswith('win'):
            wx.MessageBox('This is a standalone application, there is no installation necessary. All the data files are stored in your home directory, in the folder \'cscibox\'.',
                          'Windows Information')

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

        #we want the view, filter, etc to be set before the core is,
        #to reduce extra work.
        try:
            viewname = obj.RestoreValue('view_name')
        except SyntaxError:
            # The 'RestoreValue' method should return false if it's unable to find the value. For some reason it's throwing a syntax excpetion. This emulates the expected behavior.
            viewname = False

        try:
            browser.set_view(viewname)
        except KeyError:
            browser.set_view('All')

        filtername = obj.RestoreValue('filter_name')
        try:
            browser.set_filter(filtername)
        except KeyError:
            filtername = ''

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
        self.HTL = None
        self.model = None

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

        item = file_menu.Append(wx.ID_ANY, "Export Samples",
                                "Export currently displayed data to a csv file (Excel).")
        self.Bind(wx.EVT_MENU, self.export_samples,item)

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
        bind_editor('milieu_browser', MilieuBrowser, "Supporting Data Sets\tCtrl-5",
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
        #self.Bind(wx.EVT_TOOL, self.OnRunCalvin, id=self.analyze_ages_id)
        self.Bind(wx.EVT_TOOL, self.do_plot, id=self.plot_samples_id)
        self.Bind(wx.EVT_CHOICE, self.select_core, self.selected_core)
        self.Bind(wx.EVT_TEXT, self.update_search, self.search_box)
        self.Bind(wx.EVT_MENU, self.update_search, self.exact_box)

        self.toolbar.Realize()
        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('btoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))

    def get_metadata(self):
        mdDict = dict()

        if not self.core:
            # if there is no core loaded yet
            return
        # add the base core and its metadata
        mycores = {self.core.name:self.core}
        # mycores = datastore.cores # for viewing all cores at once

        key = 0;
        for acore in mycores:
            mdDict[acore] = coremetadata.mdCore(acore)
            displayedCPlans = set([i.computation_plan for i in self.displayed_samples])

            # add direct core attributes
            for record in mycores[acore]['all']:
                for attribute in mycores[acore]['all'][record]:
                    if (record is 'input') and (attribute != 'depth'):
                        # Show attributes directly under core
                        attr = coremetadata.mdCoreAttribute(key, record, attribute, \
                                    mycores[acore]['all'][record][attribute], mdDict[acore])
                        key = key + 1
                        mdDict[acore].atts.append(attr)

                    elif record in displayedCPlans and attribute != 'depth':
                        #only diplay metadata for displayed samples
                        cp = None
                        # Show attributes under a computation plan object

                        # find if record is already in vcs list
                        cpind = [i for i,j in enumerate(mdDict[acore].vcs) if j.name == record]

                        if not cpind:
                            cp = coremetadata.mdCompPlan(key, mdDict[acore], record)
                            cpind = len(mdDict[acore].vcs)
                            mdDict[acore].vcs.append(cp)
                        else:
                            cpind = cpind[0]

                        attr = coremetadata.mdCoreAttribute(key, record, attribute, \
                                    mycores[acore]['all'][record][attribute], cp)

                        mdDict[acore].vcs[cpind].atts.append(attr)
                        key = key + 1

        ## for test cplan data uncomment below
        # tvc = coremetadata.mdCompPlan(20,mdDict[acore], 'testing')
        # tatt = coremetadata.mdCoreAttribute(21,tvc,'myname','my value', acore)
        # tvc.atts = [tatt,tatt]
        # mdDict[acore].vcs.append(tvc)
        # tvc = coremetadata.mdCompPlan(22,mdDict[acore], 'testing2')
        # tatt = coremetadata.mdCoreAttribute(23,tvc,'myname2','my value2', acore)
        # tvc.atts = [tatt,tatt]
        # mdDict[acore].vcs.append(tvc)
        return mdDict.values()

    def update_metadata(self):
        # update metada for display
        self.model = model = self.get_metadata()

        if not self.model:
            # if the model is empty
            return
        if self.HTL is None:
            self.create_mdPane()

        self.HTL.DeleteAllItems()

        core = model[0]
        root = self.HTL.AddRoot(core.name)
        for y in core.atts:
            attribute = self.HTL.AppendItem(root, 'input')
            self.HTL.SetPyData(attribute,None)
            self.HTL.SetItemText(attribute,y.name,1)
            self.HTL.SetItemText(attribute,y.value,2)

        for z in core.vcs:
            cplan = self.HTL.AppendItem(root, z.name)
            for i in z.atts:
                attribute = self.HTL.AppendItem(cplan, '')
                self.HTL.SetPyData(attribute,None)
                self.HTL.SetItemText(attribute,i.name,1)
                self.HTL.SetItemText(attribute,i.value,2)

        self.HTL.ExpandAll()

    def createHTL(self):
        tree_list = HTL.HyperTreeList(self,size=(300,300))

        tree_list.AddColumn("Core/Comp. Plan")
        tree_list.AddColumn("Attribute")
        tree_list.AddColumn("Value")

        return tree_list

    def create_mdPane(self):
        self.HTL = self.createHTL()

        self.update_metadata()

        pane = self._mgr.AddPane(self.HTL, aui.AuiPaneInfo().
                         Name("MDNotebook").Caption("Metadata Display").
                         Right().Layer(1).Position(1).MinimizeButton(True).
                         CloseButton(False))

        self._mgr.GetPane("MDNotebook").Show()
        self._mgr.Update()

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
            if self.sort_primary is not new_sort_primary:
                self.sort_secondary = self.sort_primary
                self.sortdir_secondary = self.sortdir_primary
            self.sort_primary = new_sort_primary
            self.sortdir_primary = new_sort_dir
            self.grid_statusbar.SetStatusText("Sorting by " + self.sort_primary + (" (^)." if new_sort_dir else " (v)."),self.INFOPANE_SORT_FIELD)
            self.display_samples()

        def OnLabelLeftClick(event):
            '''Since the top left corner (the top of the depth column) doesn'get
            sorting events, I'm reproducing what EVT_GRID_COL_SORT does on the other columns,
            setting the sorting column and order as appropriate and then manually calling OnSortColumn'''
            if event.GetRow() is -1 and event.GetCol() is -1:
                if self.grid.IsSortingBy(event.GetCol()):
                    ascend = not self.sortdir_primary
                else:
                    ascend = True
                self.grid.SetSortingColumn(event.GetCol(), ascending=ascend)
                OnSortColumn(event, ascend= ascend)
            else:
                event.Skip()

        self.grid.Bind(wx.grid.EVT_GRID_COL_SORT, OnSortColumn)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, OnLabelLeftClick)

        self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Name('thegrid').CenterPane())
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

            for unit in samples.get_conv_units(old_unit):
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
        self.close_repository()
        wx.Exit()

    def on_repository_altered(self, event):
        """
        Used to cause the File->Save Repo menu option to be enabled only if
        there is new data to save.
        Also handles various widget updates on app-wide changes
        """
        self.update_metadata()
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
            if wx.MessageBox('You have modified this repository. '
                    'Would you like to save your changes?', "Unsaved Changes",
                    wx.YES_NO | wx.ICON_EXCLAMATION | wx.NO_DEFAULT) == wx.YES:
                self.save_repository()
        #just in case, for now
        datastore.data_modified = False

    def save_repository(self, event=None):
        try:
            datastore.save_datastore()
        except:
            import traceback
            print traceback.format_exc()
            wx.MessageBox('Something went wrong trying to save the repository. '
                          'Please close and re-open CScience. Your repository '
                          'will be reverted to its previous saved state.')
            #get rid of nag, if it was going to come up
            datastore.data_modified = False


    def OnCopy(self, event):
        samples = [self.displayed_samples[index] for index in self.grid.SelectedRows]
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
            self.filter_samples()
        if (value):
            self.grid_statusbar.SetStatusText("Searched with parameters: " + self.search_box.GetValue(),self.INFOPANE_SEARCH_FIELD)
        else:
            self.grid_statusbar.SetStatusText("",self.INFOPANE_SEARCH_FIELD)



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
                self.filter = None
                self.grid_statusbar.SetStatusText("",self.INFOPANE_ROW_FILT_FIELD)
                self.set_view('All')
                self.select_core(corename=importwizard.corename)
            else:
                self.selected_core.SetStringSelection(self.core.name)
            if importwizard.saverepo:
                self.save_repository()

        importwizard.Destroy()

    def export_samples(self, event):
        return io.export_samples(self.view, self.displayed_samples, self.model)


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
                self.grid_statusbar.SetStatusText("Using " + view_name + " view for columns.",self.INFOPANE_COL_FILT_FIELD)
            else:
                self.grid_statusbar.SetStatusText("Showing all columns.",self.INFOPANE_COL_FILT_FIELD)
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
            workflow.execute(computation_plan, vcore)
        except:
            msg = "We're sorry, something went wrong while running that computation. " +\
                  "Please tell someone appropriate!\n\n\n\n\n\n\n******DEBUG******\n\n" + \
                  traceback.format_exc()
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Computation Error")
            dlg.ShowModal()
            raise
        else:
            events.post_change(self, 'samples')
            self.filter = datastore.filters['Plan "%s"' % plan]
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

class AgeFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        # A data entry box
        self.item = wx.TextCtrl(self)
        # A button to agree
        self.button = wx.Button(self, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.getString, self.button)
        # Text 'splaning what to do
        self.dialog = wx.StaticText(self, -1, "Enter date correction")

        # A sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.item, 1, wx.EXPAND)
        self.sizer.Add(self.button, 0, wx.EXPAND)
        self.sizer.Add(self.dialog, 2, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        self.Show(True)

    def getString(self, event):
        string = self.item.GetValue()

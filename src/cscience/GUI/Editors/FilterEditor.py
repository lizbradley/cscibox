"""
FilterEditor.py

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
import wx.lib.newevent

from cscience import datastore
from cscience.framework import views
from cscience.GUI.Editors import MemoryFrame
from cscience.GUI import events

datastore = datastore.Datastore()

class DetailPanel(wx.Panel):
    def __init__(self, parent):
        self._filter = None
        super(DetailPanel, self).__init__(parent, id=wx.ID_ANY,
                                          style=wx.SUNKEN_BORDER)
        self.ExtraStyle = self.ExtraStyle | wx.WS_EX_VALIDATE_RECURSIVELY
        self.SetBackgroundColour(wx.WHITE)
        tsize = (16, 16)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize)
        del_bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, tsize)
        new_bmp =  wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
        tb = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        tb.SetToolBitmapSize(tsize)

        tool = tb.AddLabelTool(wx.ID_ANY, "Save Changes", save_bmp,
                               shortHelp="Save Changes")
        self.Bind(wx.EVT_TOOL, self.save_changes, tool)
        tool = tb.AddLabelTool(wx.ID_ANY, "Discard Changes", del_bmp,
                               shortHelp="Discard Changes")
        self.Bind(wx.EVT_TOOL, self.discard_changes, tool)
        tb.AddSeparator()
        tool = tb.AddLabelTool(wx.ID_ANY, "Add New...", new_bmp, shortHelp="Add New...")
        self.Bind(wx.EVT_TOOL, self.add_new, tool)
        self.type_combo = wx.ComboBox(
                tb, wx.ID_ANY, value="Item", choices=["Item", "Subfilter"],
                style=wx.CB_DROPDOWN | wx.CB_READONLY)
        tb.AddControl(self.type_combo)

        tb.Realize()

        self.name_panel = DetailPanel.NamePanel(self)
        self.item_panel = DetailPanel.ItemPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, flag=wx.EXPAND)
        sizer.Add(self.name_panel, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self.item_panel, border=5, proportion=1,
                  flag=wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)

    def save_changes(self, event):
        if not self.Validate():
            return

        # need to update the name, here...
        oldname = self.filter.name
        #clear out all the old filter items
        del self.filter[:]
        self.name_panel.save(self.filter)
        self.item_panel.save(self.filter)
        #also saves the new filter, because reasons, for now
        datastore.filters.rename(oldname, self.filter)
        events.post_change(self, 'filters', self.filter.name)

    def discard_changes(self, event):
        self.filter = self.filter

    def add_new(self, event):
        itemtype = self.type_combo.GetValue().lower()
        if itemtype == 'item':
            item = views.FilterItem()
        elif itemtype == 'subfilter':
            #TODO: don't allow subfilter as a choice when only one filter exists!
            item = views.FilterFilter(parent_name=self.filter.name)
            if len(item.item_choices) <= 1:
                wx.MessageBox("A subfilter cannot be added to this "
                              "filter as no other filters exist.")
                return
        self.item_panel.add_item(item)
        self.item_panel.Layout()
        self.Layout()

    @property
    def filter(self):
        return self._filter
    @filter.setter
    def filter(self, new_filter):
        self._filter = new_filter
        self.name_panel.filter = new_filter
        self.item_panel.filter = new_filter
        self.Layout()


    class ItemPanel(wx.ScrolledWindow):

        class ItemValidator(wx.PyValidator):
            def __init__(self):
                super(DetailPanel.ItemPanel.ItemValidator, self).__init__()

            def Clone(self):
                return DetailPanel.ItemPanel.ItemValidator()

            def Validate(self, win):
                editor = self.GetWindow()
                testitem = editor.item.copy()

                #These constrain the value types, but should not otherwise
                #crash (since they are comboboxes)
                testitem.show_item = editor.item_box.GetValue()
                if editor.ops_box:
                    testitem.show_op = editor.ops_box.GetValue()
                vbox = editor.value_box
                try:
                    testitem.show_value = vbox.GetValue()
                except ValueError:
                    vbox.SetSelection(-1, -1)
                    vbox.SetBackgroundColour('pink')
                    vbox.SetFocus()
                    vbox.Refresh()
                    wx.MessageBox("This is an invalid value for this attribute",
                                  "Save Error")
                    return False
                else:
                    vbox.SetBackgroundColour(
                            wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                    vbox.Refresh()
                return True

        class ItemEditor(wx.Panel):
            def __init__(self, parent, filteritem):
                self.item = filteritem
                super(DetailPanel.ItemPanel.ItemEditor, self).__init__(parent,
                                                                id=wx.ID_ANY)
                row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.item_box = wx.ComboBox(self, id=wx.ID_ANY,
                                            value=self.item.show_item,
                                            choices=self.item.item_choices,
                                            style=wx.CB_DROPDOWN | wx.CB_READONLY)
                if self.item.value_choices:
                    self.value_box = wx.ComboBox(self, wx.ID_ANY,
                                                 value=self.item.show_value,
                                                 choices=self.item.value_choices,
                                                 style=wx.CB_DROPDOWN | wx.CB_READONLY)
                else:
                    self.value_box = wx.TextCtrl(self, wx.ID_ANY,
                                                 value=self.item.show_value)

                self.ops_box = None
                ops = self.item.comparators
                if not ops:
                    row_sizer.Add(self.value_box, border=5, flag=wx.ALL)
                    row_sizer.Add(self.item_box, border=5, flag=wx.ALL)
                else:
                    row_sizer.Add(self.item_box, border=5, flag=wx.ALL)
                    if len(ops) == 1:
                        row_sizer.Add(wx.StaticText(self, wx.ID_ANY, ops[0]),
                                  border=5, flag=wx.ALL)
                    else:
                        self.ops_box = wx.ComboBox(self, wx.ID_ANY,
                                                   value=self.item.show_op, choices=ops,
                                                   style=wx.CB_DROPDOWN | wx.CB_READONLY)
                        row_sizer.Add(self.ops_box, border=5, flag=wx.ALL)
                    row_sizer.Add(self.value_box, border=5, flag=wx.ALL)
                self.SetValidator(DetailPanel.ItemPanel.ItemValidator())

                remove_button = wx.Button(self, wx.ID_ANY, "Remove")
                self.Bind(wx.EVT_BUTTON, self.remove_item, remove_button)
                row_sizer.Add(remove_button, border=5, flag=wx.ALL)
                self.SetSizer(row_sizer)
                self.Layout()

            def remove_item(self, event):
                self.Parent.remove(self)

            def save(self):
                self.item.show_item = self.item_box.GetValue()
                if self.ops_box:
                    self.item.show_op = self.ops_box.GetValue()
                self.item.show_value = self.value_box.GetValue()
                return self.item

        def __init__(self, parent):
            self.editors = []
            super(DetailPanel.ItemPanel, self).__init__(parent, id=wx.ID_ANY)
            self.ExtraStyle = self.ExtraStyle | wx.WS_EX_VALIDATE_RECURSIVELY

            self.noitem_label = wx.StaticText(self, id=wx.ID_ANY,
                                    label="Selected Filter has no Items")
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.noitem_label, border=5, flag=wx.ALL)

            self.SetSizer(self.sizer)
            self.Layout()
            #Don't show this panel when no filter at all is selected
            self.Hide()

        def Layout(self, *args, **kwargs):
            self.SetVirtualSize(self.sizer.GetMinSize())
            self.SetScrollRate(20, 20)
            super(DetailPanel.ItemPanel, self).Layout(*args, **kwargs)

        def filter(self, new_filter):
            for editor in self.editors:
                editor.Destroy()
            self.editors = []
            if new_filter is None:
                self.Hide()
            else:
                self.noitem_label.Show(not new_filter)
                for item in new_filter:
                    self.add_item(item)
                self.Show()
            self.Layout()
        filter = property(fset=filter)

        def add_item(self, filteritem):
            self.noitem_label.Hide()
            editor = DetailPanel.ItemPanel.ItemEditor(self, filteritem)
            self.sizer.Add(editor)
            self.editors.append(editor)

        def remove(self, ed):
            self.editors.remove(ed)
            ed.Destroy()
            #if this was the last editor, show the "no item" label
            self.noitem_label.Show(not self.editors)
            self.Layout()

        def save(self, f):
            for ed in self.editors:
                f.append(ed.save())

    class NamePanel(wx.Panel):

        class NameValidator(wx.PyValidator):
            def __init__(self, init_name=None):
                super(DetailPanel.NamePanel.NameValidator, self).__init__()
                self.init_name = init_name

            def Clone(self):
                return DetailPanel.NamePanel.NameValidator(self.init_name)

            def Validate(self, win):
                tc = self.GetWindow()
                val = tc.GetValue()

                #TODO: handle messages via exception?
                if not val or val == '<No Filter Selected>':
                    wx.MessageBox("You need to enter a name for this filter", "Save Error")
                elif val != self.init_name and val in datastore.filters.keys():
                    wx.MessageBox('The new filter name conflicts with an existing name. '
                          'Please choose a different name.', 'Name Conflict')
                else:
                    tc.SetBackgroundColour(
                         wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                    tc.Refresh()
                    return True
                tc.SetSelection(-1, -1)
                tc.SetBackgroundColour('pink')
                tc.SetFocus()
                tc.Refresh()
                return False

        def __init__(self, parent):
            super(DetailPanel.NamePanel, self).__init__(parent, id=wx.ID_ANY)

            self.name_box = wx.TextCtrl(self, id=wx.ID_ANY, size=(150, -1),
                                        value='<No Filter Selected>',
                                        validator=DetailPanel.NamePanel.NameValidator())
            self.match_type = wx.ComboBox(self, wx.ID_ANY, choices=["All", "Any"],
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self, wx.ID_ANY, "Name: "), border=5, flag=wx.ALL)
            sz.Add(self.name_box, border=5, flag=wx.ALL | wx.EXPAND)
            sizer.Add(sz, flag=wx.EXPAND)

            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self, wx.ID_ANY, "Match"), border=5,
                   flag=wx.ALL)
            sz.Add(self.match_type, border=5, flag=wx.TOP | wx.BOTTOM)
            sz.Add(wx.StaticText(self, wx.ID_ANY, "of the following:"), border=5,
                   flag=wx.ALL)
            sizer.Add(sz, flag=wx.EXPAND)

            self.SetSizer(sizer)
            self.Disable()

        def filter(self, new_filter):
            self.name_box.SetBackgroundColour(
                         wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.name_box.Refresh()
            if new_filter is None:
                self.name_box.SetValue('<No Filter Selected>')
                self.name_box.Validator.init_name = None
                self.match_type.SetValue('All')
            else:
                self.name_box.SetValue(new_filter.name)
                self.name_box.Validator.init_name = new_filter.name
                self.name_box.SetSelection(-1, -1)
                self.name_box.SetFocus()
                self.match_type.SetValue(new_filter.filtertype)
            self.Enable(new_filter is not None)
        filter = property(fset=filter)

        def save(self, f):
            f.name = self.name_box.GetValue()
            f.filtertype = self.match_type.GetValue()

class FilterEditor(MemoryFrame):

    framename = 'filtereditor'

    def __init__(self, parent):
        super(FilterEditor, self).__init__(parent, id=wx.ID_ANY, title='Filter Editor')

        self.statusbar = self.CreateStatusBar()
        self.filterlabel = wx.StaticText(self, wx.ID_ANY, "Filter")

        self.filter = None
        self.filters_list = wx.ListBox(self, wx.ID_ANY, choices=sorted(datastore.filters.keys()),
                                       style=wx.LB_SINGLE)
        self.SetBackgroundColour(wx.Colour(215,215,215))
        add_button = wx.Button(self, wx.ID_ANY, "Add Filter")

        self.detail_panel = DetailPanel(self)

        sizer = wx.FlexGridSizer(3, 2, 10, 10)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Filters"))
        sizer.Add(self.filterlabel)
        sizer.Add(self.filters_list, flag=wx.EXPAND)
        sizer.Add(self.detail_panel, flag=wx.EXPAND)
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(add_button, border=5, flag=wx.ALL)
        sizer.Add(bsz, flag=wx.ALIGN_CENTER_HORIZONTAL)
        sizer.AddGrowableCol(0, proportion=1)
        sizer.AddGrowableCol(1, proportion=3)
        sizer.AddGrowableRow(1, proportion=1)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_LISTBOX, self.select_filter, self.filters_list)
        self.Bind(wx.EVT_BUTTON, self.add_filter, add_button)

        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)

    def on_repository_altered(self, event):
        if 'filters' in event.changed:
            self.filters_list.Set(sorted(datastore.filters.keys()))
            if event.value:
                try:
                    new_index = self.filters_list.GetItems().index(event.value)
                except ValueError:
                    pass
                else:
                    #bah, there's no good way to make this fire an event
                    self.filters_list.SetSelection(new_index)
                    self.select_filter()
        event.Skip()

    def add_filter(self, event):
        suffix = 1
        name = "Untitled %d" % suffix
        while name in datastore.filters:
            suffix += 1
            name = "Untitled %d" % suffix

        new_filter = views.Filter(name, all)
        datastore.filters.add(new_filter)
        events.post_change(self, 'filters', name)

    def select_filter(self, event=None):
        name = self.filters_list.GetStringSelection()
        self.filter = datastore.filters[name]

        self.detail_panel.filter = self.filter





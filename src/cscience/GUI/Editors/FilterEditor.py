"""
FilterEditor.py

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

from cscience import datastore
from cscience.framework import views
from cscience.GUI.Editors import MemoryFrame

class FilterEditor(MemoryFrame):
    
    framename = 'filtereditor'

    def __init__(self, parent):
        super(FilterEditor, self).__init__(parent, id=wx.ID_ANY, title='Filter Editor')
    
        self.statusbar = self.CreateStatusBar()
        
        filtersLabel = wx.StaticText(self, wx.ID_ANY, "Filters")
        filterLabel = wx.StaticText(self, wx.ID_ANY, "Filter")

        self.filter = None        
        self.filters_list = wx.ListBox(self, wx.ID_ANY, choices=sorted(datastore.filters.keys()), 
                                       style=wx.LB_SINGLE)
        
        self.add_button = wx.Button(self, wx.ID_ANY, "Add Filter")
        self.remove_button = wx.Button(self, wx.ID_ANY, "Delete Filter")
        self.edit_button = wx.Button(self, wx.ID_ANY, "Edit Filter")
        
        self.remove_button.Disable()
        self.edit_button.Disable()
        
        self.addItem = wx.Button(self, wx.ID_ANY, "Add Item")
        self.addGroup = wx.Button(self, wx.ID_ANY, "Add Group")
        self.addSubFilter = wx.Button(self, wx.ID_ANY, "Add Subfilter")
        self.saveButton = wx.Button(self, wx.ID_ANY, "Save Changes")
        self.discardButton = wx.Button(self, wx.ID_ANY, "Discard Changes")

        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()
        self.discardButton.Disable()
        
        self.itemWindow = wx.ScrolledWindow(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        
        itemLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "No Filter Selected")
        
        self.item_sizer = wx.BoxSizer(wx.VERTICAL)
        self.item_sizer.Add(itemLabel, border=5, flag=wx.ALL)
        
        self.itemWindow.SetSizer(self.item_sizer)
        
        self.itemWindow.SetVirtualSize(self.item_sizer.GetMinSize())
        self.itemWindow.SetScrollRate(20, 20)
        self.itemWindow.Layout()
        
        buttonSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer1.Add(self.add_button, border=5, flag=wx.ALL)
        buttonSizer1.Add(self.remove_button, border=5, flag=wx.ALL)
        buttonSizer1.Add(self.edit_button, border=5, flag=wx.ALL)

        buttonSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer2.Add(self.addItem, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.addGroup, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.addSubFilter, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.saveButton, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.discardButton, border=5, flag=wx.ALL)
        
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(filtersLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.filters_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnOneSizer.Add(buttonSizer1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(filterLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.itemWindow, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        columnTwoSizer.Add(buttonSizer2, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)
        
        self.SetSizer(sizer)
        self.Layout()
        self.SetMinSize(self.GetSize())

        self.Bind(wx.EVT_LISTBOX, self.select_view, self.filters_list)
        self.Bind(wx.EVT_BUTTON, self.delete_view, self.remove_button)
        self.Bind(wx.EVT_BUTTON, self.OnAddFilter, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.OnEditFilter, self.edit_button)
        self.Bind(wx.EVT_BUTTON, self.OnDiscardChanges, self.discardButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddItem, self.addItem)
        self.Bind(wx.EVT_BUTTON, self.OnAddGroup, self.addGroup)
        self.Bind(wx.EVT_BUTTON, self.OnAddSubFilter, self.addSubFilter)
        self.Bind(wx.EVT_BUTTON, self.OnSaveChanges, self.saveButton)

        self.filters_list.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInFilters)

    def OnAddFilter(self, event):
        suffix = 1
        name = "Untitled %d" % suffix
        while name in datastore.filters:
            suffix += 1
            name = "Untitled %d" % suffix
            
        new_filter = views.Filter(name, all)
        datastore.filters.add(new_filter)
        self.filters_list.Set(sorted(datastore.filters.keys()))
        self.remove_button.Disable()
        self.edit_button.Disable()
        self.filter = None
        datastore.data_modified = True
        self.UpdateFiltersMenu()
        self.ConfigureColumnTwoDisplayMode()
        self.filters_list.SetStringSelection(name)
        self.select_view(None)
        self.OnEditFilter(None)
        
    def OnEditFilter(self, event):
        self.discardButton.Enable(True)
        self.addItem.Enable(True)
        self.addGroup.Enable(True)
        self.addSubFilter.Enable(True)
        self.add_button.Disable()
        self.remove_button.Disable()
        self.edit_button.Disable()
        self.filters_list.Disable()
        self.edit_filter = self.filter.copy()
        self.ConfigureColumnTwoEditMode()

    def OnAddItem(self, event):
        self.edit_filter.append(views.FilterItem())
        self.ConfigureColumnTwoEditMode()
        
    def OnAddGroup(self, event):
        self.edit_filter.append(views.FilterGroup())
        self.ConfigureColumnTwoEditMode()
        
    def OnAddSubFilter(self, event):
        ff = views.FilterFilter(self.edit_filter.name)
        if ff.item_choices:
            self.edit_filter.append(ff)
            self.statusbar.SetStatusText('')
        else:
            self.statusbar.SetStatusText("A subfilter cannot be added to this "
                                         "filter as no other filters exist.")
        self.ConfigureColumnTwoEditMode()
        
    def OnDiscardChanges(self, event):
        self.discardButton.Disable()
        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()
        
        self.add_button.Enable(True)
        self.filters_list.Enable(True)
        
        self.select_view(None)
        self.Refresh()

        self.edit_filter = None
        
        self.ConfigureColumnTwoDisplayMode()
        
    def OnSaveChanges(self, event):
        if self.edit_filter.name != self.filter.name and self.edit_filter.name in datastore.filters:
            wx.MessageBox('The new filter name conflicts with an existing name. '
                          'Please modify before saving changes.', 'Name Conflict', 
                          wx.OK | wx.ICON_INFORMATION)
            return
            
        # need to update filters that point at self.filter to self.edit_filter
        for name in datastore.filters:
            f = datastore.filters[name]
            for item in f.items:
                if type(item) == views.FilterFilter:
                    if item.filter is self.filter:
                        item.filter = self.edit_filter

        self.discardButton.Disable()
        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()

        del datastore.filters[self.filter.name]
        datastore.filters.add(self.edit_filter)
        
        self.filters_list.Set(sorted(datastore.filters.keys()))
        
        self.filters_list.SetStringSelection(self.edit_filter.name)

        self.add_button.Enable(True)
        self.filters_list.Enable(True)

        self.select_view(None)
        self.Refresh()

        self.edit_filter = None
        
        datastore.data_modified = True
        self.UpdateFiltersMenu()
        
        self.ConfigureColumnTwoDisplayMode()
        
    def select_view(self, event):
        name = self.filters_list.GetStringSelection()
        self.filter = datastore.filters[name]
        
        # can only delete filter if no other filter depends on it        
        is_depended_on = any([f.depends_on(name) for f in datastore.filters.values()])
        self.remove_button.Enable(not is_depended_on)
        self.statusbar.SetStatusText(is_depended_on and ("This filter cannot be "
                "deleted because it is used by at least one other filter.") or "")
        self.edit_button.Enable(True)      
        self.ConfigureColumnTwoDisplayMode()

    def ConfigureColumnTwoDisplayMode(self):
        self.item_sizer.Clear(True)
        if self.filter:
            #TODO: use a panel so we don't have to make & add this every time, ew!
            name_label = wx.StaticText(self.itemWindow, wx.ID_ANY, "Name: %s" % self.filter.name)
            self.item_sizer.Add(name_label, border=5, flag=wx.ALL | wx.EXPAND)
            
            type_label = wx.StaticText(self.itemWindow, wx.ID_ANY, 
                            "Match %s of the following:" % self.filter.filtertype)
            self.item_sizer.Add(type_label, border=5, flag=wx.ALL | wx.EXPAND)
            
            if self.filter.items:
                for item in self.filter.items:
                    row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                    item_label = wx.StaticText(self.itemWindow, wx.ID_ANY, item.show_item)
                    value_label = wx.StaticText(self.itemWindow, wx.ID_ANY, item.show_value)
                        
                    if not item.comparators:
                        row_sizer.Add(value_label, border=5, flag=wx.ALL)
                        row_sizer.Add(item_label, border=5, flag=wx.ALL)
                    else:
                        row_sizer.Add(item_label, border=5, flag=wx.ALL)
                        row_sizer.Add(wx.StaticText(self.itemWindow, wx.ID_ANY, 
                                                    item.show_op), 
                                      border=5, flag=wx.ALL)
                        row_sizer.Add(value_label, border=5, flag=wx.ALL)
                    self.item_sizer.Add(row_sizer, border=5, flag=wx.ALL)
            else:
                self.item_sizer.Add(wx.StaticText(self.itemWindow, wx.ID_ANY, 
                    "Selected filter has no items."), border=5, flag=wx.ALL)
        else:
            self.item_sizer.Add(wx.StaticText(self.itemWindow, wx.ID_ANY, "No Filter Selected"), 
                                border=5, flag=wx.ALL)
            
        self.itemWindow.SetVirtualSize(self.item_sizer.GetMinSize())
        self.itemWindow.SetScrollRate(20, 20)
        self.itemWindow.Layout()
        self.Layout()

    def ConfigureColumnTwoEditMode(self):
        self.item_sizer.Clear(True)

        #TODO: use a panel so we don't have to make & add this every time, ew!
        name_label = wx.StaticText(self.itemWindow, wx.ID_ANY, "Name: ")
        name_box = wx.TextCtrl(self.itemWindow, wx.ID_ANY, value=self.edit_filter.name,
                               name="filter name")
        self.itemWindow.Bind(wx.EVT_TEXT, self.on_filtername_change, name_box)
        name_box.SetFocus()
        name_box.SetSelection(-1, -1)
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(name_label, border=5, flag=wx.ALL)
        row_sizer.Add(name_box, border=5, flag=wx.ALL | wx.EXPAND)
        self.item_sizer.Add(row_sizer, border=5, flag=wx.ALL)
        
        name_label = wx.StaticText(self.itemWindow, wx.ID_ANY, "Match")
        matchtype_box = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=self.edit_filter.filtertype, 
                              choices=["All", "Any"], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        suffix_label = wx.StaticText(self.itemWindow, wx.ID_ANY, "of the following:")
        
        self.itemWindow.Bind(wx.EVT_COMBOBOX, self.on_filtertype_change, matchtype_box)
        
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(name_label, border=5, flag=wx.ALL)
        row_sizer.Add(matchtype_box, border=5, flag=wx.ALL)
        row_sizer.Add(suffix_label, border=5, flag=wx.ALL)
        self.item_sizer.Add(row_sizer, border=5, flag=wx.ALL)
        
        if self.edit_filter.items:
            for index, item in enumerate(self.edit_filter.items):
                row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                item_box = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=item.show_item,
                                       choices=item.item_choices, name=str(index),
                                       style=wx.CB_DROPDOWN | wx.CB_READONLY)
                self.itemWindow.Bind(wx.EVT_COMBOBOX, self.on_filteritem_change, item_box)
                if item.value_choices:
                    value_box = wx.ComboBox(self.itemWindow, wx.ID_ANY, 
                                    value=item.show_value, choices=item.value_choices, 
                                    name=str(index), style=wx.CB_DROPDOWN | wx.CB_READONLY)
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.on_filtervalue_change, value_box)
                else:
                    value_box = wx.TextCtrl(self.itemWindow, wx.ID_ANY, 
                                            value=item.show_value, name=str(index))
                    self.itemWindow.Bind(wx.EVT_TEXT, self.on_filtervalue_change, value_box)
                    
                ops = item.comparators
                if not ops:
                    row_sizer.Add(value_box, border=5, flag=wx.ALL)
                    row_sizer.Add(item_box, border=5, flag=wx.ALL)
                else:
                    row_sizer.Add(item_box, border=5, flag=wx.ALL)
                    if len(ops) == 1:
                        row_sizer.Add(wx.StaticText(self.itemWindow, wx.ID_ANY, ops[0]), 
                                      border=5, flag=wx.ALL)
                    else:
                        ops_box = wx.ComboBox(self.itemWindow, wx.ID_ANY, 
                                    value=item.show_op, choices=ops, 
                                    name=str(index), style=wx.CB_DROPDOWN | wx.CB_READONLY)
                        self.itemWindow.Bind(wx.EVT_COMBOBOX, self.on_filterop_change, ops_box)
                        row_sizer.Add(ops_box, border=5, flag=wx.ALL)
                    row_sizer.Add(value_box, border=5, flag=wx.ALL)
                    
                remove_button = wx.Button(self.itemWindow, wx.ID_ANY, 
                                          "Remove", name=str(index))
                self.itemWindow.Bind(wx.EVT_BUTTON, self.OnRemoveItem, remove_button)
                
                row_sizer.Add(remove_button, border=5, flag=wx.ALL)
                self.item_sizer.Add(row_sizer, border=5, flag=wx.ALL)
        else:
            self.item_sizer.Add(wx.StaticText(self.itemWindow, wx.ID_ANY, 
                "Filter has no items. Add items with buttons below."), border=5, flag=wx.ALL)

        self.itemWindow.SetVirtualSize(self.item_sizer.GetMinSize())
        self.itemWindow.SetScrollRate(20, 20)
        self.itemWindow.Layout()
        self.Layout()
        
    def OnRemoveItem(self, event):
        name = event.GetEventObject().GetName()
        del self.edit_filter[int(name)]
        self.saveButton.Enable()
        self.ConfigureColumnTwoEditMode()
        
    def on_filtervalue_change(self, event):
        index = int(event.GetEventObject().GetName())
        self.edit_filter.items[index].show_value = event.GetString()
        self.saveButton.Enable()
        
    def on_filteritem_change(self, event):
        index = int(event.GetEventObject().GetName())
        self.edit_filter.items[index].show_item = event.GetString()
        self.saveButton.Enable()
        
    def on_filterop_change(self, event):
        index = int(event.GetEventObject().GetName())
        self.edit_filter.items[index].show_op = event.GetString()
        self.saveButton.Enable()
        
    def on_filtername_change(self, event):
        self.edit_filter.filter_name = event.GetString()
        self.saveButton.Enable()
        
    def on_filtertype_change(self, event):
        self.edit_filter.filtertype = event.GetString()
        self.saveButton.Enable()
        
    def delete_view(self, event):
        name = self.filters_list.GetStringSelection()
        del datastore.filters[name]
        self.filters_list.Set(sorted(datastore.filters.keys()))
        self.remove_button.Disable()
        self.edit_button.Disable()
        self.filter = None
        datastore.data_modified = True
        self.UpdateFiltersMenu()
        self.ConfigureColumnTwoDisplayMode()

    def UpdateFiltersMenu(self):
        # whenever a filter is created or destroyed
        # we need to update the list of filters
        # that are available within the sample
        # browser
        self.GetParent().UpdateFilters()

    # list box controls do not deliver deselection events when in 'single selection' mode
    # but it is still possible for the user to clear the selection from such a list
    # as such, we need to monitor the LEFT_UP events for each of our list boxes and
    # check to see if the selection got cleared without us knowning about it
    # if so, we need to update the user interface appropriately
    # this code falls under the category of "THIS SUCKS!" It would be much cleaner to
    # just be informed of list deselection events
    def OnLeftUpInFilters(self, event):
        index = self.filters_list.GetSelection()
        if index == -1:
            self.filter = None
            self.remove_button.Disable()
            self.edit_button.Disable()
            self.statusbar.SetStatusText("")
            self.ConfigureColumnTwoDisplayMode()
        event.Skip()


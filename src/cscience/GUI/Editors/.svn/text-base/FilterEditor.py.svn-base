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

from ACE.Framework.FilterItem import FilterItem
from ACE.Framework.FilterGroup import FilterGroup
from ACE.Framework.FilterFilter import FilterFilter

from ACE.Framework import Attributes
from ACE.Framework import Filter
from ACE.Framework import Operations

class FilterEditor(wx.Frame):

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Filter Editor')
        
        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusbar = self.CreateStatusBar()
        
        filtersLabel = wx.StaticText(self, wx.ID_ANY, "Filters")
        filterLabel  = wx.StaticText(self, wx.ID_ANY, "Filter")

        self.atts    = self.repoman.GetModel("Attributes")

        self.filters = self.repoman.GetModel("Filters")
        self.filter  = None
        
        self.filters_list    = wx.ListBox(self, wx.ID_ANY, choices=self.filters.names(), style=wx.LB_SINGLE)
        
        self.addButton    = wx.Button(self, wx.ID_ANY, "Add Filter")
        self.removeButton = wx.Button(self, wx.ID_ANY, "Delete Filter")
        self.editButton   = wx.Button(self, wx.ID_ANY, "Edit Filter")
        
        self.removeButton.Disable()
        self.editButton.Disable()
        
        self.addItem       = wx.Button(self, wx.ID_ANY, "Add Item")
        self.addGroup       = wx.Button(self, wx.ID_ANY, "Add Group")
        self.addSubFilter  = wx.Button(self, wx.ID_ANY, "Add Subfilter")
        self.saveButton    = wx.Button(self, wx.ID_ANY, "Save Changes")
        self.discardButton = wx.Button(self, wx.ID_ANY, "Discard Changes")

        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()
        self.discardButton.Disable()
        
        self.itemWindow = wx.ScrolledWindow(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        
        itemLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "No Filter Selected")
        
        self.itemSizer = wx.BoxSizer(wx.VERTICAL)
        self.itemSizer.Add(itemLabel, border=5, flag=wx.ALL)
        
        self.itemWindow.SetSizer(self.itemSizer)
        
        self.itemWindow.SetVirtualSize(self.itemSizer.GetMinSize())
        self.itemWindow.SetScrollRate(20,20)
        self.itemWindow.Layout()
        
        buttonSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer1.Add(self.addButton,    border=5, flag=wx.ALL)
        buttonSizer1.Add(self.removeButton, border=5, flag=wx.ALL)
        buttonSizer1.Add(self.editButton, border=5, flag=wx.ALL)

        buttonSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer2.Add(self.addItem,    border=5, flag=wx.ALL)
        buttonSizer2.Add(self.addGroup,    border=5, flag=wx.ALL)
        buttonSizer2.Add(self.addSubFilter, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.saveButton, border=5, flag=wx.ALL)
        buttonSizer2.Add(self.discardButton, border=5, flag=wx.ALL)
        
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(filtersLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.filters_list, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        columnOneSizer.Add(buttonSizer1, border=5, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(filterLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.itemWindow, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        columnTwoSizer.Add(buttonSizer2, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)
        
        self.SetSizer(sizer)
        self.Layout()
        self.SetSize(self.GetBestSize())
        self.SetMinSize(self.GetSize())
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/filtereditor/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/filtereditor/location", repr(self.GetPosition())))

        self.SetSize(size)
        self.SetPosition(loc)

        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.filters_list)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.removeButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddFilter, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnEditFilter, self.editButton)
        self.Bind(wx.EVT_BUTTON, self.OnDiscardChanges, self.discardButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddItem, self.addItem)
        self.Bind(wx.EVT_BUTTON, self.OnAddGroup, self.addGroup)
        self.Bind(wx.EVT_BUTTON, self.OnAddSubFilter, self.addSubFilter)
        self.Bind(wx.EVT_BUTTON, self.OnSaveChanges, self.saveButton)

        self.filters_list.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInFilters)

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        repoman.AddWindow(self)

    def OnAddFilter(self, event):
        found_name = False
        suffix     = 1
        names      = self.filters.names()
        name       = None
        while not found_name:
            name = "Untitled %d" % (suffix)
            if name in names:
                suffix += 1
            else:
                found_name = True
        new_filter = Filter.Filter(name, Filter.And)
        self.filters.add(new_filter)
        self.filters_list.Set(self.filters.names())
        self.removeButton.Disable()
        self.editButton.Disable()
        self.filter = None
        self.repoman.RepositoryModified()
        self.UpdateFiltersMenu()
        self.ConfigureColumnTwoDisplayMode()
        self.filters_list.SetStringSelection(name)
        self.OnSelect(None)
        self.OnEditFilter(None)
        
    def OnEditFilter(self, event):
        self.discardButton.Enable(True)
        self.addItem.Enable(True)
        self.addGroup.Enable(True)
        self.addSubFilter.Enable(True)
        self.addButton.Disable()
        self.removeButton.Disable()
        self.editButton.Disable()
        self.filters_list.Disable()
        self.edit_filter = self.filter.copy()
        self.ConfigureColumnTwoEditMode()

    def OnAddItem(self, event):
        self.edit_filter.add_item(FilterItem('id', Operations.Equal, '<EDIT ME>'))
        self.ConfigureColumnTwoEditMode()
        
    def OnAddGroup(self, event):
        self.edit_filter.add_item(FilterGroup('Select Group', True, self.repoman))
        self.ConfigureColumnTwoEditMode()
        
    def OnAddSubFilter(self, event):
        names = self.filters.names()
        names.remove(self.edit_filter.name())
        if len(names) > 0:
            name = names[0]
            self.edit_filter.add_item(FilterFilter(self.filters.get(name), False))
            self.statusbar.SetStatusText("")
        else:
            self.statusbar.SetStatusText("A subfilter cannot be added to this filter as no other filters exist.")
        self.ConfigureColumnTwoEditMode()
        
    def OnDiscardChanges(self, event):
        self.discardButton.Disable()
        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()
        
        self.addButton.Enable(True)
        self.filters_list.Enable(True)
        
        self.OnSelect(None)
        self.Refresh()

        self.edit_filter = None
        
        self.ConfigureColumnTwoDisplayMode()
        
    def OnSaveChanges(self, event):
        names = self.filters.names()
        names.remove(self.filter.name())
        if self.edit_filter.name() in names:
            dialog = wx.MessageDialog(None, 'The new filter name conflicts with an existing name. Please modify before saving changes.','Name Conflict', wx.OK | wx.ICON_INFORMATION)
            dialog.ShowModal()
            return
            
        # need to update filters that point at self.filter to self.edit_filter
        for name in names:
            f = self.filters.get(name)
            for item in f.items:
                if type(item) == FilterFilter:
                    if item.filter is self.filter:
                        item.filter = self.edit_filter

        self.discardButton.Disable()
        self.addItem.Disable()
        self.addGroup.Disable()
        self.addSubFilter.Disable()
        self.saveButton.Disable()

        self.filters.remove(self.filter.name())
        self.filters.add(self.edit_filter)
        
        self.filters_list.Set(self.filters.names())
        
        self.filters_list.SetStringSelection(self.edit_filter.name())

        self.addButton.Enable(True)
        self.filters_list.Enable(True)

        self.OnSelect(None)
        self.Refresh()

        self.edit_filter = None
        
        self.repoman.RepositoryModified()
        self.UpdateFiltersMenu()
        
        self.ConfigureColumnTwoDisplayMode()
        
    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/filtereditor/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()
        config.Write("windows/filtereditor/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().filterEditor = None
        del(self.GetParent().filterEditor)
        self.Destroy()
        
    def OnSelect(self, event):
        name = self.filters_list.GetStringSelection()
        self.filter = self.filters.get(name)
        
        # can only delete filter if no other filter depends on it
        names = self.filters.names()
        names.remove(name)
        
        is_depended_on = False
        
        for filter_name in names:
            filter = self.filters.get(filter_name)
            if filter.depends_on(name):
                is_depended_on = True
        
        if not is_depended_on:
            self.removeButton.Enable(True)
            self.statusbar.SetStatusText('')
        else:
            self.removeButton.Enable(False)
            self.statusbar.SetStatusText("This filter cannot be deleted because it is used by at least one other filter.")
            
        self.editButton.Enable(True)
            
        self.ConfigureColumnTwoDisplayMode()

    def ConfigureColumnTwoDisplayMode(self):
        
        self.itemSizer.Clear(True)
        
        if self.filter is not None:

            prefixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "Name: ")
            nameLabel   = wx.StaticText(self.itemWindow, wx.ID_ANY, self.filter.name())
            
            rowSizer = wx.BoxSizer(wx.HORIZONTAL)
            rowSizer.Add(prefixLabel, border=5, flag=wx.ALL)
            rowSizer.Add(nameLabel, border=5, flag=wx.ALL)
            self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
            
            prefixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "Match")
            typeLabel   = wx.StaticText(self.itemWindow, wx.ID_ANY, self.filter.label())
            suffixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "of the following:")
            
            rowSizer = wx.BoxSizer(wx.HORIZONTAL)
            rowSizer.Add(prefixLabel, border=5, flag=wx.ALL)
            rowSizer.Add(typeLabel, border=5, flag=wx.ALL)
            rowSizer.Add(suffixLabel, border=5, flag=wx.ALL)
            self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
            
            if len(self.filter.items) > 0:
                for item in self.filter.items:
                    if type(item) == FilterItem:
                        attLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, item.key)
                        opsLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, Operations.nameForOp(item.op))
                        
                        value = None
                        if item.value is not None:
                            att_type = self.atts.get_att_type(item.key)
                            if att_type == Attributes.STRING:
                                value = str(item.value)
                            elif att_type == Attributes.BOOLEAN:
                                value = bool(item.value)
                            elif att_type == Attributes.FLOAT:
                                value = "%.2f" % item.value
                            elif att_type == Attributes.INTEGER:
                                value = "%d" % item.value
                            else:
                                raise ValueError("Unknown attribute type for key '%s'!" % item.key)
                        else:
                            value = repr(item.value)
                        
                        valLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, value)
                        
                        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
                        rowSizer.Add(attLabel, border=5, flag=wx.ALL)
                        rowSizer.Add(opsLabel, border=5, flag=wx.ALL)
                        rowSizer.Add(valLabel, border=5, flag=wx.ALL)
                        
                        self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
                    elif type(item) == FilterGroup:
                        label = wx.StaticText(self.itemWindow, wx.ID_ANY, item.description())
                        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
                        rowSizer.Add(label, border=5, flag=wx.ALL)
                        self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
                    else:
                        filterLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, item.filter.name())
                        equalsLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "==")
                        valLabel    = wx.StaticText(self.itemWindow, wx.ID_ANY, repr(item.value))
                        
                        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
                        rowSizer.Add(filterLabel, border=5, flag=wx.ALL)
                        rowSizer.Add(equalsLabel, border=5, flag=wx.ALL)
                        rowSizer.Add(valLabel, border=5, flag=wx.ALL)
                        
                        self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
            else:
                itemLabel  = wx.StaticText(self.itemWindow, wx.ID_ANY, "Selected filter has no items.")
                self.itemSizer.Add(itemLabel, border=5, flag=wx.ALL)
        else:
            itemLabel  = wx.StaticText(self.itemWindow, wx.ID_ANY, "No Filter Selected")
            self.itemSizer.Add(itemLabel, border=5, flag=wx.ALL)
        self.itemWindow.SetVirtualSize(self.itemSizer.GetMinSize())
        self.itemWindow.SetScrollRate(20,20)
        self.itemWindow.Layout()
        self.Layout()

    def ConfigureColumnTwoEditMode(self):
        view      = self.repoman.GetModel("Views").get('All')
        atts      = view.atts()
        
        self.itemSizer.Clear(True)
        
        names = self.filters.names()
        try:
            names.remove(self.edit_filter.name())
        except:
            pass

        prefixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "Name: ")
        
        width = self.itemWindow.GetTextExtent(self.edit_filter.name())[0]
        width += 25
        
        nameBox = wx.TextCtrl(self.itemWindow, wx.ID_ANY, value=self.edit_filter.name(), size=(width,-1), name="filter name")
        self.itemWindow.Bind(wx.EVT_TEXT, self.OnValueUpdate, nameBox)
        nameBox.SetFocus()
        nameBox.SetSelection(-1, -1)
        
        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowSizer.Add(prefixLabel, border=5, flag=wx.ALL)
        rowSizer.Add(nameBox, border=5, flag=wx.ALL)
        self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
        
        prefixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "Match")
        typeBox     = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=self.edit_filter.label(), choices=["All", "Any"], style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
        suffixLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "of the following:")
        
        self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnFilterTypeChange, typeBox)
        
        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowSizer.Add(prefixLabel, border=5, flag=wx.ALL)
        rowSizer.Add(typeBox, border=5, flag=wx.ALL)
        rowSizer.Add(suffixLabel, border=5, flag=wx.ALL)
        self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
        
        self.edit_items = {}
        
        if len(self.edit_filter.items) > 0:
            index = 0
            for item in self.edit_filter.items:
                self.edit_items[index] = item
                rowSizer = wx.BoxSizer(wx.HORIZONTAL)
                if type(item) == FilterItem:
                    attBox    = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=item.key, choices=atts, name="%d key" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
                    opsBox    = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=Operations.nameForOp(item.op), choices=map(lambda x: x[0], Operations.ops), name="%d op" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
                    valBox    = wx.TextCtrl(self.itemWindow, wx.ID_ANY, value=repr(item.value), name="%d" % index)
                    
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, attBox)
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, opsBox)
                    self.itemWindow.Bind(wx.EVT_TEXT, self.OnValueUpdate, valBox)

                    rowSizer.Add(attBox, border=5, flag=wx.ALL)
                    rowSizer.Add(opsBox, border=5, flag=wx.ALL)
                    rowSizer.Add(valBox, border=5, flag=wx.ALL)
                elif type(item) == FilterGroup:
                    member_of = ['IS MEMBER OF', 'IS NOT A MEMBER OF']
                    if item.isMember:
                        member_of_value = 'IS MEMBER OF'
                    else:
                        member_of_value = 'IS NOT A MEMBER OF'
                    isMemberBox = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=member_of_value, choices=member_of, name="%d member_of" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY)
                    
                    groups = self.repoman.GetModel('Groups')
                    names  = groups.names()
                    names.insert(0, 'Select Group')
                    
                    groupBox = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=item.group, choices=names, name="%d group" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
                    
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, isMemberBox)
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, groupBox)
                    
                    rowSizer.Add(isMemberBox, border=5, flag=wx.ALL)
                    rowSizer.Add(groupBox, border=5, flag=wx.ALL)
                    
                else:
                    filterBox = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=item.filter.name(), choices=names, name="%d filter" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)
                    equalsLabel = wx.StaticText(self.itemWindow, wx.ID_ANY, "==")
                    valBox = wx.ComboBox(self.itemWindow, wx.ID_ANY, value=repr(item.value), choices=["False", "True"], name="%d ffvalue" % index, style=wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SORT)

                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, filterBox)
                    self.itemWindow.Bind(wx.EVT_COMBOBOX, self.OnComboItemChange, valBox)
                
                    rowSizer.Add(filterBox, border=5, flag=wx.ALL)
                    rowSizer.Add(equalsLabel, border=5, flag=wx.ALL)
                    rowSizer.Add(valBox, border=5, flag=wx.ALL)
                    
                remButton = wx.Button(self.itemWindow, wx.ID_ANY, "Remove", name="%d" % index)
                self.itemWindow.Bind(wx.EVT_BUTTON, self.OnRemoveItem, remButton)
                
                rowSizer.Add(remButton, border=5, flag=wx.ALL)
                
                self.itemSizer.Add(rowSizer, border=5, flag=wx.ALL)
                index += 1
        else:
            itemLabel  = wx.StaticText(self.itemWindow, wx.ID_ANY, "Filter has no items. Add items with buttons below.")
            self.itemSizer.Add(itemLabel, border=5, flag=wx.ALL)

        self.itemWindow.SetVirtualSize(self.itemSizer.GetMinSize())
        self.itemWindow.SetScrollRate(20,20)
        self.itemWindow.Layout()
        self.Layout()
        
    def OnRemoveItem(self, event):
        name = event.GetEventObject().GetName()
        index = int(name)
        item = self.edit_items[index]
        self.edit_filter.remove_item(item)
        self.saveButton.Enable()
        self.ConfigureColumnTwoEditMode()
        
    def OnComboItemChange(self, event):
        name  = event.GetEventObject().GetName()
        value = event.GetEventObject().GetStringSelection()
        index, code = name.split(' ')
        index = int(index)
        item  = self.edit_items[index]
        if code == "key":
            item.key = value
        elif code == "ffvalue":
            item.value = eval(value)
        elif code == "member_of":
            if value == 'IS MEMBER OF':
                item.isMember = True
            else:
                item.isMember = False
        elif code == "group":
            item.group = value
        elif code == "op":
            item.op = Operations.opForName(value)
        elif code == "filter":
            item.filter = self.filters.get(value)
        else:
            raise ValueError("Incorrect code type in OnComboItemChange: %s" % code)
        self.saveButton.Enable()
        
    def OnValueUpdate(self, event):
        name  = event.GetEventObject().GetName()
        value = event.GetEventObject().GetValue()
        if name == "filter name":
            self.edit_filter.filter_name = value
        else:
            index = int(name)
            item = self.edit_items[index]
            try:
                item.value = eval(value)
                if not instanceof(item.value, (str, unicode, bool, float, int)):
                    item.value = str(value)
            except:
                item.value = str(value)
        self.saveButton.Enable()
        
    def OnFilterTypeChange(self, event):
        value = event.GetEventObject().GetStringSelection()
        if value == "All":
            self.edit_filter.filter = Filter.And
        else:
            self.edit_filter.filter = Filter.Or
        self.saveButton.Enable()
        
    def OnRemove(self, event):
        name = self.filters_list.GetStringSelection()
        self.filters.remove(name)
        self.filters_list.Set(self.filters.names())
        self.removeButton.Disable()
        self.editButton.Disable()
        self.filter = None
        self.repoman.RepositoryModified()
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
            self.removeButton.Disable()
            self.editButton.Disable()
            self.statusbar.SetStatusText("")
            self.ConfigureColumnTwoDisplayMode()
        event.Skip()


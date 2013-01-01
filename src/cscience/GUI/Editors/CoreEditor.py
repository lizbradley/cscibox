"""
CoreEditor.py

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
from cscience.framework import Group
from cscience.GUI.Editors import MemoryFrame

class CoreEditor(MemoryFrame):
    
    framename = 'coreeditor'

    def __init__(self, parent):
        super(CoreEditor, self).__init__(parent, id=wx.ID_ANY, title='Sample Core Editor')
        
        self.statusbar = self.CreateStatusBar()
        
        groupsLabel = wx.StaticText(self, wx.ID_ANY, "Core")
        groupLabel = wx.StaticText(self, wx.ID_ANY, "Samples in Core")
        availLabel = wx.StaticText(self, wx.ID_ANY, "Available Samples")
        
        self.groups_list = wx.ListBox(self, wx.ID_ANY, choices=sorted(datastore.sample_groups), 
                                      style=wx.LB_SINGLE)
        self.group_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE)
        self.avail = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE)

        self.addSampleButton = wx.Button(self, wx.ID_ANY, "<--   Add to Core    ---")
        self.removeSampleButton = wx.Button(self, wx.ID_ANY, "--- Remove from Core -->")
                
        self.add_button = wx.Button(self, wx.ID_ANY, "Add Core...")
        self.remove_button = wx.Button(self, wx.ID_ANY, "Delete Core")
        self.duplicateButton = wx.Button(self, wx.ID_ANY, "Duplicate Core...")

        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(groupsLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.groups_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(groupLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.group_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        
        columnThreeSizer = wx.BoxSizer(wx.VERTICAL)
        columnThreeSizer.Add(self.addSampleButton.GetSize())
        columnThreeSizer.Add(self.addSampleButton, border=5, flag=wx.ALL)
        columnThreeSizer.Add(self.addSampleButton.GetSize())
        columnThreeSizer.Add(self.removeSampleButton, border=5, flag=wx.ALL)

        columnFourSizer = wx.BoxSizer(wx.VERTICAL)
        columnFourSizer.Add(availLabel, border=5, flag=wx.ALL)
        columnFourSizer.Add(self.avail, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        
        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnTwoSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnThreeSizer, flag=wx.ALIGN_CENTER_VERTICAL)
        columnSizer.Add(columnFourSizer, proportion=1, flag=wx.EXPAND)
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.add_button, border=5, flag=wx.ALL)
        buttonSizer.Add(self.remove_button, border=5, flag=wx.ALL)
        buttonSizer.Add(self.duplicateButton, border=5, flag=wx.ALL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.ALIGN_LEFT)
        
        self.SetSizer(sizer)
        
        self.remove_button.Disable()
        self.duplicateButton.Disable()
        self.addSampleButton.Disable()
        self.removeSampleButton.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.add_core, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.delete_core, self.remove_button)
        self.Bind(wx.EVT_BUTTON, self.OnDuplicate, self.duplicateButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddSample, self.addSampleButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveSample, self.removeSampleButton)

        self.Bind(wx.EVT_LISTBOX, self.select_core, self.groups_list)

    def select_core(self, event):
        name = self.groups_list.GetStringSelection()
        self.group = datastore.sample_groups[name]
        
        status, message = self.GroupInUse(self.group.name)
        self.remove_button.Enable(not status)
        self.addSampleButton.Enable(not status)
        self.removeSampleButton.Enable(not status)
        self.statusbar.SetStatusText('Cannot Alter Core "%s": %s' % 
                            (self.group.name, message) if status else message)
        
        self.duplicateButton.Enable()
        self.InitGroupLists()
        
    def GroupInUse(self, group):
        return (False, "")

    def add_core(self, event):
        dialog = wx.TextEntryDialog(self, "Enter Core Name", "Create Core", style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value:
                if value not in datastore.sample_groups:
                    datastore.sample_groups.add(Group(value))
                    self.groups_list.Set(sorted(datastore.sample_groups))
                    self.ClearGroupLists()
                    self.remove_button.Disable()
                    self.duplicateButton.Disable()
                    datastore.data_modified = True
                    self.statusbar.SetStatusText("")
                else:
                    dialog = wx.MessageDialog(None, 'Group "' + value + '" already exists!', "Duplicate Group", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Group name not specified!', "Illegal Group Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()

    def OnAddSample(self, event):
        for item in self.avail.Selections:
            self.group.add(self.avail.GetString(item))
        self.InitGroupLists()
        datastore.data_modified = True

    def delete_core(self, event):
        name = self.groups_list.GetStringSelection()
        del datastore.sample_groups[name]
        self.groups_list.Set(sorted(self.groups))
        self.ClearGroupLists()
        self.remove_button.Disable()
        self.duplicateButton.Disable()
        datastore.data_modified = True

    def OnRemoveSample(self, event):
        for item in self.group_list.Selections:
            del self.group[self.group_list.GetString(item)]
        self.InitGroupLists()
        datastore.data_modified = True

    def OnDuplicate(self, event):
        name = self.groups_list.GetStringSelection()

        dialog = wx.TextEntryDialog(self, "Name for New Core", "Copy Current Core", 
                                    style=wx.OK | wx.CANCEL)
        dialog.SetValue("Copy of %s" % name)
        
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value:
                if value not in datastore.sample_groups:
                    
                    old_group = datastore.sample_groups[name]
                    new_group = old_group.copy()
                    new_group.name = value
                    
                    datastore.sample_groups.add(new_group)
                    self.groups_list.Set(sorted(datastore.sample_groups))
                    self.ClearGroupLists()
                    self.remove_button.Disable()
                    self.duplicateButton.Disable()
                    datastore.data_modified = True
                    self.statusbar.SetStatusText("")
                else:
                    dialog = wx.MessageDialog(None, 'Group "' + value + '" already exists!', "Duplicate Group", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Group name not specified!', "Illegal Group Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()

    def ClearGroupLists(self):
        self.group_list.Clear()
        self.avail.Clear()
        self.addSampleButton.Disable()
        self.removeSampleButton.Disable()
        
    def InitGroupLists(self):
        self.ClearGroupLists()
        self.group_list.Set([str(i) for i in self.group])
        
        if self.group:
            self.group_list.SetFirstItem(0)

        avail = [str(s_id) for s_id in datastore.sample_db if s_id not in self.group]
        avail.sort()
        self.avail.Set(avail)
            
        
    def UpdateGroup(self, name):
        if name == self.groups_list.GetStringSelection():
            self.ClearGroupLists()
            self.InitGroupLists()

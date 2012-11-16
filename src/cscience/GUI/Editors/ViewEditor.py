"""
ViewEditor.py

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

from cscience.GUI import events
from cscience import datastore
from cscience.framework import View
from cscience.GUI.Editors import MemoryFrame

class ViewEditor(MemoryFrame):
    framename = 'vieweditor'

    def __init__(self, parent):
        super(ViewEditor, self).__init__(parent, id=wx.ID_ANY, 
                                         title='Sample View Editor')
        
        self.statusbar = self.CreateStatusBar()
        
        viewsLabel = wx.StaticText(self, wx.ID_ANY, "Views")
        viewLabel = wx.StaticText(self, wx.ID_ANY, "Attributes in View")
        availLabel = wx.StaticText(self, wx.ID_ANY, "Available Attributes")
        
        self.views_list = wx.ListBox(self, wx.ID_ANY, choices=sorted(datastore.views.keys()), 
                                     style=wx.LB_SINGLE)
        self.view_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_EXTENDED)
        self.avail = wx.ListBox(self, wx.ID_ANY, style=wx.LB_EXTENDED)

        self.addAttButton = wx.Button(self, wx.ID_ANY, "<--  Add   ---")
        self.removeAttButton = wx.Button(self, wx.ID_ANY, "--- Remove -->")
        
        self.add_button = wx.Button(self, wx.ID_ANY, "Add View...")
        self.remove_button = wx.Button(self, wx.ID_ANY, "Delete View")

        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(viewsLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.views_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(viewLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.view_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        
        columnThreeSizer = wx.BoxSizer(wx.VERTICAL)
        columnThreeSizer.Add(self.addAttButton.GetSize())
        columnThreeSizer.Add(self.addAttButton, border=5, flag=wx.ALL)
        columnThreeSizer.Add(self.addAttButton.GetSize())
        columnThreeSizer.Add(self.removeAttButton, border=5, flag=wx.ALL)

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
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizer(sizer)

        self.remove_button.Disable()
        self.addAttButton.Disable()
        self.removeAttButton.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.add_view, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove_button)
        self.Bind(wx.EVT_BUTTON, self.OnAddAtt, self.addAttButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveAtt, self.removeAttButton)
        
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.views_list)
        self.Bind(wx.EVT_LISTBOX, self.OnViewSelect, self.view_list)
        self.Bind(wx.EVT_LISTBOX, self.OnAttSelect, self.avail)
        
    def add_view(self, event):
        dialog = wx.TextEntryDialog(self, "Enter View Name", "View Entry Dialog", 
                                    style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value:
                if not value in datastore.views:
                    datastore.views.add(View(value))
                    self.views_list.Set(sorted(datastore.views.keys()))
                    self.ClearAttLists()
                    self.remove_button.Disable()
                    self.statusbar.SetStatusText("")
                    events.post_change(self, 'views')
                else:
                    dialog = wx.MessageDialog(None, 'View "' + value + '" already exists!', "Duplicate View", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'View name not specified!', "Illegal View Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()
        
    def OnAddAtt(self, event):
        strs = self.avail.GetStrings()
        for sel in self.avail.GetSelections():
            self.view.append(strs[sel])
        self.InitAttLists()
        events.post_change(self, 'view_atts')
    
    def OnSelect(self, event):
        name = self.views_list.GetStringSelection()
        self.view = datastore.views[name]
        if name != "All":
            self.remove_button.Enable(True)
            self.statusbar.SetStatusText("View: %s" % name)
        else:
            self.remove_button.Enable(False)
            self.statusbar.SetStatusText("The 'All' View cannot be modified.")
        self.InitAttLists()
        
    def OnAttSelect(self, event):
        self.addAttButton.Enable(True)
        self.removeAttButton.Disable()
        self.view_list.DeselectAll()

    def OnViewSelect(self, event):
        self.addAttButton.Disable()
        self.removeAttButton.Enable(self.views_list.GetStringSelection() != "All")
        self.avail.DeselectAll()
    
    def OnRemove(self, event):
        name = self.views_list.GetStringSelection()
        del datastore.views[name]
        self.views_list.Set(sorted(datastore.views.keys()))
        self.ClearAttLists()
        self.remove_button.Disable()
        events.post_change(self, 'views')

    def OnRemoveAtt(self, event):
        strs = self.view_list.GetStrings()
        for sel in self.view_list.GetSelections():
            self.view.remove(strs[sel])
        self.InitAttLists()
        events.post_change(self, 'view_atts')

    def ClearAttLists(self):
        self.view_list.Clear()
        self.avail.Clear()
        self.addAttButton.Disable()
        self.removeAttButton.Disable()
        
    def InitAttLists(self):
        self.ClearAttLists()        
        #need this to make new views show up w/ forced attributes; sort of a
        #pain but wevs.
        self.view_list.Set([att_name for att_name in self.view])
        
        avail = [att.name for att in datastore.sample_attributes if att not in self.view]
        self.avail.Set(avail)
        
    def UpdateView(self, name):
        if name == self.views_list.GetStringSelection():
            self.ClearAttLists()
            self.InitAttLists()
        events.post_change(self, 'views')

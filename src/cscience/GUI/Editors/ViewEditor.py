"""
ViewEditor.py

* Copyright (c) 2006-2013, University of Colorado.
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
import wx.gizmos as gizmos

from cscience.GUI import events
from cscience import datastore
from cscience.framework import View
from cscience.GUI.Editors import MemoryFrame

datastore = datastore.Datastore()

class ViewEditor(MemoryFrame):
    framename = 'vieweditor'
    
    def __init__(self, parent):
        super(ViewEditor, self).__init__(parent, id=wx.ID_ANY,
                                         title='Sample View Editor')
        
        self.SetBackgroundColour(wx.Colour(215,215,215))
        self.vattpanel = VirtualAttPanel(self)
        self.viewpanel = ViewPanel(self)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.vattpanel, proportion=1, flag=wx.EXPAND)
        sz.Add(self.viewpanel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sz)


class VirtualAttPanel(wx.Panel):    
    def __init__(self, parent):
        super(VirtualAttPanel, self).__init__(parent, id=wx.ID_ANY)
        
        self.vatts_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SINGLE,
                                     choices=datastore.sample_attributes.virtual_atts())
        self.vattlabel = wx.StaticText(self, wx.ID_ANY, "<No Attribute Selected>")
        self.avail_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_EXTENDED)
        
        self.order_box = gizmos.EditableListBox(self, wx.ID_ANY,
                'Composes Attributes:', style=gizmos.EL_ALLOW_DELETE)
        
        self.add_att_button = wx.Button(self, wx.ID_ANY, "<--    Add    ---")
        self.add_button = wx.Button(self, wx.ID_ANY, "Add Composite Attribute...")
        self.save_button = wx.Button(self, wx.ID_ANY, "Save Composition")
        self.add_att_button.Disable()
        self.order_box.Disable()
        
        colsizer = wx.BoxSizer(wx.HORIZONTAL)
        sz =  wx.BoxSizer(wx.VERTICAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Composite Attributes"), border=5, flag=wx.ALL)
        sz.Add(self.vatts_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.vattlabel, border=5, flag=wx.ALL)
        sz.Add(self.order_box, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        sz.Add(self.save_button, border=5, flag=wx.ALL)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.add_att_button.GetSize())
        sz.Add(self.add_att_button, border=5, flag=wx.ALL)
        sz.Add(self.add_att_button.GetSize())
        colsizer.Add(sz, flag=wx.ALIGN_CENTER_VERTICAL)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Available Attributes"), border=5, flag=wx.ALL)
        sz.Add(self.avail_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.add_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(buttonsizer, border=5, flag=wx.ALL | wx.ALIGN_LEFT)
        sizer.Add(colsizer, proportion=1, flag=wx.EXPAND)
        
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.add_vatt, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.add_attribute, self.add_att_button)
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.remove_attribute, self.order_box.GetListCtrl())
        self.Bind(wx.EVT_BUTTON, self.save_changes, self.save_button)

        self.Bind(wx.EVT_LISTBOX, self.select_vatt, self.vatts_list)
        
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        
    def select_vatt(self, event=None):
        name = self.vatts_list.GetStringSelection()
        self.vatt = datastore.sample_attributes[name]
        self.vattlabel.SetLabel('"%s" Composes' % name)
        
        self.order_box.Strings = self.vatt.aggatts
        avail = [att.name for att in datastore.sample_attributes
                 if att not in self.vatt.aggatts and att.name != self.vatt.name]
        self.avail_list.Set(avail)
        self.add_att_button.Enable()
        
    def save_changes(self, event=None):
        self.vatt.aggatts = self.order_box.Strings
        events.post_change(self, 'attributes', self.vatt.name)
        
    def add_vatt(self, event):
        dialog = wx.TextEntryDialog(self, "Enter Attribute Name", "New Composite Attribute",
                                    style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            dialog.Destroy()
            if value:
                if not value in datastore.sample_attributes:
                    datastore.sample_attributes.add_virtual_att(value, [])
                    events.post_change(self, 'attributes', value)
                else:
                    wx.MessageBox('Attribute "%s" already exists!' % value,
                            "Duplicate Attribute Name", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('Attribute name not specified!',
                            "Illegal Attribute Name", wx.OK | wx.ICON_INFORMATION)
        
    def add_attribute(self, event):
        strs = self.avail_list.GetStrings()
        selected = self.avail_list.GetSelections()
        order = self.order_box.Strings
        for sel in selected:
            order.append(strs[sel])
        self.order_box.Strings = order
            
        #barf. There has to be a cleaner way to do this, but my brain is le tired.
        self.avail_list.SetItems([st for (index, st) in enumerate(strs) 
                                  if index not in selected])
        self.avail_list.DeselectAll()
        
    def remove_attribute(self, event):
        self.avail_list.Append(event.Item.Text)
        
    def on_repository_altered(self, event):
        if 'attributes' in event.changed:
            self.vatts_list.Set(datastore.sample_attributes.virtual_atts())
            if event.value:
                try:
                    new_index = self.vatts_list.GetItems().index(event.value)
                except ValueError:
                    pass
                else:
                    #bah, there's no good way to make this fire an event
                    self.vatts_list.SetSelection(new_index)
                    self.select_vatt()
                    return
            #self.update_avail()
        event.Skip()
        
        
class ViewPanel(wx.Panel):
    def __init__(self, parent):
        super(ViewPanel, self).__init__(parent, id=wx.ID_ANY)
        
        self.views_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SINGLE,
                                     choices=sorted(datastore.views.keys()))
        self.viewlabel = wx.StaticText(self, wx.ID_ANY, "<No View Selected>")
        self.view_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_EXTENDED)
        self.avail_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_EXTENDED)

        #TODO: use an ItemsPicker!
        #kinda gross hack to make these buttons the same size
        self.add_att_button = wx.Button(self, wx.ID_ANY, "<--    Add    ---")
        self.remove_att_button = wx.Button(self, wx.ID_ANY, "--- Remove -->")
        self.add_button = wx.Button(self, wx.ID_ANY, "Add View...")
        self.add_att_button.Disable()
        self.remove_att_button.Disable()

        colsizer = wx.BoxSizer(wx.HORIZONTAL)
        sz =  wx.BoxSizer(wx.VERTICAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Views"), border=5, flag=wx.ALL)
        sz.Add(self.views_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.viewlabel, border=5, flag=wx.ALL)
        sz.Add(self.view_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.add_att_button.GetSize())
        sz.Add(self.add_att_button, border=5, flag=wx.ALL)
        sz.Add(self.add_att_button.GetSize())
        sz.Add(self.remove_att_button, border=5, flag=wx.ALL)
        colsizer.Add(sz, flag=wx.ALIGN_CENTER_VERTICAL)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Available Attributes"), border=5, flag=wx.ALL)
        sz.Add(self.avail_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        colsizer.Add(sz, proportion=1, flag=wx.EXPAND)

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.add_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(buttonsizer, border=5, flag=wx.ALL | wx.ALIGN_LEFT)
        sizer.Add(colsizer, proportion=1, flag=wx.EXPAND)
        
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.add_view, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.add_attribute, self.add_att_button)
        self.Bind(wx.EVT_BUTTON, self.remove_attribute, self.remove_att_button)

        self.Bind(wx.EVT_LISTBOX, self.select_view, self.views_list)
        self.Bind(wx.EVT_LISTBOX, self.select_for_remove, self.view_list)
        self.Bind(wx.EVT_LISTBOX, self.select_for_add, self.avail_list)
        
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)

    def on_repository_altered(self, event):
        if 'views' in event.changed:
            self.views_list.Set(sorted(datastore.views.keys()))
            if event.value:
                try:
                    new_index = self.views_list.GetItems().index(event.value)
                except ValueError:
                    pass
                else:
                    #bah, there's no good way to make this fire an event
                    self.views_list.SetSelection(new_index)
                    self.select_view()
        elif 'view_atts' in event.changed and self.view.name == event.value:
            self.show_att_lists()
        event.Skip()

    def add_view(self, event):
        dialog = wx.TextEntryDialog(self, "Enter View Name", "New View",
                                    style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            dialog.Destroy()
            if value:
                if not value in datastore.views:
                    datastore.views.add(View(value))
                    self.clear_view()
                    events.post_change(self, 'views', value)
                else:
                    wx.MessageBox('View "%s" already exists!' % value,
                            "Duplicate View Name", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('View name not specified!',
                            "Illegal View Name", wx.OK | wx.ICON_INFORMATION)

    def add_attribute(self, event):
        strs = self.avail_list.GetStrings()
        for sel in self.avail_list.GetSelections():
            self.view.append(strs[sel])
        events.post_change(self, 'view_atts', self.view.name)

    def select_view(self, event=None):
        name = self.views_list.GetStringSelection()
        self.view = datastore.views[name]
        self.viewlabel.SetLabel('Attributes in "%s"' % name)
        self.show_att_lists()

    def select_for_add(self, event):
        self.add_att_button.Enable(True)
        self.remove_att_button.Disable()
        self.view_list.DeselectAll()

    def select_for_remove(self, event):
        self.add_att_button.Disable()
        self.remove_att_button.Enable(self.views_list.GetStringSelection() != "All")
        self.avail_list.DeselectAll()

    def remove_attribute(self, event):
        strs = self.view_list.GetStrings()
        for sel in self.view_list.GetSelections():
            try:
                self.view.remove(strs[sel])
            except ValueError:
                pass
                #self.statusbar.SetStatusText('Cannot remove attribute(s): '
                #                'some attributes are required in all views.')
        events.post_change(self, 'view_atts', self.view.name)

    def clear_view(self):
        self.viewlabel.SetLabel("<No View Selected>")
        self.view_list.Clear()
        self.avail_list.Clear()
        self.add_att_button.Disable()
        self.remove_att_button.Disable()

    def show_att_lists(self):
        self.add_att_button.Disable()
        self.remove_att_button.Disable()
        self.view_list.Set(self.view)
        avail = [att.name for att in datastore.sample_attributes
                 if att not in self.view]
        self.avail_list.Set(avail)

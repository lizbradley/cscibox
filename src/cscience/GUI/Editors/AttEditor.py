"""
AttEditor.py

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
from cscience.framework import Attribute
from cscience.GUI import dialogs, events
from cscience.GUI.Editors import MemoryFrame

AddAttribute = dialogs.field_dialog('Attribute', 'Output')

class AttributeListCtrl(wx.ListCtrl):
    cols = ['name', 'type_', 'output']
    labels = ['Attribute', 'Type', 'Output?']
    
    def __init__(self, *args, **kwargs):
        if 'style' in kwargs:
            style = kwargs['style']
        else:
            style = 0
        kwargs['style'] = style | wx.LC_REPORT | wx.LC_VIRTUAL | \
                                wx.LC_SINGLE_SEL
        
        super(AttributeListCtrl, self).__init__(*args, **kwargs)
        self.InsertColumn(0, 'Attribute')
        self.InsertColumn(1, 'Type')
        self.InsertColumn(2, 'Output?', format=wx.LIST_FORMAT_CENTER)
            
        self.whiteback = wx.ListItemAttr()
        self.whiteback.SetBackgroundColour('white')
        self.blueback = wx.ListItemAttr()
        self.blueback.SetBackgroundColour('light blue')
        #TODO: this would look nicer with a larger font size
        self.refresh_view()
            
    def refresh_view(self):
        self.SetItemCount(len(datastore.sample_attributes))
        maxext = max(80, max([self.GetTextExtent(name)[0] 
                      for name in datastore.sample_attributes.keys()]))
        self.SetColumnWidth(0, maxext)
        self.Refresh()
        
    def OnGetItemAttr(self, item):
        return item % 2 and self.blueback or self.whiteback
    def OnGetItemText(self, row, col):
        att = datastore.sample_attributes.byindex(row)
        if col == 2:
            return att.output and unichr(10003) or ''
        return getattr(att, self.cols[col])    
    
class AttEditor(MemoryFrame):
    
    framename = 'atteditor'

    def __init__(self, parent):
        super(AttEditor, self).__init__(parent, id=wx.ID_ANY, title='Attribute Editor')
        
        self.statusbar = self.CreateStatusBar()          
        self.listctrl = AttributeListCtrl(self, wx.ID_ANY)
        self.add_button = wx.Button(self, wx.ID_ANY, "Add Attribute...")
        self.edit_button = wx.Button(self, wx.ID_ANY, "Edit Attribute...")
        self.remove_button = wx.Button(self, wx.ID_ANY, "Remove Attribute")

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.add_button, border=5, flag=wx.ALL)
        buttonsizer.Add(self.edit_button, border=5, flag=wx.ALL)
        buttonsizer.Add(self.remove_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Attribute Names"), 
                  border=10, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT)
        sizer.Add(self.listctrl, border=10, flag=wx.EXPAND | wx.ALL, proportion=1)
        sizer.Add(buttonsizer, border=10, flag=wx.ALIGN_CENTER | wx.BOTTOM)

        self.SetSizer(sizer)
                        
        self.edit_button.Disable()
        self.remove_button.Disable()
        self.Bind(wx.EVT_BUTTON, self.add_attribute, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.edit_attribute, self.edit_button)
        self.Bind(wx.EVT_BUTTON, self.delete_attribute, self.remove_button)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_attribute, self.listctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.select_attribute, self.listctrl)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        
    def update_attribute(self, att_name='', att_type='', 
                         is_output=False, in_use=False, previous_att=None):
        dlg = AddAttribute(self, att_name, att_type, is_output, in_use)
        if dlg.ShowModal() == wx.ID_OK:
            if not dlg.field_name:
                return
            if dlg.field_name not in datastore.sample_attributes or dlg.field_name == previous_att:
                if previous_att:
                    del datastore.sample_attributes[previous_att]
                    
                datastore.sample_attributes.add(Attribute(dlg.field_name, 
                                            dlg.field_type, dlg.is_output))
                events.post_change(self, 'attributes')
                self.listctrl.Select(self.listctrl.GetFirstSelected(), False)
                
                row = datastore.sample_attributes.indexof(dlg.field_name)
                #self.grid.MakeCellVisible(row, 0)    
                
            else:
                wx.MessageBox('Attribute "%s" already exists!' % dlg.field_name, 
                        "Duplicate Attribute", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()
        
    def on_repository_altered(self, event):
        if 'attributes' in event.changed:
            self.listctrl.refresh_view()
        event.Skip()

    def add_attribute(self, event=None):
        self.update_attribute()
        
    def edit_attribute(self, event):        
        att = datastore.sample_attributes.byindex(self.listctrl.GetFirstSelected())
        self.update_attribute(att.name, att.type_, att.output, 
                              bool(att.in_use), att.name)

    def select_attribute(self, event):
        row = self.listctrl.GetFirstSelected()
        if row != -1:
            att = datastore.sample_attributes.byindex(row)
            self.edit_button.Enable()
            message = att.in_use
            if message:
                message = ' '.join(('Attribute in use:', message))
            self.remove_button.Enable(not bool(message))
            self.statusbar.SetStatusText(message)
        else:
            self.edit_button.Disable()
            self.remove_button.Disable()
            self.statusbar.SetStatusText('')

    def delete_attribute(self, event):
        row = self.listctrl.GetFirstSelected()
        att = datastore.sample_attributes.getkeyat(row)
        self.listctrl.Select(row, False)
        del datastore.sample_attributes[att]
        events.post_change(self, 'attributes')
        
        
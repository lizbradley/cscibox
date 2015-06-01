"""
TemplateEditor.py

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

from cscience import datastore
from cscience.framework import Template
from cscience.GUI import dialogs, events
from cscience.GUI.Editors import MemoryFrame

datastore = datastore.Datastore()

EditTemplateField = dialogs.field_dialog('Template Field', 'Key')

class TemplateListCtrl(wx.ListCtrl):
    cols = ['name', 'field_type', 'iskey']
    labels = ['Name', 'Type', 'Is Key?']

    def __init__(self, *args, **kwargs):
        self._template = None
        if 'style' in kwargs:
            style = kwargs['style']
        else:
            style = 0
        kwargs['style'] = style | wx.LC_REPORT | wx.LC_VIRTUAL | \
                                wx.LC_SINGLE_SEL

        super(TemplateListCtrl, self).__init__(*args, **kwargs)
        self.InsertColumn(0, self.labels[0])
        self.InsertColumn(1, self.labels[1])
        self.InsertColumn(2, self.labels[2], format=wx.LIST_FORMAT_CENTER)

        font = self.GetFont()
        font.SetPointSize(14)
        self.SetFont(font)

        self.whiteback = wx.ListItemAttr()
        self.whiteback.SetBackgroundColour('white')
        self.blueback = wx.ListItemAttr()
        self.blueback.SetBackgroundColour('light blue')

        self.refresh_view()

    @property
    def template(self):
        return self._template
    @template.setter
    def template(self, value):
        self._template = value
        self.Select(self.GetFirstSelected(), False)
        self.refresh_view()

    def refresh_view(self):
        if not self.template:
            self.SetItemCount(1)
            self.SetColumnWidth(0, 200)
            self.Enable(False)
        else:
            self.SetItemCount(len(self.template))

            #fudge for border and spacing
            maxext = max(80, max([self.GetTextExtent(name)[0] + 15
                      for name in self.template.keys()]))
            self.SetColumnWidth(0, maxext)
            self.Enable(True)
        self.Refresh()

    def OnGetItemAttr(self, item):
        return item % 2 and self.blueback or self.whiteback
    def OnGetItemText(self, row, col):
        if not self.template:
            if col == 0:
                if self.template is None:
                    return "Please select a template"
                else:
                    return "This template has no fields"
            else:
                return ''
        field = self.template.values()[row]
        if col == 2:
            return field.iskey and unichr(10003) or ''
        return getattr(field, self.cols[col])

class TemplateEditor(MemoryFrame):

    framename = 'templateeditor'

    def __init__(self, parent):
        super(TemplateEditor, self).__init__(parent, id=wx.ID_ANY,
                                             title='Paleobase Template Editor')
        self.SetBackgroundColour(wx.Colour(215,215,215))
        self.template = None

        self.statusbar = self.CreateStatusBar()
        self.template_label = wx.StaticText(self, wx.ID_ANY, "Template")

        self.templates_list = wx.ListBox(self, wx.ID_ANY,
                                         choices=sorted(datastore.templates),
                                         style=wx.LB_SINGLE)
        self.add_button = wx.Button(self, wx.ID_ANY, "Add Template...")

        self.fieldlist = TemplateListCtrl(self, wx.ID_ANY)
        self.addfieldbutton = wx.Button(self, wx.ID_ANY, "Add Field...")
        self.editfieldbutton = wx.Button(self, wx.ID_ANY, "Edit Field...")
        self.deletefieldbutton = wx.Button(self, wx.ID_ANY, "Delete Field")
        self.addfieldbutton.Disable()
        self.editfieldbutton.Disable()
        self.deletefieldbutton.Disable()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Templates"), border=5, flag=wx.ALL)
        sz.Add(self.templates_list, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(self.add_button, border=5, flag=wx.ALL)
        sz.Add(bsz, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(sz, proportion=1, flag=wx.EXPAND)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.template_label, border=5, flag=wx.ALL)
        sz.Add(self.fieldlist, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(self.addfieldbutton, border=5, flag=wx.ALL)
        bsz.Add(self.editfieldbutton, border=5, flag=wx.ALL)
        bsz.Add(self.deletefieldbutton, border=5, flag=wx.ALL)
        sz.Add(bsz, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(sz, proportion=2, flag=wx.EXPAND)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.add_template, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.add_template_field, self.addfieldbutton)
        self.Bind(wx.EVT_BUTTON, self.edit_template_field, self.editfieldbutton)
        self.Bind(wx.EVT_BUTTON, self.delete_template_field, self.deletefieldbutton)
        self.Bind(wx.EVT_LISTBOX, self.select_template, self.templates_list)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)

    def on_repository_altered(self, event):
        if 'templates' in event.changed:
            self.templates_list.Set(sorted(datastore.templates.keys()))
            self.addfieldbutton.Disable()
            if event.value:
                try:
                    new_index = self.templates_list.GetItems().index(event.value)
                except ValueError:
                    pass
                else:
                    #bah, there's no good way to make this fire an event
                    self.templates_list.SetSelection(new_index)
                    self.select_template()
        elif 'template_fields' in event.changed and self.template.name == event.value:
            self.fieldlist.refresh_view()
        event.Skip()

    def add_template(self, event):
        dialog = wx.TextEntryDialog(self, "Enter Template Name",
                                    "Template Entry Dialog", style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value:
                if value not in datastore.templates:
                    template = Template(name=value)
                    datastore.templates.add(template)
                    events.post_change(self, 'templates', value)
                else:
                    dialog = wx.MessageDialog(None, 'Template "' + value + '" already exists!', "Duplicate Template", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Template name not specified!', "Illegal Template Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()

    def select_template(self, event=None):
        #TODO: this isn't working for Paul or Liz; I suspect there is a wxPython
        #version issue going on. Would rather fix as part of 3.0 upgrade...
        name = self.templates_list.GetStringSelection()
        self.template = datastore.templates[name]
        self.fieldlist.template = self.template
        self.template_label.SetLabel('Fields for Template: %s' % name)

        self.deletefieldbutton.Enable(False)
        self.editfieldbutton.Enable(False)

        self.addfieldbutton.Enable()

    def update_template_field(self, prev_name='', prev_type='', prev_key=False):
        dlg = EditTemplateField(self, prev_name, prev_type, prev_key)
        if dlg.ShowModal() == wx.ID_OK:
            if prev_name:
                del self.template[prev_name]
            self.template.add_field(dlg.field_name, dlg.field_type, dlg.is_key)
            events.post_change(self, 'template_fields', self.template.name)
        dlg.Destroy()

    def add_template_field(self, event):
        self.update_template_field()

    def edit_template_field(self, event):
        field = self.template.getitemat(self.fieldlist.GetFirstSelected())
        self.update_template_field(field.name, field.field_type, field.iskey)

    def delete_template_field(self, event):
        field = self.template.getitemat(self.fieldlist.GetFirstSelected())
        del self.template[field.name]
        events.post_change(self, 'template_fields', self.template.name)
        self.editfieldbutton.Disable()
        self.deletefieldbutton.Disable()


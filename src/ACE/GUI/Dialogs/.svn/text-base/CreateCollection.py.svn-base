"""
CreateCollection.py

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

class CreateCollection(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'Create Collection', size=(600, 300) )
        
        self.templates = parent.repoman.GetModel("Templates")

        self.panel = wx.Panel(self, -1)

        nameLabel  = wx.StaticText(self.panel, wx.ID_ANY, "Collection Name")
        typeLabel  = wx.StaticText(self.panel, wx.ID_ANY, "Based On")
        pathLabel  = wx.StaticText(self.panel, wx.ID_ANY, "Path to CSV File")

        self.nameBox   = wx.TextCtrl(self.panel, wx.ID_ANY, size=(150,-1))
        self.typeBox   = wx.ComboBox(self.panel, wx.ID_ANY, value=self.templates.names()[0], choices=self.templates.names(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.pathBox   = wx.TextCtrl(self.panel, wx.ID_ANY, size=(150,-1))

        self.browse_button = wx.Button(self.panel, wx.ID_ANY, "Browse")
        ok_button     = wx.Button(self.panel, wx.ID_OK, "Ok")
        cancel_button = wx.Button(self.panel, wx.ID_CANCEL, "Cancel")

        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(nameLabel, pos=(0,0), border=10, flag=wx.ALIGN_RIGHT|wx.ALL)
        sizer.Add(typeLabel, pos=(1,0), border=10, flag=wx.ALIGN_RIGHT|wx.ALL)
        sizer.Add(pathLabel, pos=(2,0), border=10, flag=wx.ALIGN_RIGHT|wx.ALL)
        sizer.Add(self.nameBox, pos=(0,1), border=10, flag=wx.EXPAND|wx.ALL)
        sizer.Add(self.typeBox, pos=(1,1), border=10, flag=wx.ALIGN_LEFT|wx.ALL)
        sizer.Add(self.pathBox, pos=(2,1), border=10, flag=wx.EXPAND|wx.ALL)
        sizer.Add(self.browse_button, pos=(2,2), border=10, flag=wx.ALIGN_LEFT|wx.ALL)
        sizer.Add(cancel_button,  pos=(3,1), border=10, flag=wx.ALIGN_RIGHT|wx.ALL)
        sizer.Add(ok_button,  pos=(3,2), border=10, flag=wx.ALIGN_CENTER|wx.ALL)

        sizer.AddGrowableCol(1)

        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse_button)

        self.panel.Layout()
        self.Layout()
        
    def OnBrowse(self, event):
        dialog = wx.FileDialog(None, "Select a CSV File that contains data for this collection", style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        path   = dialog.GetPath()
        dialog.Destroy()
        if result == wx.ID_OK:
            self.pathBox.SetValue(path)

    def get_name(self):
        return self.nameBox.GetValue()
    
    def get_template(self):
        return self.typeBox.GetValue()
        
    def get_path(self):
        return self.pathBox.GetValue()
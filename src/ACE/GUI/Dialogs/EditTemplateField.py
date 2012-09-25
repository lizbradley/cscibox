"""
EditTemplateField.py

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

class EditTemplateField(wx.Dialog):
    def __init__(self, parent, name, field_type, iskey):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Add/Edit Template Field')
        
        if field_type == "":
            field_type = "Float"

        nameLabel = wx.StaticText(self, wx.ID_ANY, "Name")
        typeLabel = wx.StaticText(self, wx.ID_ANY, "Value")
        isKeyLabel = wx.StaticText(self, wx.ID_ANY, "Is Key?")

        self.name_box = wx.TextCtrl(self, wx.ID_ANY, name, size=(150, -1))
        self.type_box = wx.ComboBox(self, wx.ID_ANY, value=field_type, choices=["String", "Integer", "Float"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.isKeyBox = wx.CheckBox(self, wx.ID_ANY)
        self.isKeyBox.SetValue(iskey)

        ok_button = wx.Button(self, wx.ID_OK, "Ok")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")

        sizer = wx.GridBagSizer(10, 10)
        sizer.Add(nameLabel, pos=(0, 0), border=5, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
        sizer.Add(typeLabel, pos=(0, 1), border=5, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
        sizer.Add(isKeyLabel, pos=(0, 2), border=5, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)
        sizer.Add(self.name_box, pos=(1, 0), border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.type_box, pos=(1, 1), border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.isKeyBox, pos=(1, 2), border=5, flag=wx.ALIGN_CENTER | wx.ALL)
        sizer.Add(cancel_button, pos=(2, 1), border=5, flag=wx.ALIGN_CENTER | wx.ALL)
        sizer.Add(ok_button, pos=(2, 2), border=5, flag=wx.ALIGN_CENTER | wx.ALL)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Centre(wx.BOTH)
        

    def get_name(self):
        return self.name_box.GetValue()
    
    def get_type(self):
        return self.type_box.GetValue()
        
    def get_iskey(self):
        return self.isKeyBox.GetValue()

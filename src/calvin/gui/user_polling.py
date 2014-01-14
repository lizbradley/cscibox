"""
user_polling.py

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

This module contains stuff to poll the user when I encounter a field I wanted
and don't yet seem to have.
"""

import wx

def result_query(arg):
    dialog = ResultQuery(arg)
    result = None
    if dialog.ShowModal() == wx.ID_OK:
        result = dialog.result
    dialog.Destroy()
    return result

class BooleanInput(wx.RadioBox):
    
    def __init__(self, parent):
        super(BooleanInput, self).__init__(parent, wx.ID_ANY, label="", 
                                           choices=['Yes', 'No'])
        
    def get_value(self):
        #not, since we have No in the 1 position
        return not self.GetSelection()
    
class NumericInput(wx.TextCtrl):
    
    def __init__(self, parent):
        super(NumericInput, self).__init__(parent, wx.ID_ANY)
        
        self.SetValue('0')
        self.SetSelection(-1, -1)
        
        self.Bind(wx.EVT_KILL_FOCUS, self.check_input)
        self.Bind(wx.EVT_SET_FOCUS, self.highlight)
        
    def check_input(self, event):
        try:
            float(self.GetValue())
        except ValueError:
            self.SetValue('0')
            self.SetBackgroundColour('red')
            self.SetSelection(-1, -1)
        else:
            self.SetBackgroundColour('white')
        
        event.Skip()
        
    def highlight(self, event):
        #wait till all selections are actually finshed, then select
        wx.CallAfter(self.SetSelection, -1, -1)
        event.Skip()
        
    def get_value(self):
        return float(self.GetValue())
    
class LabelledInput(wx.Panel):
    
    control_types = {bool: BooleanInput, float: NumericInput}
    
    def __init__(self, parent, label, input_type):
        super(LabelledInput, self).__init__(parent)
        
        self.control = self.control_types[input_type](self)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=label), flag=wx.ALL, border=2)
        sizer.Add(self.control, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
        self.SetSizer(sizer)
        
    def get_value(self):
        return self.control.get_value()
    

class PollingDialog(wx.Dialog):
    
    def __init__(self, caption):
        super(PollingDialog, self).__init__(None, title=caption, style=wx.CAPTION)
        self.controls = {}  
        
        scrolledwindow = wx.ScrolledWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.setup_window(scrolledwindow, sizer)
        
        scrolledwindow.SetSizer(sizer)
        scrolledwindow.SetScrollRate(20, 20)
        scrolledwindow.EnableScrolling(True, True)
        
        self.finish_ui(scrolledwindow)
        scrolledwindow.Layout()
        self.Centre()
        
    def create_control(self, name, tp, parent):
        ctrl = LabelledInput(parent, name, tp)
        self.controls[name] = ctrl
        return ctrl

class ResultQuery(PollingDialog):
    
    def __init__(self, argument):
        self.argument = argument
        super(ResultQuery, self).__init__("Please check results")
        
    def setup_window(self, window, sizer):
        for name, tp in self.argument.conclusion.result:
            sizer.Add(self.create_control(name, tp, window),
                      flag=wx.EXPAND | wx.ALL, border=3)
    def finish_ui(self, controlswindow):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(self, 
            label='Suggested Values for {}'.format(self.argument.conclusion.name)),
                  flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
        sizer.Add(wx.StaticText(self,
            label=str(self.argument.conclusion.result)),
                  flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
        
        sizer.Add(controlswindow, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
        sizer.Add(wx.Button(self, wx.ID_OK), flag=wx.CENTER)
        self.SetSizer(sizer)
        
        #self.SetSize((400, 400))
        
    @property
    def result(self):
        return dict([(name, ctrl.get_value()) for name, ctrl in self.controls.items()])
       

 

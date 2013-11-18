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
import wx.wizard as wizard
import  wx.lib.intctrl as intctrl

from calvin.reasoning import samples


    
def doLandformPolling():
    if len(samples.landformPoll) > 0:
        dialog = LandformDialog()
        dialog.ShowModal()
        dialog.Destroy()
    
def doSamplePolling():
    if len(samples.samplePoll) > 0:
        dialog = SampleDialog()
        dialog.ShowModal()
        dialog.Destroy()
    

class PollingControl:
    
    def getCaption(self, prop):
        return prop.capitalize() + "'s " + self.fName + ':'
    
    def getValue(self):
        return None
    
    def setField(self, fName):
        self.fName = fName
        
    def getField(self):
        return self.fName
    
class BooleanInput(wx.RadioBox, PollingControl):
    
    def __init__(self, parent, naAllowed=True):
        choices = ['Yes', 'No']
        if naAllowed:
            choices.append('No Answer')
        wx.RadioBox.__init__(self, parent, wx.ID_ANY, "", choices=choices)
        
        self.SetSelection(len(choices) - 1)
       
    def getCaption(self, prop):
        return 'Is ' + prop + ' ' + self.fName + '?'
        
    def getValue(self):
        val = self.GetSelection()
        if val == 0:
            return True
        elif val == 1:
            return False
        else:
            return None
        
class NumericInput(wx.TextCtrl, PollingControl):
    
    def __init__(self, parent, naAllowed=True):
        self.naAllowed = naAllowed
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY)
        
        self.value = None
        self.__setNilValue()
        
        self.Bind(wx.EVT_KILL_FOCUS, self.__checkInput)
        self.Bind(wx.EVT_SET_FOCUS, self.__highlight)
        
    def __setNilValue(self):
        if self.naAllowed:
            self.ChangeValue('<No Answer>')
            self.value = None
            self.SetSelection(-1, -1)
        else:
            if self.value is None:
                self.value = 0
                
            self.ChangeValue(str(self.value))
            self.SetSelection(-1, -1)
        
    def __checkInput(self, event):
        try:
            self.value = float(self.GetValue())
        except ValueError:
            self.__setNilValue()
        
        event.Skip()
        
    def __highlight(self, event):
        #horrible ugly hack to cope with wxWidgets bug.
        #this doesn't work otherwise. Why? Who knows!
        wx.CallAfter(self.__doHighlight)
            
        event.Skip()
        
    def __doHighlight(self):
        self.SetSelection(-1, -1)
        
    def getValue(self):
        return self.value
        
class CheckPane(wx.CollapsiblePane):
    
    def __init__(self, parent, label):
        wx.CollapsiblePane.__init__(self, parent, label=label)
        
        self.parent = parent
        self.items = []
        self.prevExp = False
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.checkBox = wx.CheckBox(self.GetPane(), label="Don't Give this Data")
        self.checkBox.SetValue(True)
        
        self.sizer.Add(self.checkBox, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.__paneChanged)
        self.Bind(wx.EVT_CHECKBOX, self.__checkChanged, self.checkBox)
        
        self.GetPane().SetSizer(self.sizer)
        
    def addItem(self, itemType, label):
        text = wx.StaticText(self.GetPane(), label=label)
        item = itemType(self.GetPane(), False)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(text, flag=wx.CENTER | wx.LEFT | wx.RIGHT, border=3)
        sizer.AddStretchSpacer()
        sizer.Add(item, flag=wx.CENTER | wx.LEFT | wx.RIGHT, border=3)
        
        self.items.append(item)
        self.sizer.Add(sizer, flag=wx.EXPAND)
        item.Disable()
        
    def isActive(self):
        return not self.checkBox.GetValue()
        
    def getItemValues(self):
        return [item.getValue() for item in self.items]
        
    def __paneChanged(self, event):
        self.parent.Layout()
        self.parent.FitInside()
        
        if self.IsExpanded() and not self.prevExp:
            self.prevExp = True
            self.checkBox.SetValue(False)
            self.__checkChanged()
            
        event.Skip()
        
    def __checkChanged(self, event=None):
        val = self.checkBox.GetValue()
        
        self.Collapse(val)
        self.parent.Layout()
        self.parent.FitInside()
        
        for item in self.items:
            item.Enable(not val)
        
    
class PollingDialog(wx.Dialog):
    
    def __init__(self, caption):
        wx.Dialog.__init__(self, None, title=caption, style=wx.CAPTION)  
        
        self.Centre()
        
    @staticmethod
    def getType(fName):
        fType = samples.getFieldType(fName)
        if fType == 'boolean':
            return BooleanInput
        else: #fType == 'num':
            return NumericInput
        
    def createControl(self, fName, naAllowed=True):
        control = PollingDialog.getType(fName)(self, naAllowed)
            
        control.setField(fName)
        return control
    
class PromptDialog(PollingDialog):
    def __init__(self, question, type):
        PollingDialog.__init__(self, 'landform information')
        
        label = wx.StaticText(self, label=question)
        if type == 'boolean':
            self.input = BooleanInput(self, False)
            #may need a string input here someday
        else:
            self.input = NumericInput(self, False)
        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, flag=wx.EXPAND)
        sizer.Add(self.input, flag=wx.EXPAND, proportion=1)
        
        button = wx.Button(self, wx.ID_OK)    
        sizer.Add(button, flag=wx.CENTER)
        
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()
        
        self.Bind(wx.EVT_BUTTON, self.__onOK, button)
        
    def __onOK(self, event):
        #might want to check that the input got filled?
        self.Close()
        
    def getResult(self):
        return self.input.getValue()
        
class LandformDialog(PollingDialog):
    
    def __init__(self):
        PollingDialog.__init__(self, "Please enter landform information")
        
        cSizer = wx.GridSizer(cols=2, hgap=8, vgap=8)
        self.controls = []
        
        for pollItem in samples.landformPoll:
            control = self.createControl(pollItem)
            label = wx.StaticText(self, label=control.getCaption('this landform'))
            
            cSizer.Add(label, flag=wx.CENTER)
            cSizer.Add(control, flag=wx.CENTER)
            self.controls.append(control)
        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(cSizer, flag=wx.EXPAND, proportion=1)
        button = wx.Button(self, wx.ID_OK)    
        sizer.Add(button, flag=wx.CENTER)
        
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()
        
        self.Bind(wx.EVT_BUTTON, self.__onOK, button)
        
    def __onOK(self, event):
        for item, control in zip(samples.landformPoll, self.controls):
            if control.getValue() is not None:
                samples.landformData[item] = control.getValue()
                
        samples.landformPoll = []
        self.Close()
        
class SampleDialog(PollingDialog):
    
    def __init__(self):
        PollingDialog.__init__(self, "Please enter sample data")
        
        self.scrolledWindow = wx.ScrolledWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panes = []
        
        for pollItem in samples.samplePoll:
            
            pane = CheckPane(self.scrolledWindow, pollItem)
            
            cType = self.getType(pollItem)
            
            for sample in samples.sample_list:
                pane.addItem(cType, str(sample))
                
            sizer.Add(pane, flag=wx.EXPAND | wx.ALL, border=3)
            self.panes.append(pane)
              
        self.scrolledWindow.SetSizer(sizer)
        self.scrolledWindow.SetScrollRate(20, 20)
        self.scrolledWindow.EnableScrolling(True, True)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        
        topSizer.Add(self.scrolledWindow, flag=wx.EXPAND, proportion=1)
        button = wx.Button(self, wx.ID_OK)    
        topSizer.Add(button, flag=wx.CENTER)
        
        self.SetSizer(topSizer)
        self.SetSize((250, 400))
        self.scrolledWindow.Layout()
        
        self.Bind(wx.EVT_BUTTON, self.__onOK, button)
        
    def __onOK(self, event):
        for item, pane in zip(samples.samplePoll, self.panes):
            if pane.isActive():
                for sample, value in zip(samples.sample_list, pane.getItemValues()):
                    sample[item] = value
                    
        samples.samplePoll = []
        self.Close()
        

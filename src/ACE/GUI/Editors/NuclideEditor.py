"""
NuclideEditor.py

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

from ACE.Framework.Nuclide  import Nuclide
from ACE.Framework.Nuclides import Nuclides

class NuclideEditor(wx.Frame):

    def __init__(self, parent, repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='ACE Nuclide Editor')
        
        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusbar = self.CreateStatusBar()

        nucLabel   = wx.StaticText(self, wx.ID_ANY, "Nuclides")
        availLabel = wx.StaticText(self, wx.ID_ANY, "Available Attributes")
        reqLabel   = wx.StaticText(self, wx.ID_ANY, "Required Attributes")
        optLabel   = wx.StaticText(self, wx.ID_ANY, "Optional Attributes")

        self.nuclides = self.repoman.GetModel("Nuclides")
        
        self.listBox = wx.ListBox(self, wx.ID_ANY, choices=self.nuclides.names(), style=wx.LB_SINGLE)
        self.avail = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SINGLE)
        self.req = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SINGLE)
        self.opt = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SINGLE)
        
        self.addReqButton    = wx.Button(self, wx.ID_ANY, "<-- Add to Required  ---")
        self.addOptButton    = wx.Button(self, wx.ID_ANY, "<-- Add to Optional  ---")
        self.removeAttButton = wx.Button(self, wx.ID_ANY, "--- Remove Attribute -->")
                
        self.addButton = wx.Button(self, wx.ID_ANY, "Add Nuclide...")
        self.removeButton = wx.Button(self, wx.ID_ANY, "Delete Nuclide")
        
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(nucLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.listBox, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(reqLabel, border=5, flag=wx.ALL)
        columnTwoSizer.Add(self.req, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        
        columnThreeSizer = wx.BoxSizer(wx.VERTICAL)
        columnThreeSizer.Add(optLabel, border=5, flag=wx.ALL)
        columnThreeSizer.Add(self.opt, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

        columnFourSizer = wx.BoxSizer(wx.VERTICAL)
        columnFourSizer.Add(self.addReqButton,    border=5, flag=wx.ALL)
        columnFourSizer.Add(self.addOptButton,    border=5, flag=wx.ALL)
        columnFourSizer.Add(self.removeAttButton, border=5, flag=wx.ALL)

        columnFiveSizer = wx.BoxSizer(wx.VERTICAL)
        columnFiveSizer.Add(availLabel, border=5, flag=wx.ALL)
        columnFiveSizer.Add(self.avail, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        
        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnTwoSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnThreeSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnFourSizer, flag=wx.ALIGN_CENTER_VERTICAL)
        columnSizer.Add(columnFiveSizer, proportion=1, flag=wx.EXPAND)
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton,    border=5, flag=wx.ALL)
        buttonSizer.Add(self.removeButton, border=5, flag=wx.ALL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizer(sizer)
        self.Layout()
        self.SetSize(self.GetBestSize())
        self.SetMinSize(self.GetSize())
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/nuceditor/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/nuceditor/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)

        self.removeButton.Disable()
        self.addReqButton.Disable()
        self.addOptButton.Disable()
        self.removeAttButton.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.removeButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddReq, self.addReqButton)
        self.Bind(wx.EVT_BUTTON, self.OnAddOpt, self.addOptButton)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveAtt, self.removeAttButton)
        
        self.listBox.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInNuclides)
        self.req.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInReq)
        self.opt.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInOpt)
        self.avail.Bind(wx.EVT_LEFT_UP, self.OnLeftUpInAvail)
        
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.listBox)
        self.Bind(wx.EVT_LISTBOX, self.OnAttSelect, self.avail)
        self.Bind(wx.EVT_LISTBOX, self.OnReqSelect, self.req)
        self.Bind(wx.EVT_LISTBOX, self.OnOptSelect, self.opt)
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        repoman.AddWindow(self)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/nuceditor/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()
        config.Write("windows/nuceditor/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().nucEditor = None
        del(self.GetParent().nucEditor)
        self.Destroy()

    def OnAdd(self, event):
        dialog = wx.TextEntryDialog(self, "Enter Nuclide Name", "Nuclide Entry Dialog", style=wx.OK | wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.GetValue()
            if value != "":
                if not self.nuclides.contains(value):
                    self.nuclides.add(Nuclide(value))
                    self.listBox.Set(self.nuclides.names())
                    self.ClearAttLists()
                    self.removeButton.Disable()
                    self.repoman.RepositoryModified()
                else:
                    dialog = wx.MessageDialog(None, 'Nuclide "' + value + '" already exists!', "Duplicate Nuclide", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Nuclide name not specified!', "Illegal Nuclide Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dialog.Destroy()
        
    def OnAddReq(self, event):
        name = self.avail.GetStringSelection()
        self.nuclide.add_required(name)
        self.InitAttLists()
        self.repoman.RepositoryModified()

    def OnAddOpt(self, event):
        name = self.avail.GetStringSelection()
        self.nuclide.add_optional(name)
        self.InitAttLists()
        self.repoman.RepositoryModified()
    
    def NuclideInUse(self, nuclide):
        
        # determine if a nuclide is being used
        # first check to see if a workflow uses it
        # second check to see if an experient uses it
        # third check to see if a sample references it
        # if any of these conditions is true, return True, otherwise False
        
        workflows = self.repoman.GetModel("Workflows")
        names     = workflows.names()
        for name in names:
            workflow = workflows.get(name)
            if workflow.supports_nuclide(nuclide):
                return (True, "Nuclide In Use: Used by Workflow '%s'" % (name))
        
        experiments = self.repoman.GetModel("Experiments")
        experiments = experiments.experimentsWithNuclide(nuclide)
        if len(experiments) > 0:
            return (True, "Nuclide In Use: Used by Experiment '%s'" % (experiments[0]))
        
        samples_db = self.repoman.GetModel("Samples")
        ids = samples_db.ids()
        for s_id in ids:
            sample = samples_db.get(s_id)
            if nuclide in sample:
                return (True, "Nuclide In Use: Used by Sample '%s'" % (s_id))
                
        return (False, "")
    
    def OnSelect(self, event):
        name = self.listBox.GetStringSelection()
        self.nuclide = self.nuclides.get(name)
        if name != "ALL":
            status, message = self.NuclideInUse(name)
            if status:
                message = "Nuclide cannot be deleted: " + message
                self.removeButton.Enable(False)
            else:
                self.removeButton.Enable(True)
            self.statusbar.SetStatusText(message)
        else:
            self.removeButton.Enable(False)
            self.statusbar.SetStatusText("The 'ALL' Nuclide cannot be deleted.")
        self.InitAttLists()
        
    # list box controls do not deliver deselection events when in 'single selection' mode
    # but it is still possible for the user to clear the selection from such a list
    # as such, we need to monitor the LEFT_UP events for each of our list boxes and
    # check to see if the selection got cleared without us knowning about it
    # if so, we need to update the user interface appropriately
    # this code falls under the category of "THIS SUCKS!" It would be much cleaner to
    # just be informed of list deselection events
    def OnLeftUpInNuclides(self, event):
        index = self.listBox.GetSelection()
        if index == -1:
            self.ClearAttLists()
            self.removeButton.Disable()
        event.Skip()

    def OnLeftUpInReq(self, event):
        index = self.req.GetSelection()
        if index == -1:
            self.removeAttButton.Disable()
        event.Skip()

    def OnLeftUpInOpt(self, event):
        index = self.opt.GetSelection()
        if index == -1:
            self.removeAttButton.Disable()
        event.Skip()

    def OnLeftUpInAvail(self, event):
        index = self.avail.GetSelection()
        if index == -1:
            self.addReqButton.Disable()
            self.addOptButton.Disable()
        event.Skip()

        
    def OnAttSelect(self, event):
        self.addReqButton.Enable(True)
        self.addOptButton.Enable(True)
        self.removeAttButton.Disable()
        self.req.Deselect(self.req.GetSelection())
        self.opt.Deselect(self.opt.GetSelection())

    def OnReqSelect(self, event):
        self.addReqButton.Disable()
        self.addOptButton.Disable()
        self.removeAttButton.Enable(True)
        self.avail.Deselect(self.avail.GetSelection())
        self.opt.Deselect(self.opt.GetSelection())
        self.att_selection = "req"

    def OnOptSelect(self, event):
        self.addReqButton.Disable()
        self.addOptButton.Disable()
        self.removeAttButton.Enable(True)
        self.avail.Deselect(self.avail.GetSelection())
        self.req.Deselect(self.req.GetSelection())
        self.att_selection = "opt"
    
    def OnRemove(self, event):
        name = self.listBox.GetStringSelection()
        self.nuclides.remove(name)
        self.listBox.Set(self.nuclides.names())
        self.ClearAttLists()
        self.removeButton.Disable()
        self.repoman.RepositoryModified()

    def OnRemoveAtt(self, event):
        if self.att_selection == "req":
            name = self.req.GetStringSelection()
            self.nuclide.remove_required(name)
        else:
            name = self.opt.GetStringSelection()
            self.nuclide.remove_optional(name)
        self.InitAttLists()
        self.repoman.RepositoryModified()

    def ClearAttLists(self):
        self.req.Clear()
        self.opt.Clear()
        self.avail.Clear()
        self.addReqButton.Disable()
        self.addOptButton.Disable()
        self.removeAttButton.Disable()
        
    def InitAttLists(self):
        self.ClearAttLists()
        
        atts = self.repoman.GetModel("Attributes").names()
        
        if self.nuclide.name() != "ALL":
            default_nuc = self.nuclides.get("ALL")
            atts = [att for att in atts if not att in default_nuc.required_atts()]
            atts = [att for att in atts if not att in default_nuc.optional_atts()]
        
        req  = self.nuclide.required_atts()
        opt  = self.nuclide.optional_atts()
        
        self.req.Set(req)
        self.opt.Set(opt)
        
        avail_temp = [att for att in atts if not att in req]
        avail = [att for att in avail_temp if not att in opt]
        avail.sort()
        self.avail.Set(avail)
        

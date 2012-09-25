"""
ExperimentSelector.py

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

class ExperimentSelector(wx.Dialog):

    def __init__(self, parent, samples, repoman):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title="Experiment/Sample Selector")

        self.samples = samples
        self.repoman = repoman

        label1 = wx.StaticText(self, wx.ID_ANY, "Apply Experiment ")
        label2 = wx.StaticText(self, wx.ID_ANY, "To Eligible Samples: ")

        experiments = self.repoman.GetModel("Experiments")
        exp_names = experiments.keys()
        exp_names.insert(0, "<SELECT EXPERIMENT>")
        
        self.selectedExperiment = wx.ComboBox(self, wx.ID_ANY, value="<SELECT EXPERIMENT>", choices=exp_names, style=wx.CB_DROPDOWN | wx.CB_READONLY)

        ids = ["%s" % (sample['id']) for sample in self.samples]

        no_dups = set(ids)

        ids = sorted(list(no_dups))

        self.listBox = wx.ListBox(self, wx.ID_ANY, choices=ids, style=wx.LB_SINGLE)

        self.ok_btn = wx.Button(self, wx.ID_OK, 'Ok')
        cancel_btn = wx.Button(self, wx.ID_CANCEL, 'Cancel')

        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        rowSizer.Add(label1, border=5, flag=wx.ALL)
        rowSizer.Add(self.selectedExperiment, border=5, flag=wx.ALL)

        btnsizer = wx.StdDialogButtonSizer()
        btnsizer.AddButton(self.ok_btn)
        btnsizer.AddButton(cancel_btn)
        btnsizer.Realize()
        
        self.ok_btn.Disable()

        columnSizer = wx.BoxSizer(wx.VERTICAL)
        columnSizer.Add(rowSizer, border=5, flag=wx.ALL)
        columnSizer.Add(label2, border=5, flag=wx.ALL)
        columnSizer.Add(self.listBox, proportion=1, border=5, flag=wx.ALL)
        columnSizer.Add(btnsizer, border=10, flag=wx.ALL)
        
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect, self.selectedExperiment)
        self.Bind(wx.EVT_LISTBOX, self.OnListSelect, self.listBox)
        

        self.SetSizer(columnSizer)
        self.Layout()
        self.Centre()
        
    def OnListSelect(self, event):
        self.listBox.SetSelection(wx.NOT_FOUND)
        
    def OnSelect(self, event):
        selected = self.selectedExperiment.GetStringSelection()
        if selected == "<SELECT EXPERIMENT>":
            ids = ["%s" % (sample['id']) for sample in self.samples]
            no_dups = set(ids)
            ids = sorted(list(no_dups))
            self.listBox.Set(ids)
            if len(ids) > 0:
                self.listBox.SetFirstItem(0)
            self.ok_btn.Disable()
        else:
            experiments = self.repoman.GetModel("Experiments")
            experiment = experiments.get(selected)
            
            all_samples = self.repoman.GetModel("Samples")

            self.current_samples = set()

            for vsample in self.samples:
                s_id = vsample['id']
                sample = all_samples.get(s_id)
                if experiment['nuclide'] in sample:
                    if experiment['name'] not in sample.experiments(experiment['nuclide']):
                        sample.experiment = experiment['name']
                        self.current_samples.add(sample)

            self.current_samples = sorted(list(self.current_samples))
            
            if len(self.current_samples) > 0:
                self.ok_btn.Enable()
            else:
                self.ok_btn.Disable()
            
            ids = ["%s" % (sample['id']) for sample in self.current_samples]
            no_dups = set(ids)
            ids = sorted(list(no_dups))
            self.listBox.Set(ids)
            if len(ids) > 0:
                self.listBox.SetFirstItem(0)
            
            

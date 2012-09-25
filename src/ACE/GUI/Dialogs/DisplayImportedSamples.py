"""
DisplayImportedSamples.py

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

class DisplayImportedSamples(wx.Dialog):
    def __init__(self, parent, csv_file, fields, rows):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Import Samples')
        
        self.csv_file = csv_file
        self.fields = fields
        self.rows = rows
        
        headingLabel = wx.StaticText(self, wx.ID_ANY, "The following samples are contained in %s:" % self.csv_file)
        questionLabel = wx.StaticText(self, wx.ID_ANY, "Do you want to import these samples as displayed?")
        # ok_button      = wx.Button(self, wx.ID_OK, "Yes")
        # cancel_button  = wx.Button(self, wx.ID_CANCEL, "No")
        
        self.grid = wx.grid.Grid(self, wx.ID_ANY, size=(640, 480))
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "Waiting For Data")
        self.grid.AutoSize()
        self.grid.EnableEditing(False)

        self.ConfigureGrid()
        
        self.createGroup = wx.CheckBox(self, -1, "Auto-Create group with 'sample set' name and these samples")

        if 'sample set' not in self.fields:
            self.createGroup.Enable(False)
            self.addSampleSet = wx.CheckBox(self, -1, "Add 'sample set' attribute with value: ")
            self.sampleSetValue = wx.TextCtrl(self, wx.ID_ANY, size=(250, -1))
            self.sampleSetValue.Enable(False)
            self.sampleSetSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sampleSetSizer.Add(self.addSampleSet, border=5, flag=wx.ALL)
            self.sampleSetSizer.Add(self.sampleSetValue, border=5, flag=wx.ALL)
            
            self.Bind(wx.EVT_TEXT, self.OnSampleSetValueUpdate, self.sampleSetValue)

        if 'source' not in self.fields:
            self.addSource = wx.CheckBox(self, -1, "Add 'source' attribute with value: ")
            self.sourceValue = wx.TextCtrl(self, wx.ID_ANY, size=(250, -1))
            self.sourceValue.SetValue(self.csv_file)
            self.sourceValue.Enable(False)
            self.sourceSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sourceSizer.Add(self.addSource, border=5, flag=wx.ALL)
            self.sourceSizer.Add(self.sourceValue, border=5, flag=wx.ALL)

        # btnsizer = wx.StdDialogButtonSizer()
        # btnsizer.AddButton(ok_button)
        # btnsizer.AddButton(cancel_button)
        # btnsizer.Realize()

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(headingLabel, border=5, flag=wx.ALL)
        sizer.Add(self.grid, border=5, flag=wx.ALL)
        sizer.Add(self.createGroup, border=5, flag=wx.ALL)

        if 'sample set' not in self.fields:
            sizer.Add(self.sampleSetSizer, border=0, flag=wx.ALL)
        if 'source' not in self.fields:
            sizer.Add(self.sourceSizer, border=0, flag=wx.ALL)
        sizer.Add(questionLabel, border=5, flag=wx.ALL | wx.ALIGN_CENTER)
        sizer.Add(btnsizer, border=5, flag=wx.ALL | wx.ALIGN_CENTER)

        if 'sample set' not in self.fields:
            self.Bind(wx.EVT_CHECKBOX, self.OnAddSampleSet, self.addSampleSet)
        if 'source' not in self.fields:
            self.Bind(wx.EVT_CHECKBOX, self.OnAddSource, self.addSource)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Centre(wx.BOTH)

    def OnAddSampleSet(self, event):
        if self.addSampleSet.IsChecked():
            self.sampleSetValue.Enable(True)
        else:
            self.createGroup.SetValue(False)
            self.createGroup.Enable(False)
            self.sampleSetValue.SetValue("")
            self.sampleSetValue.Enable(False)

    def OnAddSource(self, event):
        if self.addSource.IsChecked():
            self.sourceValue.Enable(True)
        else:
            self.sourceValue.Enable(False)
            self.sourceValue.SetValue(self.csv_file)

    def OnSampleSetValueUpdate(self, event):
        value = self.sampleSetValue.GetValue()
        if value != "":
            self.createGroup.Enable(True)
        else:
            self.createGroup.SetValue(False)
            self.createGroup.Enable(False)

    def ConfigureGrid(self):
        self.grid.BeginBatch()

        numCols = len(self.fields)
        numRows = len(self.rows)

        currentCols = self.grid.GetNumberCols()
        currentRows = self.grid.GetNumberRows()
        
        if numCols > currentCols:
            self.grid.AppendCols(numCols - currentCols)
        if numCols < currentCols:
            self.grid.DeleteCols(0, currentCols - numCols)
        if numRows > currentRows:
            self.grid.AppendRows(numRows - currentRows)
        if numRows < currentRows:
            self.grid.DeleteRows(0, currentRows - numRows)

        # clear row labels
        for index in range(len(self.rows)):
            self.grid.SetRowLabelValue(index, "")

        # set column names
        index = 0
        maxNumberOfSpaces = 0
        maxHeight = 0
        for att in self.fields:
            att_value = att.replace(" ", "\n")
            numberOfSpaces = att.count(" ")
            self.grid.SetColLabelValue(index, att_value)
            extent = self.grid.GetTextExtent(att_value)
            height = extent[1]
            if height > maxHeight:
                maxHeight = height
            if numberOfSpaces > maxNumberOfSpaces:
                maxNumberOfSpaces = numberOfSpaces
            index += 1
        height = maxHeight * (maxNumberOfSpaces + 1)
        height += 20
        self.grid.SetColLabelSize(height)

        # fill out grid with values
        for row in range(len(self.rows)):
            index = 0
            for att in self.fields:
                sample = self.rows[row]
                value = sample[att]
                
                if isinstance(value, float):
                    self.grid.SetCellValue(row, index, "%.2f" % value)
                else:
                    self.grid.SetCellValue(row, index, str(value))
                index += 1
            
        self.grid.AutoSize()

        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()

    def add_sample_set(self):
        
        if not hasattr(self, "sampleSetValue"):
            return False
        
        value = self.sampleSetValue.GetValue()
        if value == '':
            return False
        else:
            return self.addSampleSet.IsChecked()
            
    def get_sample_set_name(self):
        if not hasattr(self, "sampleSetValue"):
            return None
        return self.sampleSetValue.GetValue()
        
    def add_source(self):
        if not hasattr(self, "sourceValue"):
            return False
        
        value = self.sourceValue.GetValue()
        if value == '':
            return False
        else:
            return self.addSource.IsChecked()
            
    def get_source(self):
        if not hasattr(self, "sourceValue"):
            return None
        return self.sourceValue.GetValue()
        
    def create_group(self):
        return self.createGroup.IsChecked()

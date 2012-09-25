"""
ExperimentEditor.py

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

from ACE.GUI.Util.ExperimentUtils import ExperimentUtils
from ACE.GUI.Util.FancyTextRenderer import FancyTextRenderer

class ExperimentEditor(wx.Dialog):

    report_order = []
    report_order.append('name')
    report_order.append('nuclide')
    report_order.append('timestep')
    report_order.append('calibration')
    report_order.append('dating')
    report_order.append('calibration_set')
    report_order.append('geomagneticLatitude')
    report_order.append('geographicScaling')
    report_order.append('geomagneticIntensity')
    report_order.append('seaLevel')
    report_order.append('psi_mu_0')
    report_order.append('phi_mu_f0')
    report_order.append('slowMuonPerc')
    report_order.append('fastMuonPerc')
    
    @staticmethod
    def report_cmp(x, y):
        return cmp(ExperimentEditor.report_order.index(x), ExperimentEditor.report_order.index(y))

    def __init__(self, parent, repoman):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title='ACE Experiment Editor')
        
        self.repoman = repoman

        self.experiments = self.repoman.GetModel("Experiments")

        self.selectedNuclide = None
        self.fields = {}
        self.values = {}
        self.error_labels = {}

        self.ok_button = wx.Button(self, wx.ID_OK, "Create Experiment")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        self.ok_button.Disable()

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(cancel_button, border=5, flag=wx.ALL)
        buttonSizer.Add(self.ok_button, border=5, flag=wx.ALL)
        
        self.editor = wx.Notebook(self, wx.ID_ANY, size=(540, 380), style=wx.BK_DEFAULT)
        
        self.editor.AddPage(self.createWorkflowsPage(self.editor), "Workflows")
        self.editor.AddPage(self.createCalSetPage(self.editor), "Calibration Set")
        self.editor.AddPage(self.createFactorsPage(self.editor), "Factors")
        self.editor.AddPage(self.createParamsPage(self.editor), "Parameters")
        self.editor.AddPage(self.createSummaryPage(self.editor), "Summary")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.editor, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.CENTER)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Centre()
        
        self.OnNameUpdate(None)
        self.OnTimeStepUpdate(None)
        
    def OnNameUpdate(self, evt):
        value = self.fields['name'].GetValue()
        if value in self.repoman.GetModel("Experiments").names():
            self.values['name'] = 'Invalid: Name In Use'
            self.error_name.SetLabel('<-- Invalid: Name In Use')
        elif value == "":
            self.values['name'] = 'Invalid: Empty Name'
            self.error_name.SetLabel('<-- Invalid: Empty Name')
        else:
            self.values['name'] = value
            self.error_name.SetLabel('                         ')
        self.fields['name'].GetParent().Refresh()
        self.ConfigureGrid()
        self.CheckStatus()
            
    def OnTimeStepUpdate(self, evt):
        try:
            self.values['timestep'] = int(self.fields['timestep'].GetValue())
            self.error_timestep.SetLabel('                         ')
        except:
            self.values['timestep'] = 'Invalid: Need Integer'
            self.error_timestep.SetLabel('<-- Invalid: Need Integer')
        self.fields['timestep'].GetParent().Refresh()
        self.ConfigureGrid()
        self.CheckStatus()
        
    def createWorkflowsPage(self, editor):

        panel = wx.Panel(editor, wx.ID_ANY)

        cal_label = wx.StaticText(panel, wx.ID_ANY, "Calibration Workflow:")
        dat_label = wx.StaticText(panel, wx.ID_ANY, "Dating Workflow:")

        self.fields['calibration'] = wx.ComboBox(panel, wx.ID_ANY, value="Select Calibration Workflow", choices=["Select Calibration Workflow"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.fields['dating'] = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_READONLY)
        
        self.values['calibration'] = 'Not Selected'
        self.values['dating'] = 'Not Selected'
        
        widgets = wx.GridBagSizer(10, 10)
        
        widgets.Add(cal_label, pos=(0, 0), border=5, flag=wx.ALIGN_RIGHT | wx.ALL)
        widgets.Add(self.fields['calibration'], pos=(0, 1), border=5, flag=wx.ALIGN_LEFT | wx.ALL | wx.EXPAND)
        widgets.Add(dat_label, pos=(1, 0), border=5, flag=wx.ALIGN_RIGHT | wx.ALL)
        widgets.Add(self.fields['dating'], pos=(1, 1), border=5, flag=wx.ALIGN_LEFT | wx.ALL | wx.EXPAND)

        prev_button = wx.Button(panel, wx.ID_ANY, "Prev")
        next_button = wx.Button(panel, wx.ID_ANY, "Next")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(prev_button, border=5, flag=wx.ALL)
        buttonSizer.Add(next_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Step 2 of 6"), border=5, flag=wx.ALL | wx.CENTER)
        sizer.Add(widgets, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.CENTER)

        panel.SetSizer(sizer)
        panel.Layout()

        def OnNext(evt):
            editor.ChangeSelection(2)

        def OnPrev(evt):
            editor.ChangeSelection(0)
        
        panel.Bind(wx.EVT_BUTTON, OnPrev, prev_button)
        panel.Bind(wx.EVT_BUTTON, OnNext, next_button)
        panel.Bind(wx.EVT_COMBOBOX, self.OnWorkflowSelect, self.fields['calibration'])

        return panel
        
    def createCalSetPage(self, editor):
        
        panel = wx.Panel(editor, wx.ID_ANY)
        
        label = wx.StaticText(panel, wx.ID_ANY, "Calibration Set:")
        
        self.fields['calibration_set'] = wx.ComboBox(panel, wx.ID_ANY, value="Select Calibration Set", choices=["Select Calibration Set"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        
        self.values['calibration_set'] = 'Not Selected'
        
        widgetsizer = wx.BoxSizer(wx.HORIZONTAL)
        widgetsizer.Add(label, border=5, flag=wx.ALL | wx.RIGHT)
        widgetsizer.Add(self.fields['calibration_set'], border=5, proportion=1, flag=wx.ALL | wx.EXPAND)

        prev_button = wx.Button(panel, wx.ID_ANY, "Prev")
        next_button = wx.Button(panel, wx.ID_ANY, "Next")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(prev_button, border=5, flag=wx.ALL)
        buttonSizer.Add(next_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Step 3 of 6"), border=5, flag=wx.ALL | wx.CENTER)
        sizer.Add(widgetsizer, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.CENTER)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        def OnNext(evt):
            editor.ChangeSelection(3)

        def OnPrev(evt):
            editor.ChangeSelection(1)
        
        panel.Bind(wx.EVT_BUTTON, OnPrev, prev_button)
        panel.Bind(wx.EVT_BUTTON, OnNext, next_button)
        panel.Bind(wx.EVT_COMBOBOX, self.OnCalSetSelect, self.fields['calibration_set'])
        
        return panel

    def createFactorsPage(self, editor):
        
        panel = wx.Panel(editor, wx.ID_ANY)
        
        self.factorPanel = wx.Panel(panel, wx.ID_ANY)
        
        label = wx.StaticText(self.factorPanel, wx.ID_ANY, "You need to select a Calibration Workflow\nbefore you can configure an Experiment's Factors")

        prev_button = wx.Button(panel, wx.ID_ANY, "Prev")
        next_button = wx.Button(panel, wx.ID_ANY, "Next")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(prev_button, border=5, flag=wx.ALL)
        buttonSizer.Add(next_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Step 4 of 6"), border=5, flag=wx.ALL | wx.CENTER)
        sizer.Add(self.factorPanel, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.CENTER)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        def OnNext(evt):
            editor.ChangeSelection(4)

        def OnPrev(evt):
            editor.ChangeSelection(2)
        
        panel.Bind(wx.EVT_BUTTON, OnPrev, prev_button)
        panel.Bind(wx.EVT_BUTTON, OnNext, next_button)
        
        return panel

    def createParamsPage(self, editor):
        
        panel = wx.Panel(editor, wx.ID_ANY)
        
        self.paramsPanel = wx.Panel(panel, wx.ID_ANY)
        
        label = wx.StaticText(self.paramsPanel, wx.ID_ANY, "You need to select a Nuclide\nbefore you can configure an Experiment's Parameters")

        prev_button = wx.Button(panel, wx.ID_ANY, "Prev")
        next_button = wx.Button(panel, wx.ID_ANY, "Next")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(prev_button, border=5, flag=wx.ALL)
        buttonSizer.Add(next_button, border=5, flag=wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Step 5 of 6"), border=5, flag=wx.ALL | wx.CENTER)
        sizer.Add(self.paramsPanel, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL | wx.CENTER)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        def OnNext(evt):
            editor.ChangeSelection(5)

        def OnPrev(evt):
            editor.ChangeSelection(3)
        
        panel.Bind(wx.EVT_BUTTON, OnPrev, prev_button)
        panel.Bind(wx.EVT_BUTTON, OnNext, next_button)
        
        return panel

    def createSummaryPage(self, editor):
        
        panel = wx.Panel(editor, wx.ID_ANY)

        self.grid = wx.grid.Grid(panel, wx.ID_ANY)
        self.grid.CreateGrid(1, 1)
        self.grid.SetCellValue(0, 0, "Select one or more Experiments")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "No Experiments Selected")
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.grid.SetDefaultRenderer(FancyTextRenderer())

        ExperimentUtils.InstallGridHint(self.grid, ExperimentUtils.GetToolTipString)
        
        self.ConfigureGrid()
        self.CheckStatus()

        # prev_button = wx.Button(panel, wx.ID_ANY, "Prev")
        # next_button = wx.Button(panel, wx.ID_ANY, "Next")
        # 
        # next_button.Disable()
        # 
        # buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # buttonSizer.Add(prev_button, border=5, flag=wx.ALL)
        # buttonSizer.Add(next_button, border=5, flag=wx.ALL)

        gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer.Add(self.grid, border=5, flag=wx.ALL | wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Step 6 of 6"), border=5, flag=wx.ALL|wx.CENTER)
        sizer.Add(gridSizer, border=5, flag=wx.ALL | wx.EXPAND)
        # sizer.Add(buttonSizer, border=5, flag=wx.ALL|wx.CENTER)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        # def OnPrev(evt):
        #     editor.ChangeSelection(4)
        # 
        # panel.Bind(wx.EVT_BUTTON, OnPrev, prev_button)
        
        return panel
        
    def ConfigureGrid(self):
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        
        self.grid.AppendCols(1)
        self.grid.AppendRows(len(self.fields))
        
        rowNames = sorted(self.fields.keys())
        rowLabels = rowNames[:]
        rowLabels.sort(ExperimentEditor.report_cmp)
        
        displayLabels = [ExperimentUtils.display_name[item] for item in rowLabels]
        
        maxName = ""
        index = 0
        for label in displayLabels:
            if len(label) > len(maxName):
                maxName = label
            self.grid.SetRowLabelValue(index, label)
            index += 1
        extent = self.grid.GetTextExtent(maxName)
        width = extent[0]
        if width == 0:
            width = 50
        else:
            width += 25
        self.grid.SetRowLabelSize(width)
    
        self.grid.SetColLabelValue(0, '')
        
        row = 0
        for label in rowLabels:
            try:
                self.grid.SetCellValue(row, 0, "<FancyText>%s</FancyText>" % (ExperimentUtils.GetGridValue(self.values, label)))
            except Exception, e:
                print e
            row += 1
            
        self.grid.AutoSize()
        
        h, w = self.grid.GetSize()
        self.grid.SetSize((h + 5, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()

    def OnNuclideSelect(self, event):
        
        newNuclide = self.fields["nuclide"].GetStringSelection()
        if newNuclide == "Select Nuclide":
            newNuclide = None
            
        if self.selectedNuclide != newNuclide:
            self.selectedNuclide = newNuclide
            if newNuclide is None:
                newNuclide = 'Not Selected'
            self.values['nuclide'] = newNuclide
            self.UpdateEditor()
            
        self.ConfigureGrid()
        self.CheckStatus()
            
    def OnWorkflowSelect(self, event):
        name = self.fields['calibration'].GetStringSelection()
        w = None
        if name != "Select Calibration Workflow":
            self.values['calibration'] = name
            w = self.repoman.GetModel("Workflows").get(name)
            name = w.get_dating_workflow()
            if name is not None:
                self.fields['dating'].SetValue(name)
                self.values['dating'] = name
            else:
                self.fields['dating'].SetValue('')
                self.values['dating'] = 'Not Selected'
        else:
            self.fields['dating'].SetValue("")
            self.values['calibration'] = 'Not Selected'
            self.values['dating'] = 'Not Selected'
            
        self.UpdateFactors(w)
        self.ConfigureGrid()
        self.CheckStatus()

    def OnCalSetSelect(self, event):
        name = self.fields['calibration_set'].GetStringSelection()
        if name != "Select Calibration Set":
            self.values['calibration_set'] = name
        else:
            self.values['calibration_set'] = 'Not Selected'
        self.ConfigureGrid()
        self.CheckStatus()
        
    def GetValues(self):
        return self.values

    def UpdateEditor(self):
        self.UpdateWorkflowChoices()
        self.UpdateCalSets()
        self.UpdateParams()
        self.Layout()

    def UpdateWorkflowChoices(self):
        self.fields['calibration'].Clear()
        self.fields['calibration'].Append("Select Calibration Workflow")
        self.fields['calibration'].SetStringSelection("Select Calibration Workflow")
        if self.selectedNuclide is not None:
            names = self.repoman.GetModel("Workflows").names()
            for name in names:
                w = self.repoman.GetModel("Workflows").get(name)
                if w.get_type() == "calibration":
                    if w.supports_nuclide(self.selectedNuclide):
                        self.fields['calibration'].Append(w.get_name())
        self.OnWorkflowSelect(None)
                        
    def UpdateCalSets(self):
        self.fields['calibration_set'].Clear()
        self.fields['calibration_set'].Append("Select Calibration Set")
        self.fields['calibration_set'].SetStringSelection("Select Calibration Set")
        if self.selectedNuclide is not None:
            
            groups = self.repoman.GetModel('Groups')
            samples_db = self.repoman.GetModel('Samples')
            
            names = groups.calibration_sets(samples_db)
            
            for name in names:
                group = groups.get(name)
                if self.selectedNuclide in group.get_nuclides():
                    self.fields['calibration_set'].Append(group.name())

    def CheckStatus(self):
        count = 0
        for key in self.values.keys():
            value = self.values[key]
            if isinstance(value, (str, unicode)):
                if value.startswith("Not") or value.startswith("Invalid"):
                    count += 1
        if count == 0:
            self.ok_button.Enable()
        else:
            self.ok_button.Disable()

    def UpdateParams(self):
        self.paramsPanel.DestroyChildren()
        self.paramsPanel.SetSizer(None)
        
        for name in ["psi_mu_0", "phi_mu_f0", "slowMuonPerc", "fastMuonPerc"]:
            try:
                self.paramsPanel.Unbind(wx.EVT_TEXT, self.fields[name])
            except:
                pass
            try:
                del self.fields[name]
                del self.values[name]
            except:
                pass
                
        if self.selectedNuclide is not None:
            if self.selectedNuclide == "36Cl":
                self.fields["psi_mu_0"] = wx.TextCtrl(self.paramsPanel, wx.ID_ANY, name="psi_mu_0")
                self.fields["psi_mu_0"].SetValue(str(Nuclide.getSlowMuonStoppingRate()))
                self.error_labels["psi_mu_0"] = wx.StaticText(self.paramsPanel, wx.ID_ANY, '                         ')                
                self.values["psi_mu_0"] = Nuclide.getSlowMuonStoppingRate()
                self.paramsPanel.Bind(wx.EVT_TEXT, self.OnParamUpdate, self.fields['psi_mu_0'])                
                
                self.fields["phi_mu_f0"] = wx.TextCtrl(self.paramsPanel, wx.ID_ANY, name="phi_mu_f0")
                self.fields["phi_mu_f0"].SetValue(str(Nuclide.getFastMuonFlux()))
                self.values["phi_mu_f0"] = Nuclide.getFastMuonFlux()
                self.error_labels["phi_mu_f0"] = wx.StaticText(self.paramsPanel, wx.ID_ANY, '                         ')
                self.paramsPanel.Bind(wx.EVT_TEXT, self.OnParamUpdate, self.fields['phi_mu_f0'])
                
            else:
                self.fields["slowMuonPerc"] = wx.TextCtrl(self.paramsPanel, wx.ID_ANY, name="slowMuonPerc")
                self.fields["slowMuonPerc"].SetValue(str(Nuclide.getSlowMuonPerc(self.selectedNuclide)))
                self.values["slowMuonPerc"] = Nuclide.getSlowMuonPerc(self.selectedNuclide)
                self.error_labels["slowMuonPerc"] = wx.StaticText(self.paramsPanel, wx.ID_ANY, '                         ')
                self.paramsPanel.Bind(wx.EVT_TEXT, self.OnParamUpdate, self.fields['slowMuonPerc'])
                
                self.fields["fastMuonPerc"] = wx.TextCtrl(self.paramsPanel, wx.ID_ANY, name="fastMuonPerc")
                self.fields["fastMuonPerc"].SetValue(str(Nuclide.getFastMuonPerc(self.selectedNuclide)))
                self.values["fastMuonPerc"] = Nuclide.getFastMuonPerc(self.selectedNuclide)
                self.error_labels["fastMuonPerc"] = wx.StaticText(self.paramsPanel, wx.ID_ANY, '                         ')
                self.paramsPanel.Bind(wx.EVT_TEXT, self.OnParamUpdate, self.fields['fastMuonPerc'])
                
            labels = []
    
            if self.selectedNuclide == "36Cl":
                labels.append(wx.StaticText(self.paramsPanel, wx.ID_ANY, "Slow Muon Stopping Rate:"))
                labels.append(wx.StaticText(self.paramsPanel, wx.ID_ANY, "Fast Muon Flux:"))
            else:
                labels.append(wx.StaticText(self.paramsPanel, wx.ID_ANY, "Slow Muon Production:"))
                labels.append(wx.StaticText(self.paramsPanel, wx.ID_ANY, "Fast Muon Production:"))
            
            sizer = wx.GridBagSizer(10, 10)
    
            row = 0
            for label in labels:
                sizer.Add(label, pos=(row, 0), border=5, flag=wx.ALIGN_RIGHT | wx.ALL)
                row += 1
    
            names = []
            if self.selectedNuclide == "36Cl":
                names = ["psi_mu_0", "phi_mu_f0"]
            else:
                names = ["slowMuonPerc", "fastMuonPerc"]
    
            row = 0
            for name in names:
                sizer.Add(self.fields[name], pos=(row, 1), border=5, flag=wx.ALIGN_LEFT | wx.ALL | wx.EXPAND)
                sizer.Add(self.error_labels[name], pos=(row, 2), border=5, flag=wx.ALIGN_LEFT | wx.ALL)
                row += 1
    
            self.paramsPanel.SetSizer(sizer)
            self.paramsPanel.Layout()
            self.ConfigureGrid()
            self.CheckStatus()
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.StaticText(self.paramsPanel, wx.ID_ANY, "You need to select a Nuclide\nbefore you can configure an Experiment's Parameters"), border=5, flag=wx.ALL | wx.ALIGN_TOP)
            self.paramsPanel.SetSizer(sizer)
            self.paramsPanel.Layout()
            
            
    def UpdateFactors(self, workflow):
        self.factorPanel.DestroyChildren()
        self.factorPanel.SetSizer(None)
        
        factors = self.repoman.GetModel("Factors")
        for name in factors.names():
            try:
                factor = factors.get(name)
                self.factorPanel.Unbind(wx.EVT_COMBOBOX, self.fields[factor.get_name()])
            except:
                pass
            try:
                factor = factors.get(name)
                del self.fields[factor.get_name()]
                del self.values[factor.get_name()]
                
            except:
                pass

        if workflow is not None:
            sizer = wx.GridBagSizer(10, 10)
            
            row = 0
            
            facts = workflow.get_factors()
            for name in facts:
                factor = factors.get(name)
                modes = factor.get_mode_names()
                
                modes.insert(0, "Select Value")
                
                sizer.Add(wx.StaticText(self.factorPanel, wx.ID_ANY, ExperimentUtils.display_name[factor.get_name()] + ":"), pos=(row, 0), border=5, flag=wx.ALIGN_RIGHT | wx.ALL)
                
                self.fields[factor.get_name()] = wx.ComboBox(self.factorPanel, wx.ID_ANY, value="Select Value", choices=modes, style=wx.CB_DROPDOWN | wx.CB_READONLY, name=factor.get_name())
                self.values[factor.get_name()] = "Not Selected"
                
                sizer.Add(self.fields[factor.get_name()], pos=(row, 1), border=5, flag=wx.ALIGN_LEFT | wx.ALL | wx.EXPAND)
                
                self.factorPanel.Bind(wx.EVT_COMBOBOX, self.OnFactorSelect, self.fields[factor.get_name()])
                
                row += 1
                
            self.factorPanel.SetSizer(sizer)
            self.factorPanel.Layout()
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.StaticText(self.factorPanel, wx.ID_ANY, "You need to select a Calibration Workflow\nbefore you can configure an Experiment's Factors"), border=5, flag=wx.ALL | wx.ALIGN_TOP)
            self.factorPanel.SetSizer(sizer)
            self.factorPanel.Layout()
            
    def OnFactorSelect(self, event):
        name = event.GetEventObject().GetName()
        value = event.GetEventObject().GetStringSelection()
        if value != "Select Value":
            self.values[name] = value
        else:
            self.values[name] = "Not Selected"
        self.ConfigureGrid()
        self.CheckStatus()
        
    def OnParamUpdate(self, event):
        name = event.GetEventObject().GetName()
        value = event.GetEventObject().GetValue()
        try:
            self.values[name] = float(value)
            self.error_labels[name].SetLabel('                         ')
        except:
            self.values[name] = 'Invalid: Need Float'
            self.error_labels[name].SetLabel('<-- Invalid: Need Float')
        self.fields[name].GetParent().Refresh()
        self.ConfigureGrid()
        self.CheckStatus()

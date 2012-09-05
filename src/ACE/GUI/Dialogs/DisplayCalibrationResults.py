"""
DisplayCalibrationResults.py

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

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure

from numpy import sort, transpose

import wx

from ACE.GUI.Util.ExperimentUtils import ExperimentUtils
from ACE.GUI.Util.FancyTextRenderer import FancyTextRenderer

class DisplayCalibrationResults(wx.Dialog):
    
    def __init__(self, parent, plot_data, experiment):
        wx.Dialog.__init__(self, parent, -1, 'Calibration Results')

        self.grid   = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1,1)
        self.grid.SetCellValue(0,0, "Select one or more Experiments")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "No Experiments Selected")
        self.grid.AutoSize()
        self.grid.EnableEditing(False)
        self.grid.SetDefaultRenderer(FancyTextRenderer())
        
        ExperimentUtils.InstallGridHint(self.grid, ExperimentUtils.GetToolTipString)
        
        self.ConfigureGrid(experiment)
        
        self.fig = Figure((9,8), 75)
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)

        RHS = plot_data["RHS"]
        yhat = plot_data["yhat"]
        Inv_calc_err = plot_data["Inv_calc_err"]
        Inv_meas_err = plot_data["Inv_meas_err"]
        
        if experiment['nuclide'] == '36Cl':

            ax = self.fig.add_subplot(111)
            ax.plot(RHS,yhat,'o')
            ax.plot(sort(RHS,0,'mergesort'),sort(RHS,0,'mergesort')) # y = x
            ax.errorbar(RHS,transpose(yhat),Inv_calc_err,Inv_meas_err,fmt='b.', ecolor=None)
            ax.set_title('Calibration Results for Experiment: %s' % (experiment['name']))
            ax.set_ylabel('Modelled Inventory (No Muon Contribution)')
            ax.set_xlabel('Observed Inventory - Muon Contribution')
            textlabel = "Ca Production rate =  %3.2f +- %3.2f  atoms / g / yr" % (float(experiment["psi_ca_0"] * 1.502E22) , float(experiment["psi_ca_uncertainty"] * 1.502E22))
            ax.text(0.05, 0.90,textlabel,transform = ax.transAxes, size = 12)
            textlabel = "K  Production rate = %3.2f +- %3.2f  atoms / g / yr"  % (float(experiment["psi_k_0"] * 1.54E22), float(experiment["psi_k_uncertainty"] * 1.54E22))
            ax.text(0.05, 0.85,textlabel,transform = ax.transAxes, size = 12)
            textlabel = "N  Production rate = %3.2f +- %3.2f  atoms / g / yr" % (float(experiment["Pf_0"]), float(experiment["Pf_uncertainty"]))
            ax.text(0.05, 0.80,textlabel,transform = ax.transAxes, size = 12)
            textlabel = "Reduced Chi-Square = %3.2f"  % float(experiment["chi_square"])
            ax.text(0.05, 0.75,textlabel,transform = ax.transAxes, size = 12)
            ax.grid()

        else:
            
            LHS = plot_data["LHS"]
            j = 0
            yhatList = []
            for i in range(experiment['sample_size']):
                yhatList.append(0.0)
            
            while j <= i:
                yhatList[j] = float(experiment["psi_spallation_nuclide"] * LHS[j][0])
                j += 1 
            
            # Plot up
            ax = self.fig.add_subplot(111)
            ax.plot(RHS,yhatList,'o')
            sortedRHS = sort(RHS, 0, 'mergesort')
            ax.plot(sortedRHS,sortedRHS) # Plot y = x  
            ax.errorbar(RHS,yhatList,Inv_calc_err,Inv_meas_err,fmt='b.', ecolor=None)
            textlabel = "Calibration Results for Experiment: %s" % (experiment['name'])
            ax.set_title(textlabel)
            ax.set_xlabel('Observed Inventory - Muon Contribution')
            ax.set_ylabel('Modelled Inventory (No Muon Contribution)')
            textlabel = "Production rate = %3.2f +- %3.2f  atoms / g / yr" % (float(experiment["psi_spallation_nuclide"]), float(experiment["psi_spallation_uncertainty"]))
            ax.text(0.05, 0.90,textlabel,transform = ax.transAxes,size = 14)
            textlabel = "Reduced Chi-Square = %3.2f" % float(experiment["chi_square"])
            ax.text(0.05, 0.85,textlabel,transform = ax.transAxes,size = 14)
            ax.grid()
        
        questionLabel = wx.StaticText(self, wx.ID_ANY, "Do you want to save the results of this calibration?")

        ok_button     = wx.Button(self, wx.ID_OK, "Yes")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "No")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(ok_button,    border=5, flag=wx.ALL)
        buttonSizer.Add(cancel_button, border=5, flag=wx.ALL)

        infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        infoSizer.Add(self.grid, border=5, proportion=1, flag=wx.EXPAND|wx.ALL)
        infoSizer.Add(self.canvas, border=5, proportion=2, flag=wx.EXPAND|wx.ALL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(infoSizer, border=5, proportion=1, flag=wx.ALL|wx.EXPAND)
        sizer.Add(questionLabel, border=5, flag=wx.ALL|wx.CENTER)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL|wx.CENTER)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Centre()
        
    def ConfigureGrid(self, experiment):
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        names  = []
        labels = []
        
        if experiment['nuclide'] == '36Cl':
            names = ["psi_ca_0", "psi_k_0", "Pf_0", "psi_ca_uncertainty", "psi_k_uncertainty", "Pf_uncertainty", "chi_square", "sample_size", "probability"]
            labels = ["Calcium Production", "Potassium Production", "Neutron Production", "1-Sigma Calcium", "1-Sigma Potassium", "1-Sigma Neutron", "Chi Square", "Sample Size", "Regression Probability"]
        else:
            names = ["psi_spallation_nuclide", "psi_spallation_uncertainty", "post_calibrated_slowMuon", "post_calibrated_fastMuon", "chi_square", "sample_size", "probability"]
            labels = ["Spallation Production", "1-Sigma Spallation", "Final Percent Slow Muon", "Final Percent Fast Muon", "Chi Square", "Sample Size", "Regression Probability"]
            
        self.grid.AppendRows(len(names))
        self.grid.AppendCols(1)
        
        self.grid.SetColLabelValue(0, experiment['name'])
        
        maxName = ""
        index = 0
        for label in labels:
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
        
        row = 0
        for name in names:
            try:
                self.grid.SetCellValue(row, 0, "<FancyText>%s</FancyText>" % (ExperimentUtils.GetGridValue(experiment, name)))
            except:
                pass
            row += 1
            
        self.grid.AutoSize()
        
        h,w = self.grid.GetSize()
        self.grid.SetSize((h+1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
"""
ExperimentUtils.py

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

class ExperimentUtils(object):

    display_name = {}

    display_name['name'] = 'Name'
    display_name['nuclide'] = 'Nuclide'
    display_name['timestep'] = 'Time Step'
    display_name['calibration'] = 'Calibration Workflow'
    display_name['calibration_set'] = 'Calibration Data Set'
    display_name['dating'] = 'Dating Workflow'

    display_name['geomagneticLatitude']  = 'Geomagnetic Latitude'
    display_name['geographicScaling']    = 'Scaling Model'
    display_name['geomagneticIntensity'] = 'Geomagnetic Intensity'
    display_name['seaLevel']             = 'Sea Level'

    display_name['psi_mu_0']     = 'Slow Muon Rate'
    display_name['phi_mu_f0']    = 'Fast Muon Flux'
    display_name['slowMuonPerc'] = 'Percent Slow Muon Rate'
    display_name['fastMuonPerc'] = 'Percent Fast Muon Rate'

    display_name['post_calibrated_slowMuon'] = 'Final Percent Slow Muon'
    display_name['post_calibrated_fastMuon'] = 'Final Percent Fast Muon'

    display_name['psi_k_0']                = 'Potassium Production'
    display_name['Pf_0']                   = 'Neutron Production'
    display_name['psi_ca_0']               = 'Calcium Production'
    display_name['psi_spallation_nuclide'] = 'Spallation Production'

    display_name['psi_ca_uncertainty']         = '1-Sigma Calcium'
    display_name['psi_k_uncertainty']          = '1-Sigma Potassium'
    display_name['Pf_uncertainty']             = '1-Sigma Neutron'
    display_name['psi_spallation_uncertainty'] = '1-Sigma Spallation'
    
    display_name['probability']            = 'Regression Probability'
    display_name['chi_square']             = 'Chi Square'
    display_name['sample_size']            = 'Sample Size'

    tooltip = {}
    
    tooltip['Name'] = 'Name of Experiment'
    tooltip['Nuclide'] = 'Choice of Nuclide used in Experiment'
    tooltip['Time Step'] = 'Time Interval used to Simulate Inventory Change'
    tooltip['Calibration Workflow'] = 'Calibration Workflow'
    tooltip['Calibration Data Set'] = 'Data Set used to determine HLSL Production Rates'
    tooltip['Dating Workflow'] = 'Dating Workflow'

    tooltip['Geomagnetic Latitude'] = 'Geomagnetic Latitude Reconstruction'
    tooltip['Scaling Model'] = 'Atmospheric/Geomagnetic Attenuation Model'
    tooltip['Geomagnetic Intensity'] = 'Geomagnetic Intensity Reconstruction'
    tooltip['Sea Level'] = 'Eustatic Sea Level Reconstruction'

    tooltip['Slow Muon Rate'] = 'Slow Negative Muon Stopping Rate'
    tooltip['Fast Muon Flux'] = 'Fast Muon Flux '
    tooltip['Percent Slow Muon Rate'] = 'Slow Muon Percentage Production Rate'
    tooltip['Percent Fast Muon Rate'] = 'Fast Muon Percentage Production Rate '

    tooltip['Final Percent Slow Muon'] = 'Post Calibrated Slow Muon Percentage Production Rate'
    tooltip['Final Percent Fast Muon'] = 'Post Calibrated Fast Muon Percentage Production Rate'

    tooltip['Potassium Production'] = 'HLSL Production Rate due to Potassium Spallation'
    tooltip['Neutron Production'] = 'HLSL Production Rate due to Fast Neutrons'
    tooltip['Calcium Production'] = 'HLSL Production Rate due to Calcium Spallation'
    tooltip['Spallation Production'] = 'HLSL Production Rate due to Spallation'

    tooltip['1-Sigma Calcium'] = '1-Sigma Uncertainty in Calcium Spallation Production Rate'
    tooltip['1-Sigma Potassium'] = '1-Sigma Uncertainty in Potassium Spallation Production Rate'
    tooltip['1-Sigma Neutron'] = '1-Sigma Uncertainty in Fast Neutron Production Rate '
    tooltip['1-Sigma Spallation'] = '1-Sigma Uncertainty in Spallation Production Rate'
    
    tooltip['Regression Probability'] = 'Probability that Correlation is Not Random'
    tooltip['Chi Square'] = 'Reduced Chi Square'
    tooltip['Sample Size'] = 'Number of Samples in Calibration Database'

    units = {}

    units['name'] = ''
    units['nuclide']         = ''
    units['timestep']        = 'yr'
    units['calibration']     = ''
    units['calibration_set'] = ''
    units['dating']          = ''

    units['geomagneticLatitude']  = ''
    units['geographicScaling']    = ''
    units['geomagneticIntensity'] = ''
    units['seaLevel']             = ''

    units['psi_mu_0']     = 'muons cm<sup>-2</sup> yr<sup>-1</sup>'
    units['phi_mu_f0']    = 'muons cm<sup>-2</sup> yr<sup>-1</sup>'
    units['slowMuonPerc'] = '%'
    units['fastMuonPerc'] = '%'

    units['post_calibrated_slowMuon'] = '%'
    units['post_calibrated_fastMuon'] = '%'

    units['psi_k_0']                = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'
    units['Pf_0']                   = 'neutrons g<sup>-1</sup> yr<sup>-1</sup>'
    units['psi_ca_0']               = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'
    units['psi_spallation_nuclide'] = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'

    units['psi_ca_uncertainty']         = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'
    units['psi_k_uncertainty']          = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'
    units['Pf_uncertainty']             = 'neutrons g<sup>-1</sup> yr<sup>-1</sup>'
    units['psi_spallation_uncertainty'] = 'atoms g<sup>-1</sup> yr<sup>-1</sup>'
    
    units['probability']            = '%'
    units['chi_square']             = ''
    units['sample_size']            = ''

    @staticmethod
    def GetToolTipString(grid, row, col):
        try:
            return ExperimentUtils.tooltip[grid.GetRowLabelValue(row)]
        except:
            return ""

    @staticmethod
    def InstallGridHint(grid, rowcolhintcallback):
        prev_rowcol = [None,None]
        def OnMouseMotion(evt):
            # evt.GetRow() and evt.GetCol() would be nice to have here,
            # but as this is a mouse event, not a grid event, they are not
            # available and we need to compute them by hand.
            x, y = grid.CalcUnscrolledPosition(evt.GetPosition())
            row = grid.YToRow(y)
            col = grid.XToCol(x)

            if (row,col) != prev_rowcol and row >= 0 and col >= 0:
                prev_rowcol[:] = [row,col]
                hinttext = rowcolhintcallback(grid, row, col)
                if hinttext is None:
                    hinttext = ''
                grid.GetGridRowLabelWindow().SetToolTipString(hinttext)
            evt.Skip()

        wx.EVT_MOTION(grid.GetGridRowLabelWindow(), OnMouseMotion)

    @staticmethod
    def GetGridValue(exp, label):
        try:
            val = exp[label]
        except:
            return ''
        try:
            if val.startswith('Not') or val.startswith('Invalid'):
                return val
        except:
            pass        
        if label.startswith('psi_ca'):
            val = val * 1.502E22
        if label.startswith('psi_k'):
            val = val * 1.54E22
        value = ''
        if isinstance(val, (str, unicode)):
            value = "%s %s" % (val, ExperimentUtils.units[label])
        elif isinstance(val, int):
            value = "%d %s" % (val, ExperimentUtils.units[label])
        else:
            value = "%.2f %s" % (val, ExperimentUtils.units[label])
        return value.strip()
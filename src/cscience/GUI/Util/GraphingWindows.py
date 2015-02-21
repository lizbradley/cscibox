""";
Graphing.py

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
from cscience.GUI.Util.SampleCollection import SampleCollection

from cscience import datastore

from cscience.GUI.Util.Graphing import Plotter, PlotPoint, PlotCanvas, SetPlotLabels

from cscience.GUI.Util.CalGraphingToolbar import Toolbar
from cscience.GUI.Util.CalGraphingOptionsPane import OptionsPane

class PlotWindow(wx.Frame):

    def __init__(self, parent, samples):
        # samples is in this case a list of
        # virtual samples 

        self._m_samples = SampleCollection(samples);

        print("Keys: " + str(self._m_samples.get_numeric_attributes()));

        start_pos = parent.GetPosition()
        start_pos.x += 50
        start_pos.y += 100

        # initialize the window as a frame
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'],
                                         pos=start_pos)


        # list of possible independent variables
        independent_choices = self._m_samples.get_numeric_attributes()

        sizer = wx.GridBagSizer()

        _m_options_pane = self.build_options_pane(self, samples)

        # Create the toolbar and hook it up so that when the options
        # button is pressed, the options pane is toggled
        self._m_toolbar = toolbar = self.build_toolbar(self, independent_choices)


        toolbar.on_options_pressed_do( lambda:
            # uncollapse the options pane with the button is pressed
            _m_options_pane.Collapse( not _m_options_pane.IsCollapsed() )
        )

        toolbar.on_invar_changed_do( lambda x: 
            self.when_independent_variable_changes(x)
        )

        toolbar.on_depvar_changed_do( lambda x:
            self.when_dependent_variable_changes(x)
        )

        def options_do(b):
            self._m_plot_canvas.get_options().enable_legend( b )
            self._m_plot_canvas.update_graph()
        toolbar.on_legend_pressed_do(options_do)
        
        sizer.Add(toolbar, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND)

        self._m_plot_canvas = self.build_plot(self)
        sizer.Add(self._m_plot_canvas, wx.GBPosition(1, 0),
                    wx.GBSpan(1, 1), wx.EXPAND)
        # This is just for testing {;
        # A pointset is simply a set of points used for graphing
        l_Plotter = Plotter()
        self._m_plot_canvas.add_pointset(0,
            [PlotPoint(i,i**2,0,0) for i in range(0,10)],
            Plotter()) 
        # }

        sizer.Add(_m_options_pane,
                    wx.GBPosition(0, 1), wx.GBSpan(2, 1), wx.EXPAND)

        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableRow(1, 0)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def build_pointset(self):
        ivar = self._m_toolbar.get_independent_variable()
        dvars = self._m_toolbar.get_dependent_variables()
        if not ivar:
            return

        self._m_plot_canvas.clear()
        self._m_plot_canvas.clear_pointset()

        identity = 0;
        print ("DVARS: %s" % (dvars,))

        for (dvar,opts) in dvars:
            pointset = self._m_samples.get_pointset(ivar, dvar)
    
            l_plotter = Plotter(opts)
    
            print ("Plotter opts %s %s" % (opts.color, opts.fmt))
            self._m_plot_canvas.add_pointset(identity, pointset, l_plotter);
            identity += 1

        self._m_plot_canvas.update_graph()


    def when_independent_variable_changes(self, x):
        print ("Independent variable has changed: " +
            str(self._m_toolbar.get_independent_variable()))
        self.build_pointset()
        

    def when_dependent_variable_changes(self, x):
        print ("Dependent variable has changed: " + 
            str(self._m_toolbar.get_dependent_variables()) )
        self.build_pointset()

    def build_options_pane(self, parent, samples):
        selected = [sample['computation plan'] 
                        for sample in samples]
        ret = OptionsPane(self, list(set(selected))) ;
        ret.Expand()
        return ret
    
    def build_plot(self, parent):
        ret = PlotCanvas(parent)
        return ret;

    def build_toolbar(self, parent, independent_choice):
        # The toolbar for the window
        ret = Toolbar(parent, independent_choice)
        return ret
            
        



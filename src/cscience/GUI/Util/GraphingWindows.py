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
import os

from cscience import datastore

from cscience.GUI.Util.SampleCollection import SampleCollection
from cscience.GUI.Util import graph

from cscience.GUI.Util.widgets import Toolbar, OptionsPane

def get_distribution(original_point): # -> Maybe [PlotPoint]
    dist = original_point.uncertainty.distribution
    if hasattr(dist, "x"):
        x_points = dist.x
        y_points = dist.y
        return [graph.PlotPoint(x, y, None, None, None) for (x,y) in zip(x_points, y_points)]
    else:
        return None

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

        # the frame used to sore the options pane
        self._m_options_frame = graph.FrameWrappedPanel()

        self._m_options_frame.Bind(wx.EVT_CLOSE, lambda _: self._m_options_frame.Hide())

        self._m_options_pane = self.build_options_pane(self._m_options_frame.get_panel(), samples)
        self._m_options_frame.set_panel(self._m_options_pane)

        def new_options_do():
            options = self._m_options_pane.get_canvas_options()
            print("Options were just pressed " + str(options))
            self._m_plot_canvas.set_options(options)

        self._m_options_frame.set_ok_listener(new_options_do)

        # Create the toolbar and hook it up so that when the options
        # button is pressed, the options pane is toggled

        computation_plans = [sample['computation plan'] for sample in samples]
        self._m_toolbar = toolbar = self.build_toolbar(self, independent_choices, computation_plans)


        toolbar.on_options_pressed_do(self._m_options_frame.ShowModal)
        toolbar.on_invar_changed_do(self.when_independent_variable_changes)
        toolbar.on_depvar_changed_do(self.when_dependent_variable_changes)
        toolbar.on_export_pressed_do(self.when_export_pressed)


        self._m_plot_canvas = self.build_plot(self)

        # plot canvases for when the user clicks
        # on a point. These show the distribution of
        # the variables at play
        self._m_zoom_plot_canvas = self.build_plot(self)
        self._m_zoom_plot_canvas2 = self.build_plot(self)

        def collapse():
            self._m_zoom_plot_canvas.Hide()
            self._m_zoom_plot_canvas2.Hide()
            self.Layout()
            self.Fit()

        toolbar.on_exit_pressed_do(collapse)
        
        # This is just for testing {;
        # A pointset is simply a set of points used for graphing
        # l_Plotter = graph.Plotter()
        # self._m_plot_canvas.add_pointset(0,
        #     [graph.PlotPoint(i,i**2,0,0) for i in range(0,10)],
        #      graph.Plotter()) 
        # }

        sizer.Add(self._m_toolbar,wx.GBPosition(0,0),wx.GBSpan(1,3),wx.EXPAND)
        sizer.Add(self._m_plot_canvas,wx.GBPosition(1,0),wx.GBSpan(2,2),wx.EXPAND)

        self._m_zoom_plot_canvas.SetMaxSize((100,100))
        self._m_zoom_plot_canvas.Hide();
        self._m_zoom_plot_canvas2.Hide();

        sizer.Add(self._m_zoom_plot_canvas, (1,2), (1,1), wx.EXPAND)
        sizer.Add(self._m_zoom_plot_canvas2, (2,2), (1,1), wx.EXPAND)


        # this is called when we zoom in on a point
        def show_zoom(point):
            # show the zoom for the C14 age of the point
            print point.xorig
            print point.yorig

            # get the distributions for both the independent
            # and dependent variables
            plot_points_x = get_distribution(point.xorig)
            plot_points_y = get_distribution(point.yorig)

            # plot the distributions as a line
            plot_options = graph.PlotOptions()
            plot_options.fmt = "-"

            if plot_points_x:
                # plot if and only if there is actually something to plot
                # (not all points have distributions associated with them)
                self._m_zoom_plot_canvas.add_pointset(0, graph.PointSet(plot_points_x, ""), 
                                                      graph.Plotter(plot_options))
            else:
                # if there is nothing to plot, clear the graph
                self._m_zoom_plot_canvas.clear()

            if plot_points_y:
                print "test 2"
                self._m_zoom_plot_canvas2.add_pointset(0, graph.PointSet(plot_points_y, ""), 
                                                       graph.Plotter(plot_options))
            else:
                self._m_zoom_plot_canvas2.clear()

            self._m_zoom_plot_canvas.update_graph()
            self._m_zoom_plot_canvas2.update_graph()

            self._m_zoom_plot_canvas.Show()
            self._m_zoom_plot_canvas2.Show()

            self.Layout()
            self.Fit()

        self._m_plot_canvas.set_pick_listener(show_zoom)

        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)

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
            pointset = self._m_samples.get_pointset(ivar, dvar, opts.computation_plan)
    
            l_plotter = graph.Plotter(opts)
    
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

    def when_export_pressed(self):
        l_file_dialog = wx.FileDialog(
               self, message="Export plot as ...", defaultDir=os.getcwd(), 
                defaultFile="", wildcard="Scalable Vector Graphics (*.svg)|*.svg", style=wx.SAVE
                )
        if l_file_dialog.ShowModal() == wx.ID_OK:
            path = l_file_dialog.GetPath()
            print "Exporting to file:", path
            self._m_plot_canvas.export_to_file(path)
        l_file_dialog.Destroy()

    def build_options_pane(self, parent, samples):
        selected = [sample['computation plan'] 
                        for sample in samples]
        ret = OptionsPane(parent, list(set(selected))) ;
        return ret
    
    def build_plot(self, parent):
        ret = graph.PlotCanvas(parent)
        return ret;

    def build_toolbar(self, parent, independent_choice, computation_plans):
        # The toolbar for the window
        ret = Toolbar(parent, independent_choice, list(set(computation_plans)))
        return ret
            
        



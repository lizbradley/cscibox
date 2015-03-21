"""
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

import matplotlib
matplotlib.use( 'WXAgg' )

import matplotlib.pyplot as plt
import matplotlib.backends.backend_wxagg as wxagg

from scipy.interpolate import interp1d
import numpy as np
import wx

from cscience.GUI.Util.graph.PlotCanvasOptions import PlotCanvasOptions

# interp_func = interp1d([float(i) for i in x], [float(i) for i in y], 
#                        bounds_error=False, fill_value=0, kind='cubic')
# new_x = arange(min(x), max(x), abs(max(x)-min(x))/100.0)
# plot.plot(new_x, interp_func(new_x), ''.join((color,'-')), label='%s_%s'%(lab,'cubic_interp'))

class LinearInterpolationStrategy:
    def __init__(self):
        pass
    def interpolate(self, x, y):
        self = self # shutup pylint
        return (x, y)

class SciInterpolationStrategy:
    def __init__(self, kind):
        self.kind = kind

    def interpolate(self, x, y):
        interp_func = interp1d([float(i) for i in x], [float(i) for i in y], 
                               bounds_error=False, fill_value=0, kind=self.kind)
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        return (new_x, interp_func(new_x))

# Options for a single xvy plot. Not the case for the
# more global options about plotting.
class PlotOptions:
    def __init__(self):
        self.color = (0,0,0)
        self.fmt = "o"
        self.interpolation_strategy = None

    # plot points on plot under the context
    # represented by this object
    #
    # points :: [PlotPoint]
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot):
        (xs, ys, _, _) = points.unzip_points()

        if self.interpolation_strategy:
            (xs, ys) = self.interpolation_strategy.interpolate(xs, ys)

        plot.plot(xs, ys, self.fmt, color="#%02x%02x%02x"%self.color, label=points.get_variable_name(), picker=5)

# glorified list of points. Can attach additional metadata to
# the list of point =s
class PointSet:
    # create a pointset from a list of plot points
    def __init__( self, plotpoints, vname ):
        self.m_plotpoints = plotpoints[:] # copy
        self.m_plotpoints.sort(key=lambda p: p.x)
        self.m_variable_name = vname

    def __getitem__(self, i):
        return self.m_plotpoints[i]

    def get_variable_name(self):
        return self.m_variable_name

    # returns a ([Num],[Num],[Num],[Num]) of
    # x, y, xorig, yorig
    def unzip_points(self):
        return unzip_plot_points(self.m_plotpoints)



class PlotPoint:
    # Potenitally change to have a more robutst
    # statistical distribution than just error bars
    # perhaps maybe?
    def __init__(self, x, y, xorig, yorig):
        self.x = x
        self.y = y
        
        self.xorig = xorig
        self.yorig = yorig

    def __str__(self):
        return "(%s,%s,%s,%s)" % (self.x, self.y, self.xorig, self.yorig)
    def __repr__(self):
        return self.__str__()

# :: [PlotPoints] -> ([float], [float], [float], [float])
#                      x's     y's       xerr's    yerr's
def unzip_plot_points( points ):
    return (
        [i.x    for i in points],
        [i.y    for i in points],
        [i.xorig for i in points],
        [i.yorig for i in points] )
        

class SetPlotLabels:    
    def __init__(self, xlab, ylab):
        self.x_lab = xlab
        self.y_lab = ylab

    def __call__(self, plot):
        plot.label_options.x_label = self.x_lab
        plot.label_options.y_label = self.y_lab
        plot.label_options.x_label_visible = True
        plot.label_options.y_label_visible = True
        
# This class just knows how to plot things.
# Nothing else. It works by having a pipeline
# associated with mutating the data and the plot
class Plotter:
    def __init__(self, opts=PlotOptions()):
        self.opts = opts

    # points :: [PlotPoint] 
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot) :
        opts = self.opts
        opts.plot_with( points, plot )
        
        

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self._m_plot = self.figure.add_subplot(1,1,1)
        self._m_pointset = {} # :: Int => (Plotter, [PlotPoint])
        self._m_canvas_options = PlotCanvasOptions()
        self._m_pick_listener = None
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self._m_pointset_table = {} # used to index into when there is a pick event

    def get_options(self):
        return self._m_canvas_options
    
    # identitiy :: int - the pointset identity
    # points    :: PointSet - the list of points and their error bars
    # plotter   :: Plotter - the plotter used to plot
    def add_pointset(self, identity, points, plotter):
        # add a pointset to the dictionary of pointsets.
        # This will allow the 
        self._m_pointset[identity] = (points, plotter)

    def clear_pointset(self):
        self._m_pointset = {}

    def on_pick(self, evt):
        label = evt.artist.get_label()
        index = evt.ind
        try:
            point = self._m_pointset_table[label][index[0]]
            self._m_pick_listener(point)
        except KeyError:
            print ("[WARN] - invalid key " + label)

    def set_pick_listener(self, l):
        self._m_pick_listener = l
        
    def delete_pointset(self, identity):
        # Python! Why no haz remove!!!
        del self._m_pointset[identity]

    def update_graph(self):
        print ("Updating graph")
        self._update_graph()

    def clear(self):
        self._m_plot.clear()
        self._m_pointset.clear()
        self.draw()

    def reapply_options(self):
        self._m_canvas_options.plot_with(self._m_pointset, self._m_plot)

    def _update_graph(self):
        self._m_plot.clear()
        self._m_pointset_table = {}
        # for now, plot everything on the same axis
        for (points, plotter) in self._m_pointset.values():
            self._m_pointset_table[points.get_variable_name()] = points
            plotter.plot_with(points, self._m_plot)

        self.reapply_options()

        self.draw()
        


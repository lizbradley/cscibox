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

# itertoos.x is stupidly verbose for how basic they are! Who
# claims that python in succinct!
from itertools import *

import matplotlib
matplotlib.use( 'WXAgg' )

import operator
import matplotlib.pyplot as plt
import quantities as pq
import matplotlib.backends.backend_wxagg as wxagg
from matplotlib.patches import Circle
from numpy import arange
from scipy.interpolate import interp1d
import wx

from cscience.GUI import events
from cscience import datastore
from matplotlib.offsetbox import AuxTransformBox, AnnotationBbox

class PlotErrorBarOptions:
    def __init__(self):
        self.label = ""
        self.fmt = 'r'
        self.enabled = False

    def plot_with( self, points, plot ):
        if self.enabled:
            (xs,ys,xerrs,yerrs) = unzip_plot_points( points )
            plot.plot( xs, ys, xerrs, yerrs, fmt=self.fmt, label=self.label )

class PlottingOptions:
    def __init__(self):
        self.fmt = "r"
        self.label = ""
        self.show_legend = False
        self.show_grid = False

    # plot points on plot under the context
    # represented by this object
    #
    # points :: [PlotPoint]
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot):
        (xs, ys, _, _) = unzip_plot_points(points)
        plot.plot(xs, ys, self.fmt, self.label)


        
class LabelOptions:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""

        self.x_label_visible = False
        self.y_label_visible = False

    def plot_with( self, _, plot ):
        plot.set_xlabel( self.x_label, self.x_label_visible )
        plot.set_ylabel( self.y_label, self.y_label_visible )


class PlotOptions:
    def __init__(self):
        self.errorbar_options = PlotErrorBarOptions()
        self.plotting_options = PlottingOptions()
        self.label_options = LabelOptions()

    def plot_with( self, points, plot ):
        self.errorbar_options.plot_with(points, plot)
        self.plotting_options.plot_with(points, plot)
        self.label_options.plot_with(points, plot)



class PlotPoint:
    # Potenitally change to have a more robutst
    # statistical distribution than just error bars
    # perhaps maybe?
    def __init__(self, x, y, xerr, yerr):
        self.x = x
        self.y = y
        self.xerr = xerr
        self.yerr = yerr

# :: [PlotPoints] -> ([float], [float], [float], [float])
#                      x's     y's       xerr's    yerr's
def unzip_plot_points( points ):
    return (
        [i.x    for i in points],
        [i.y    for i in points],
        [i.xerr for i in points],
        [i.yerr for i in points] )
        

# This class just knows how to plot things.
# Nothing else. It works by having a pipeline
# associated with mutating the data and the plot
class Plotter:
    def __init__(self):

        self.data_mutators = []
        self.plot_mutators = []

    # points :: [PlotPoint] 
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot) :
        opts = PlotOptions();

        for m in self.plot_mutators:
            m(opts)

        for m in self.data_mutators:
            points = m(points)

        opts.plot_with( points, plot )
        
    def set_data_mutators( self, mutators ):
        self.data_mutators = mutators

    def set_plot_mutators( self, mutators ):
        self.plot_mutators = mutators
        
    # first stage of the pipline. Mutators
    # take raw points and turn them into some
    # other form. Useful for inverting the axis
    # and maybe setting error bars
    #
    # mutators :: (const) [PlotPoint] -> [PlotPoint]
    #
    # mutators should not mutate the input
    def append_data_mutator(self, mutator):
        self.data_mutators.append(mutator)

    def insert_data_mutator(self, mutator, idx=0):
        self.data_mutators.insert(mutator, idx)

    def remove_data_mutator(self, mutator):
        self.data_mutators.remove(mutator)

    # The next set of function modifies the plot itself.
    # These are plot mutators. These are used for things
    # like being able to set the axis visible and showing
    # the grid.
    #
    # These mutators :: PlotOptions -> Void
    def append_plot_mutator(self, mutator):
        self.plot_mutators.append(mutator)

    def insert_plot_mutator(self, mutator, idx=0):
        self.plot_mutators.insert(mutator, idx)

    def remove_plot_mutator(self, mutator):
        self.plot_mutators.remove(mutator)
        

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self._m_plot = self.figure.add_subplot(1,1,1)
        self._m_pointset = {} # :: Int => (Plotter, [PlotPoint])
    
    # identitiy :: int
    # points    :: [PlotPoint]
    # plotter   :: Plotter
    def add_pointset(self, identity, points, plotter):
        # add a pointset to the dictionary of pointsets.
        # This will allow the 
        self._m_pointset[identity] = (points, plotter)

    def clear_pointset(self):
        self._m_pointset = {}

    def delete_pointset(self, identity):
        # Python! Why no haz remove!!!
        del self._m_pointset[identity]

    def update_graph(self):
        self._update_graph()

    def _update_graph(self):
        # for now, plot everything on the same axis
        for (points, plotter) in self._m_pointset.values():
            plotter.plot_with(points, self._m_plot)
        


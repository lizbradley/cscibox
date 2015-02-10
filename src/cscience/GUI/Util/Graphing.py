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
import wx

class PlotOptions:
    def __init__(self):
        self.color = (0,0,0)
        self.fmt = "o"

    # plot points on plot under the context
    # represented by this object
    #
    # points :: [PlotPoint]
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot):
        (xs, ys, _, _) = unzip_plot_points(points)
        plot.plot(xs, ys, self.fmt, color="#%02x%02x%02x"%self.color)




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
    
    # identitiy :: int - the pointset identity
    # points    :: [PlotPoint] - the list of points and their error bars
    # plotter   :: Plotter - the plotter used to plot
    def add_pointset(self, identity, points, plotter):
        # add a pointset to the dictionary of pointsets.
        # This will allow the 
        points = points[:]
        points.sort(key=lambda point: point.x) # sort by x element
        self._m_pointset[identity] = (points, plotter)

    def clear_pointset(self):
        self._m_pointset = {}

    def delete_pointset(self, identity):
        # Python! Why no haz remove!!!
        del self._m_pointset[identity]

    def update_graph(self):
        print ("Updating graph")
        self._update_graph()

    def clear(self):
        self._m_plot.clear()
        self.draw()

    def _update_graph(self):
        self._m_plot.clear()
        # for now, plot everything on the same axis
        for (points, plotter) in self._m_pointset.values():
            print ("Points " + str(points))
            plotter.plot_with(points, self._m_plot)

        self.draw()
        


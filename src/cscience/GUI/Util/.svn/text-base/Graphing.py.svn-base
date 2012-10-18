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

import pylab
import matplotlib.transforms
import matplotlib.backends.backend_wxagg as wxagg
import wx
        
class Plot:
    figNum = 1
    
    def __init__(self, sampleSet, xatt, yatt):
        self.samples = sampleSet[:]
        self.xatt = xatt
        self.yatt = yatt
        
        self.titleSet = False
        #self.lines = []
        self.__createFigure()
        
    def showFigure(self):
        self.parent = wxagg.FigureFrameWxAgg(Plot.figNum, self.fig)
        Plot.figNum += 1
        self.parent.Bind(wx.EVT_CLOSE, self.onClose)
        self.canvas = self.parent.get_canvas(self.fig)
        self.__bindEvents()
        self.parent.Show()
            
    def makeFigure(self, parent):
        self.parent = parent
        self.canvas = wxagg.FigureCanvasWxAgg(self.parent, -1, self.fig)
        self.__bindEvents()
        
        return self.canvas
    
    def __bindEvents(self):
        self.canvas.mpl_connect('draw_event', self.drawArea)
        self.canvas.mpl_connect('pick_event', self.samplePicker)
        
    def setTitle(self, title):
        self.titleSet = True
        self.figure.set_title(title)
        
    def plotLine(self, slope, intercept):
        xbounds = self.figure.get_xbound()
        self.figure.plot(xbounds, [(val * slope) + intercept for val in xbounds], 'r--')
        
    def onClose(self, evt):
        #print 'trying to close!'
        self.parent.Destroy()
        
        return True
        
    def indexStrings(self, strings):
        labelList = []
        indexList = []
        
        for x in strings:
            try:
                indexList.append(labelList.index(x))
            except ValueError:
                labelList.append(x)
                indexList.append(len(labelList)-1)
        
        return indexList, labelList
    
    def __createFigure(self):
        if all([sample[self.xatt] is None or sample[self.yatt] is None for sample in self.samples]):
            return
        self.ids, xvals, yvals, xerr, yerr = \
          zip(*[[sample['id'], sample[self.xatt], sample[self.yatt], 
                 sample[self.xatt + ' uncertainty'], sample[self.yatt + ' uncertainty']] 
                for sample in self.samples if
                (sample[self.xatt] is not None and sample[self.yatt] is not None)])
        
        xlabels = None
        ylabels = None
        
        self.fig = pylab.Figure()
        self.figure = self.fig.add_subplot(111)

        if isinstance(xvals[0], (str, unicode)):
            xvals, xlabels = self.indexStrings(xvals)
            #horrible hack to keep these labels from being drawn inside the graph area
            xlabels = map(lambda lbl: lbl + '      ', xlabels)

        if isinstance(yvals[0], (str, unicode)): 
            yvals, ylabels = self.indexStrings(yvals)
 
        self.figure.set_title('Click for Sample Names')

        #add uncertainties if they exist
        if all(xerr):
            self.figure.errorbar(x=xvals, y=yvals, xerr=xerr, yerr=None, fmt='bs')
        if all(yerr):
            self.figure.errorbar(x=xvals, y=yvals, xerr=None, yerr=yerr, fmt='bs')

        points = self.figure.plot(xvals, yvals, 'gs', picker=self.samplePicker)[0]
        self.figure.grid()

        if xlabels is not None:
            self.figure.set_xticks(range(len(xlabels)))
            self.figure.set_xlim(-0.5, len(xlabels) - 0.5)
            
            if len(xlabels) < 40:
                labels = self.figure.set_xticklabels(xlabels, rotation='vertical',
                              verticalalignment='top', horizontalalignment='center')
            #else:
            #    self.figure.setp(self.figure.gca(), xticklabels=[])

        if ylabels is not None:
            self.figure.set_yticks(range(len(ylabels)))
            self.figure.set_ylim(-0.5, len(ylabels) - 0.5)
            
            if len(ylabels) < 40:
                self.figure.set_yticklabels(ylabels) 
            #else:
            #    pylab.setp(pylab.gca(), yticklabels=[])
        
        self.xlabel = self.figure.set_xlabel(self.xatt)
        self.ylabel = self.figure.set_ylabel(self.yatt)
        
    def drawArea(self, event):
        #drawing location of the x axis label
        xbox = matplotlib.transforms.Bbox(
                    self.xlabel.get_window_extent().inverse_transformed(
                                                            self.fig.transFigure))
        if xbox.y0 < 0:
            self.fig.subplots_adjust(bottom=(self.fig.subplotpars.bottom - (xbox.y0 * 1.1)))
            
        #drawing location of the y axis label
        ybox = matplotlib.transforms.Bbox(
                    self.ylabel.get_window_extent().inverse_transformed(
                                                            self.fig.transFigure))
        if ybox.x0 < 0:
           # print self.canvas
            self.fig.subplots_adjust(left=(self.fig.subplotpars.left - (ybox.x0 * 1.1)))
            
        if xbox.y0 < 0 or ybox.x0 < 0:
            self.canvas.draw()
            return False
        
    def samplePicker(self, points, mouseevent=None):
        #print 'picking a sample now'
        
        if mouseevent is None or mouseevent.xdata is None: 
            return (False, {})
        
        #we need to normalize distances to something more like what
        #the user sees on the screen (since the values passed are
        #graph coordinates, not pixel coordinates)
        xvals = points.get_xdata()
        yvals = points.get_ydata()
        xbounds = self.figure.get_xbound()
        ybounds = self.figure.get_ybound()
        xrange = xbounds[1] - xbounds[0]
        yrange = ybounds[1] - ybounds[0]
        
        assert xrange != 0 and yrange != 0
        
        #this is actually dist squared, of course
        distances = ((xvals - mouseevent.xdata)/xrange)**2 + \
                    ((yvals - mouseevent.ydata)/yrange)**2
                    
        allIndexes = map(lambda (x,y): ((y == min(distances)) and [x] or None), enumerate(distances))
        allIndexes = [ind[0] for ind in allIndexes if ind is not None]
        
        assert len(allIndexes) > 0
        
        pickedx = [xvals[ind] for ind in allIndexes]
        pickedy = [yvals[ind] for ind in allIndexes]
        
        props = {'ind':ind, 'pickx':pickedx, 'picky':pickedy}
        
        #if len(pickedx) == 1: #one sample has these coordinates
        #    self.figure.text(pickedx[0], pickedy[0], self.ids[allIndexes[0]])
        #else: #More than one sample has these coordinates
        samples = '\n'.join([self.ids[ind] for ind in allIndexes])
        self.figure.text(pickedx[0], pickedy[0], samples)
            
        if not self.titleSet:
            self.figure.set_title('')
            
        self.canvas.draw()
        return (True, props)
        
        
    

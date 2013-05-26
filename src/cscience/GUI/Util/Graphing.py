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

import itertools
import matplotlib.pyplot as plt
import matplotlib.backends.backend_wxagg as wxagg
import wx

from cscience import datastore


class PlotOptionsDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(PlotOptionsDialog, self).__init__(*args, **kwargs)
        
        numericatts = [att.name for att in datastore.sample_attributes if 
                       att.type_ in ('integer', 'float')]
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        rows = wx.BoxSizer(wx.HORIZONTAL)
        rows.Add(wx.StaticText(self, wx.ID_ANY, "Invariant Axis"))
        self.invarchoice = wx.Choice(self, wx.ID_ANY, choices=numericatts)
        rows.Add(self.invarchoice)
        self.invarchoice.SetStringSelection('depth')
        sizer.Add(rows)
        
        #TODO: more than one variant
        rows = wx.BoxSizer(wx.HORIZONTAL)
        rows.Add(wx.StaticText(self, wx.ID_ANY, "Variant Axis"))
        self.varchoice = wx.Choice(self, wx.ID_ANY, choices=numericatts)
        rows.Add(self.varchoice)
        self.varchoice.SetStringSelection("14C Age")
        sizer.Add(rows)
        
        #TODO: asymmetrical axes...
        rows = wx.BoxSizer(wx.HORIZONTAL)
        rows.Add(wx.StaticText(self, wx.ID_ANY, "Variant Axis Error Bars"))
        self.varerrchoice = wx.Choice(self, wx.ID_ANY, choices=numericatts)
        rows.Add(self.varerrchoice)
        self.varerrchoice.SetStringSelection('14C Age Error')
        sizer.Add(rows)
        
        rows = wx.BoxSizer(wx.HORIZONTAL)
        rows.Add(wx.StaticText(self, wx.ID_ANY, "Graph Invariant on"))
        self.yinvar = wx.RadioButton(self, wx.ID_ANY, 'y axis')
        self.xinvar = wx.RadioButton(self, wx.ID_ANY, 'x axis')
        rows.Add(self.yinvar)
        rows.Add(self.xinvar)
        sizer.Add(rows)
        self.xinvar.SetValue(True)
        
        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btnsizer)
        
        self.SetSizer(sizer)
        
    def get_options(self):
        return PlotOptions(self.invarchoice.GetStringSelection(),
                           varatts=[self.varchoice.GetStringSelection()],
                           varerrs=[(self.varerrchoice.GetStringSelection(),
                                     self.varerrchoice.GetStringSelection())],
                           invaraxis='y' if self.yinvar.GetValue() else 'x')


class PlotOptions(object):
    def __init__(self, invaratt, **kwargs):
        self.invaratt = invaratt
        self.invarerr = kwargs.get('invarerr', None)
        self.varatts = kwargs.get('varatts', ['Calibrated 14C Age'])
        self.varerrs = kwargs.get('varerrs', [('Calibrated 14C Age Error-', 
                                               'Calibrated 14C Age Error+')])
        self.invaraxis = kwargs.get('invaraxis', 'y')
        self.stacked = kwargs.get('stacked', False)
        
    @property
    def invarerr(self):
        return self._invarerr
    @invarerr.setter
    def invarerr(self, newval):
        if newval and len(newval != 2):
            self._invarerr = (newval, newval)
        else:
            self._invarerr = newval
        
    def add_att(self, att, err=None):
        self.varatts.append(att)
        #hack -- using len(2) to check if we are using bimodal errors -- just
        #forcing all errors to be bimodal for max simplicity.
        if err and len(err) != 2:
            self.varerrs.append((err, err))
        else:
            self.varerrs.append(err)
        
    def ok(self):
        #TODO: check that all the attributes being graphed are numeric
        #TODO: should implement a max # of plot atts...
        return bool(self.varatts)

class SamplePlot(object):
    #use shapes for different attribute plots, colors for different computations,
    #so black/white printouts are as legible as possible.
    #correction: if we're stacked, use shapes for comp plans...
    colorseries = 'brgmyck'
    shapeseries = 's^ov*p+hxD'
    
    def __init__(self, samples, options):
        #TODO: muck around with tick colors & positions to make what's being
        #displayed all supah clear!
        if not options.ok():
            raise TypeError('Cannot plot the current options zomg')
        self.options = options
        #we don't want to plot any samples where the invariant doesn't actually
        #exist, so we can filter those out now
        self.samples = filter(lambda s: s[options.invaratt] is not None, samples)
        
        #create the graphing figure and all the axes I want...
        if self.options.stacked:
            argset = {}
            if self.options.invaraxis == 'y':
                argset['ncols'] = len(self.options.varatts)
                argset['sharey'] = True
            else:
                argset['nrows'] = len(self.options.varatts)
                argset['sharex'] = True
            self.figure, self.plots = plt.subplots(**argset)
        else:
            #overlapping figures...
            self.figure = plt.Figure()
            self.figure.add_subplot(1, 1, 1)
            plot = self.figure.get_axes()[0]
            argset = {'frameon':False}
            if self.options.invaraxis == 'y':
                argset['sharey'] = plot
            else:
                argset['sharex'] = plot
            for i in xrange(1, len(self.options.varatts)):
                #TODO: muck w/ axes...
                self.figure.add_axes(plot.get_position(True), 
                                                       **argset)
            self.plots = self.figure.get_axes()
                
        for vatt, err, plot in zip(self.options.varatts, self.options.varerrs, self.plots):
            self.samples.sort(key=lambda s: (s['computation plan'], s[self.options.invaratt]))
            colors = itertools.cycle(self.colorseries)
            for cplan, sampleset in itertools.groupby(self.samples, key=lambda s: s['computation plan']):
                args = self.extract_graph_series(sampleset, vatt, err)
                
                if self.options.invaraxis == 'y':
                    plot.errorbar(x=args['var'], y=args['invar'], 
                                  xerr=args['verr'], yerr=args['ierr'], fmt=''.join((colors.next(),'o')))
                    plot.set_xlabel(vatt)
                    plot.set_ylabel(self.options.invaratt)
                else:
                    plot.errorbar(y=args['var'], x=args['invar'], 
                                  yerr=args['verr'], xerr=args['ierr'], fmt=''.join((colors.next(), 'o')))
                    plot.set_xlabel(self.options.invaratt)
                    plot.set_ylabel(vatt)
                #TODO: annotate points w/ their depth, if depth is not the invariant
                #SRS TODO: make sure there is a legend for all this foofrah
                #TODO: x label, y label, title...
        #TODO: get this thing working.
        #plt.tight_layout()
        
    def extract_graph_series(self, sampleset, att, err):
        plotargs = {'invar':[], 'var':[], 'depth':[], 'ierr':None, 'verr':None}
        if self.options.invarerr:
            plotargs['ierr'] = []
            def ierr(s):
                plotargs['ierr'].append((s[self.options.invarerr[0]] or 0, 
                                         s[self.options.invarerr[1]] or 0))
        else:
            def ierr(s):
                pass
        if err:
            plotargs['verr'] = []
            def verr(s):
                plotargs['verr'].append((s[err[0]] or 0, s[err[1]] or 0))
        else:
            def verr(s):
                pass
            
        for s in sampleset:
            if s[self.options.invaratt] is None or s[att] is None:
                continue
            if s[self.options.invaratt] > 999999 or s[att] > 999999:
                #hack to exclude huge #s coming out of current calcs...
                continue
            plotargs['invar'].append(s[self.options.invaratt])
            plotargs['var'].append(s[att])
            plotargs['depth'].append(s['depth'])
            ierr(s)
            verr(s)
            
        #change [(-, +), (-, +)...] to ([-, -, ...], [+, +, ...] since that's
        #the matplotlib format
        if self.options.invarerr:
            plotargs['ierr'] = zip(*plotargs['ierr'])
        if err:
            plotargs['verr'] = zip(*plotargs['verr'])
        return plotargs
    
class PlotWindow(wx.Frame):
    
    def __init__(self, parent, samples, options):
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'])
        self.canvas = PlotCanvas(self, samples, options)
#        TODO: Convince auto sizing to recognize the axes labels.
#        TODO: Have plot window appear near my window, not in the top left corner.
#                ...though this may be unnecessary when we switch to fancy docking.
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, flag=wx.ALL | wx.EXPAND, proportion=1, border=0)
        self.SetSizer(sizer)
        #TODO: can add lots of awesome menus & similar here now!

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    
    def __init__(self, parent, samples, options):
        self.plot = SamplePlot(samples, options)
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, self.plot.figure)
        

    

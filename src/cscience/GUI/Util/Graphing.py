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
import matplotlib
matplotlib.use( 'WXAgg' )

import matplotlib.pyplot as plt
import matplotlib.backends.backend_wxagg as wxagg
import wx

from cscience import datastore
from wx.lib.agw import aui
from wx.lib.agw import pycollapsiblepane

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
        self.picked_indices = {}
        
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
                    x = args['var']
                    y = args['invar']
                    xerr = args['verr']
                    yerr = args['ierr']
                    xlab = vatt
                    ylab = self.options.invaratt
                else:
                    x = args['invar']
                    y = args['var']
                    xerr = args['ierr']
                    yerr = args['verr']
                    xlab = self.options.invaratt
                    ylab = vatt
                
                self.picked_indices[cplan] = []    
                plot.plot(x, y, ''.join((colors.next(),'o')), label=cplan, 
                          picker=5)
                #We do the errorbars separately so that they don't get rendered
                #by the legend. Could also use a custom legend handler, but since
                #we're planning on displaying the error in morecomplicated
                #ways later, I thought separating the two made sense.
                plot.errorbar(x, y, xerr=xerr, yerr=yerr, label='_nolegend_',
                              fmt=None)
                plot.set_xlabel(xlab)
                plot.set_ylabel(ylab)
                plot.set_label(cplan)
                #TODO: annotate points w/ their depth, if depth is not the invariant
                #SRS TODO: make sure there is a legend for all this foofrah
                #TODO: x label, y label, title...
            plot.legend(loc='upper left',fontsize='small')
        #TODO: get this thing working.
        #plt.tight_layout()
    
    def on_pick(self, event):
        cplan = event.artist.get_label()
        xdata, ydata = event.artist.get_data()
        ind = event.ind
        print("On " + str(cplan) + ", picked: ",zip(xdata[ind],ydata[ind]))
        self.picked_indices[cplan].append(ind)
    
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
    
    def __init__(self, parent, samples):
        start_position = parent.GetPosition()
        start_position.x += 50
        start_position.y += 100 
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'],
                                         pos=start_position)
        
        
        self.samples = samples
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        self.toolbar = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORZ_TEXT)

        numericatts = [att.name for att in datastore.sample_attributes if 
                        att.type_ in ('integer', 'float')]

        self.radio_id = wx.NewId()
        self.choice_id = wx.NewId()
        
        self.xinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "")
        self.xinvar_radio.SetValue(True)
        self.toolbar.AddControl(self.xinvar_radio)

        self.x_choice = wx.Choice(self.toolbar, self.choice_id, choices=numericatts)
        self.x_choice.SetStringSelection('depth')
        self.toolbar.AddControl(self.x_choice)
        
        self.yinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "")
        self.toolbar.AddControl(self.yinvar_radio)
        
        self.y_choice = wx.Choice(self.toolbar, self.choice_id, choices=numericatts)
        self.y_choice.SetStringSelection('14C Age')
        self.toolbar.AddControl(self.y_choice)
        
        self.toolbar.AddSeparator()
        
        self.var_err_choice = wx.Choice(self.toolbar, self.choice_id, choices=numericatts)
        self.var_err_choice.SetStringSelection('14C Age Error')
        self.toolbar.AddControl(self.var_err_choice)
        
        self.toolbar.Realize()
        self.SetToolBar(self.toolbar)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnVariablesChanged, id=self.radio_id)
        self.Bind(wx.EVT_CHOICE, self.OnVariablesChanged, id=self.choice_id)
        
        self.OnVariablesChanged(None)
        
    def OnVariablesChanged(self, event):
        if(self.xinvar_radio.GetValue()):
            options = PlotOptions(self.x_choice.GetStringSelection(),
                                  varatts = [self.y_choice.GetStringSelection()],
                                  varerrs = [(self.var_err_choice.GetStringSelection(),
                                              self.var_err_choice.GetStringSelection())],
                                  invaraxis = 'x'
                                  )
        else:
            options = PlotOptions(self.y_choice.GetStringSelection(),
                      varatts = [self.x_choice.GetStringSelection()],
                      varerrs = [(self.var_err_choice.GetStringSelection(),
                                  self.var_err_choice.GetStringSelection())],
                      invaraxis = 'y'
                      )
        self.canvas = PlotCanvas(self, self.samples, options)
        self.GetSizer().Clear()
        self.GetSizer().Add(self.canvas, flag=wx.ALL | wx.EXPAND, proportion=1, 
                            border=0)
        #TODO: Figure out why the frame only auto-resizes correctly to shrink?
        self.SetSize(self.canvas.GetSize())
        self.Update()




class PlotCanvas(wxagg.FigureCanvasWxAgg):
    
    def __init__(self, parent, samples, options):
        self.plot = SamplePlot(samples, options)
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, self.plot.figure)
        
        
    def update(self, options):
        self.plot = SamplePlot(samples, options)
        self.Update()
        
        
    

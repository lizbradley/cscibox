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
        #TODO: HACK
        self.varerrs = []
        for varatt in self.varatts:
            self.varerrs.append((varatt+" Error", varatt+" Error"))
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


class PlotCanvas(wxagg.FigureCanvasWxAgg):
    
    colorseries = 'brgmyck'
    shapeseries = 's^ov*p+hxD'
    
    def __init__(self, parent, samples, options):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())
        self.samples = samples
        self.picked_indices = {}
        self.draw_graph(options)
        self.draw()
        
    def update_graph(self, options):
        self.figure.clear()
        self.draw_graph(options)
        self.draw()
        
    def draw_graph(self, options):
        samples = filter(lambda s: s[options.invaratt] is not None, self.samples)
        
        if options.stacked:
            argset = {}
            if options.invaraxis == 'y':
                nrows = 1
                ncols = len(options.varatts)
            else:
                nrows = len(options.varatts)
                ncols = 1
            ax0 = self.figure.add_subplot(nrows, ncols, 1)
            if options.invaraxis == 'y':
                sx = None
                sy = ax0
            else:
                sx = ax0
                sy = None
            for i in xrange(1, len(options.varatts)):
                self.figure.add_subplot(nrows, ncols, i+1, sharex=sx, sharey=sy)
            self.plots = self.figure.get_axes()
        else:
            #overlapping figures...
            plot = self.figure.add_subplot(1, 1, 1)
            argset = {'frameon':False}
            if options.invaraxis == 'y':
                argset['sharey'] = plot
            else:
                argset['sharex'] = plot
            for i in xrange(1, len(options.varatts)):
                #TODO: muck w/ axes...
                self.figure.add_axes(plot.get_position(True), 
                                                       **argset)
            self.plots = self.figure.get_axes()
            
        for vatt, err, plot in zip(options.varatts, options.varerrs, self.plots):
            self.samples.sort(key=lambda s: (s['computation plan'], s[options.invaratt]))
            colors = itertools.cycle(self.colorseries)
            for cplan, sampleset in itertools.groupby(self.samples, key=lambda s: s['computation plan']):
                args = self.extract_graph_series(sampleset, options, vatt, err)
                
                if options.invaraxis == 'y':
                    x = args['var']
                    y = args['invar']
                    xerr = args['verr']
                    yerr = args['ierr']
                    xlab = vatt
                    ylab = options.invaratt
                else:
                    x = args['invar']
                    y = args['var']
                    xerr = args['ierr']
                    yerr = args['verr']
                    xlab = options.invaratt
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
        
    def extract_graph_series(self, sampleset, options, att, err):
        plotargs = {'invar':[], 'var':[], 'depth':[], 'ierr':None, 'verr':None}
        if options.invarerr:
            plotargs['ierr'] = []
            def ierr(s):
                plotargs['ierr'].append((s[options.invarerr[0]] or 0, 
                                         s[options.invarerr[1]] or 0))
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
            if s[options.invaratt] is None or s[att] is None:
                continue
            if s[options.invaratt] > 999999 or s[att] > 999999:
                #hack to exclude huge #s coming out of current calcs...
                continue
            plotargs['invar'].append(s[options.invaratt])
            plotargs['var'].append(s[att])
            plotargs['depth'].append(s['depth'])
            ierr(s)
            verr(s)
            
        #change [(-, +), (-, +)...] to ([-, -, ...], [+, +, ...] since that's
        #the matplotlib format
        if options.invarerr:
            plotargs['ierr'] = zip(*plotargs['ierr'])
        if err:
            plotargs['verr'] = zip(*plotargs['verr'])
        return plotargs
        
    def on_pick(self, event):
        cplan = event.artist.get_label()
        xdata, ydata = event.artist.get_data()
        ind = event.ind
        print("On " + str(cplan) + ", picked: ",zip(xdata[ind],ydata[ind]))
        self.picked_indices[cplan].append(ind)

class PlotWindow(wx.Frame):
    
    def __init__(self, parent, samples):
        start_position = parent.GetPosition()
        start_position.x += 50
        start_position.y += 100
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'],
                                         pos=start_position)

        self._mgr = aui.AuiManager(self, 
                    agwFlags=aui.AUI_MGR_DEFAULT & ~aui.AUI_MGR_ALLOW_FLOATING)
        
        self.numericatts = [att.name for att in datastore.sample_attributes if 
                        att.type_ in ('integer', 'float')]
        self.var_choice_atts = [att.name for att in datastore.sample_attributes if 
                        att.type_ in ('integer', 'float')]
        self.var_choice_atts.append("<Multiple>")
        
        self.create_toolbar()
        self.canvas = PlotCanvas(self, samples, self.get_options()) 
        
        self.SetSize(self.canvas.GetMinSize())
        self.SetMinSize(self.canvas.GetMinSize())
        self._mgr.AddPane(self.canvas, 
                          aui.AuiPaneInfo().CenterPane().Name('theplot').
                          DockFixed())
        self._mgr.Update()
        
    def get_max_extent(self, choice):
        max_width = -1
        max_extent = None
        for str in choice.GetStrings():
            extent = wx.Size(*choice.GetTextExtent(str))
            width = extent.width
            if(width > max_width):
                max_width = width
                max_extent = extent
        return max_extent
        
    def create_toolbar(self):
        self.toolbar = aui.AuiToolBar(self, wx.ID_ANY, 
                                      agwStyle=aui.AUI_TB_HORZ_TEXT | 
                                      aui.AUI_TB_PLAIN_BACKGROUND)
        self.radio_id = wx.NewId()
        
        self.toolbar.AddLabel(wx.ID_ANY, "Invariant Axis:",70)
        
        self.xinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "X")
        self.xinvar_radio.SetValue(True)
        self.toolbar.AddControl(self.xinvar_radio)
        self.yinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "Y")
        self.toolbar.AddControl(self.yinvar_radio)
        
        self.toolbar.AddSeparator()

        self.invar_choice_id = wx.NewId()
        self.invar_choice = wx.Choice(self.toolbar, self.invar_choice_id, 
                                      choices=self.numericatts)
        self.invar_choice.SetMaxSize(self.get_max_extent(self.invar_choice))
        self.invar_choice.SetStringSelection('depth')
        self.toolbar.AddControl(self.invar_choice)
        
        self.var_choice_id = wx.NewId()
        self.var_choice = wx.Choice(self.toolbar, self.var_choice_id, 
                                choices=self.var_choice_atts)
        self.var_choice.SetMaxSize(self.get_max_extent(self.var_choice))
        self.var_choice.SetStringSelection('14C Age')
        self.var_selection = [ self.var_choice.GetStringSelection() ] 
        self.last_var_selection = self.var_selection
        self.toolbar.AddControl(self.var_choice)
        
        self.Bind(wx.EVT_RADIOBUTTON,self.OnVariablesChanged, id=self.radio_id)
        self.Bind(wx.EVT_CHOICE, self.OnVariablesChanged, 
                  id=self.invar_choice_id)
        self.Bind(wx.EVT_CHOICE, self.OnVariantChanged, id=self.var_choice_id)
                
        self.toolbar.Realize()
        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('gtoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))
        
    def OnVariantChanged(self, event):
        if event.GetId() is not self.var_choice_id:
            print("Error: unexpected event source.")
            return
        
        if self.var_choice.GetStringSelection() != "<Multiple>":
            self.var_selection = [self.var_choice.GetStringSelection()]
        else:
            dlg = wx.MultiChoiceDialog( self, 
                    "Select multiple attributes to plot on the variant aixs.",
                    "Blah?", self.numericatts)
            if (dlg.ShowModal() == wx.ID_OK):
                self.var_selection = [self.numericatts[i] 
                                      for i in dlg.GetSelections()]
            else:
                self.var_selection = self.last_var_selection
            dlg.Destroy()
            if len(self.var_selection) is 1:
                self.var_choice.SetStringSelection(self.var_selection[0])
        self.last_var_selection = self.var_selection
        self.OnVariablesChanged(event)
        
    def OnVariablesChanged(self, event):
        self.canvas.update_graph(self.get_options())
        
    def get_options(self):
        options = PlotOptions(self.invar_choice.GetStringSelection(),
                          varatts = self.var_selection,
                          invaraxis = 'x' if self.xinvar_radio.GetValue() else 'y'
                          )
        return options

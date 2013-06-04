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
from cscience.GUI import icons
from wx.lib.agw import aui
from wx.lib.agw import foldpanelbar as fpb
from wx.lib.agw import pycollapsiblepane as pcp

class PlotOptions(object):
    
    defaults = {
                       'invaratt' : 'depth',
                       'invarerr' : None,
                       'varatts' : ['14C Age'],
                       'varerrs' : [('14C Age Error', '14C Age Error')],
                       'invaraxis' : 'x',
                       'stacked' : False
                       }

    def __init__(self, **kwargs):
        self.invaratt = kwargs.get('invaratt', self.defaults['invaratt'])
        self.invarerr = kwargs.get('invarerr', self.defaults['invarerr'])
        self.varatts = kwargs.get('varatts', self.defaults['varatts'])
        if 'varatts' in kwargs:
            #TODO: HACK
            self.varerrs = []
            for varatt in self.varatts:
                self.varerrs.append((varatt+" Error", varatt+" Error"))
        else:
            self.varerrs = self.defaults['varerrs']
        self.invaraxis = kwargs.get('invaraxis', self.defaults['invaraxis'])
        self.stacked = kwargs.get('stacked', self.defaults['stacked'])
        
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
    
#TODO: Probably would make sense to move this class elsewhere.
"""We want the pane to be invisible when collapsed, so we have to make some 
minor modifications to PyCollapsiblePane"""
class CalCollapsiblePane(pcp.PyCollapsiblePane):
    
    def __init__(self, parent):
        super(CalCollapsiblePane, self).__init__(parent, label="",
                                                 agwStyle = wx.CP_DEFAULT_STYLE |
                                                 wx.CP_GTK_EXPANDER)
        self.SetExpanderDimensions(0,0)
    
    
    """Overriding PyCollapsiblePane's DoGetBestSize()"""
    def DoGetBestSize(self):
        if self.IsExpanded():
            return super(CalCollapsiblePane, self).DoGetBestSize()
        else:
            return wx.Size(0,0)


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

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._mgr = aui.AuiManager(self, 
                    agwFlags=aui.AUI_MGR_DEFAULT)
        
        self.numericatts = [att.name for att in datastore.sample_attributes if 
                        att.type_ in ('integer', 'float')]
        self.var_choice_atts = [att.name for att in datastore.sample_attributes if 
                        att.type_ in ('integer', 'float')]
        self.var_choice_atts.append("<Multiple>")

        self.plot_pane = wx.Panel(self, id=wx.ID_ANY)
        self.populate_plot_pane(self.plot_pane, samples)
        self._mgr.AddPane(self.plot_pane, 
                          aui.AuiPaneInfo().CenterPane().Name('theplot').
                          Layer(0))
        sizer.Add(self.plot_pane,1,wx.EXPAND)
        
        self.cp = CalCollapsiblePane(self)
        self.make_pane_content()
        sizer.Add(self.cp, 0, wx.EXPAND)
        self._mgr.AddPane(self.cp,
                          aui.AuiPaneInfo().Name('optionspane').Layer(5).
                          CenterPane())
        
        self.SetSizerAndFit(sizer)
        self.Layout()
#         self._mgr.Update()

        
    def make_pane_content(self):
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        bar = fpb.FoldPanelBar(self.cp.GetPane(), wx.ID_ANY,
                           agwStyle=fpb.FPB_VERTICAL)
        
        cs = fpb.CaptionBarStyle()
        cs.SetCaptionStyle(fpb.CAPTIONBAR_SINGLE)
        cs.SetFirstColour(wx.WHITE)
        
        item = bar.AddFoldPanel("Error Display", collapsed=False, cbstyle=cs)
        for choice in ('None', 'Error Bars', 'Violin Plot'):
            radio_button = wx.RadioButton(item, wx.ID_ANY,
                                          choice)
            radio_button.SetValue(choice == 'Error Bars') #default selection
            radio_button.Bind(wx.EVT_RADIOBUTTON, self.OnOptionsChanged)
            bar.AddFoldPanelWindow(item, radio_button,fpb.FPB_ALIGN_LEFT)
            
        sizer.Add(bar,1,wx.EXPAND)
        #TODO: Make the below hack less.. hacky.
        size = item._captionBar.DoGetBestSize()
        size.width = size.width + 30
        sizer.SetMinSize(size)
        self.cp.GetPane().SetSizer(sizer)
        
    def populate_plot_pane(self, pane, samples):
        mgr = aui.AuiManager(pane)
        
        self.plot_canvas = PlotCanvas(self, samples, self.get_options())
        mgr.AddPane(self.plot_canvas, aui.AuiPaneInfo().Name('plotcanvas').
                    CenterPane().Layer(0))
        
        self.create_toolbar(pane)
        mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('gtoolbar').
                      Layer(10).Top().DockFixed().Gripper(False).
                      CaptionVisible(False).CloseButton(False))
        
        pane.SetMinSize(self.plot_canvas.GetMinSize())
        mgr.Update()

    
    def create_toolbar(self, pane):
        
        self.toolbar = aui.AuiToolBar(pane, wx.ID_ANY, 
                                      agwStyle=aui.AUI_TB_HORZ_TEXT | 
                                      aui.AUI_TB_PLAIN_BACKGROUND)
        self.radio_id = wx.NewId()
        
        self.toolbar.AddLabel(wx.ID_ANY, "Invariant Axis:",70)
        
        self.xinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "X")
        self.xinvar_radio.SetValue(PlotOptions.defaults['invaraxis']=='x')
        self.toolbar.AddControl(self.xinvar_radio)
        self.yinvar_radio = wx.RadioButton(self.toolbar, self.radio_id, "Y")
        self.yinvar_radio.SetValue(PlotOptions.defaults['invaraxis']=='x')
        self.toolbar.AddControl(self.yinvar_radio)
        
        self.toolbar.AddSeparator()

        self.invar_choice_id = wx.NewId()
        self.invar_choice = wx.Choice(self.toolbar, self.invar_choice_id, 
                                      choices=self.numericatts)
        self.invar_choice.SetStringSelection(PlotOptions.defaults['invaratt'])
        self.toolbar.AddControl(self.invar_choice)
        
        self.var_choice_id = wx.NewId()
        self.var_choice = wx.Choice(self.toolbar, self.var_choice_id, 
                                choices=self.var_choice_atts)
        self.var_choice.SetStringSelection(PlotOptions.defaults['varatts'][0])
        self.var_selection = [ self.var_choice.GetStringSelection() ] 
        self.last_var_selection = self.var_selection
        self.toolbar.AddControl(self.var_choice)
        
        self.toolbar.AddStretchSpacer()
        
        self.options_button_id = wx.NewId()
        self.toolbar.AddSimpleTool(self.options_button_id, '',
                        wx.ArtProvider.GetBitmap(icons.ART_GRAPHING_OPTIONS,
                                                 wx.ART_TOOLBAR,(16,16)))
        
        self.Bind(wx.EVT_RADIOBUTTON,self.OnOptionsChanged, id=self.radio_id)
        self.Bind(wx.EVT_CHOICE, self.OnOptionsChanged, 
                  id=self.invar_choice_id)
        self.Bind(wx.EVT_CHOICE, self.OnVariantChanged, id=self.var_choice_id)
        self.Bind(wx.EVT_TOOL, self.OnOptionsPressed, id=self.options_button_id)
                
        self.toolbar.Realize()
        
    def OnOptionsPressed(self, event):
        if self.cp.IsExpanded():
            self.cp.Collapse()
        else:
            self.cp.Expand()
        
    def OnOptionsChanged(self, event):
        self.plot_canvas.update_graph(self.get_options())
        
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
        self.OnOptionsChanged(event)
        
    def get_options(self):
        #TODO: Kind of a hack.
        try:
            options = PlotOptions(invaratt=self.invar_choice.GetStringSelection(),
                              varatts=self.var_selection,
                              invaraxis='x' if self.xinvar_radio.GetValue() else 'y'
                              )
        except AttributeError:
            options = PlotOptions()
        return options

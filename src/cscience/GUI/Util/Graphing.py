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

class PlotOptions(object):
    
    ERROR_NONE = 0
    ERROR_BARS = 1
    INTERP_NONE = 3
    INTERP_LINEAR = 4
    INTERP_CUBIC = 5
    
    defaults = {'invaratt' : 'depth',
                'varatts' : ['14C Age'],
                'invaraxis' : 'x',
                'stacked' : False,
                'error_display' :  ERROR_BARS,
                'show_axes_labels' : True,
                'show_legend' : True,
                'show_grid' : False,
                'x_invert' : False,
                'y_invert' : False,
                'interpolation' : INTERP_NONE,
                'selected_cplans' : []}
    options_list = []

    def __init__(self, **kwargs):
        for parm in ('invaratt', 'varatts', 'invaraxis', 'stacked', 
                     'error_display', 'show_axes_labels', 'show_legend',
                     'show_grid', 'interpolation', 'selected_cplans',
                     'x_invert', 'y_invert'):
            setattr(self, parm, kwargs.get(parm, self.defaults.get(parm)))
        
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

# Doesn't need to be a thing, but for the
# sake of claity, here's an interface!
class Option:
    # Abstract
    def update_plot(self, canvas): # takes a plot canvas
        pass

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    
    colorseries = 'brgmyck'
    shapeseries = 's^ov*p+hxD'
    
    def __init__(self, parent, samples, options):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())
        self.samples = samples
        self.picked_indices = {}
        self.SetBackgroundColour(wx.BLUE)
        colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        new_colour = [colour.Red()/255.0, colour.Green()/255.0, colour.Blue()/255.0, colour.Alpha()/255.0]
        #wx.Colour is 0 to 255, but matplotlib color is 0 to 1?
        self.figure.set_facecolor(new_colour)
        self.parent = parent
        self.all_cplans = options.selected_cplans #bit of a hack, but this should always be a list of all possible cplans at the start
        self.draw_graph(options)
        self.figure.canvas.mpl_connect('pick_event',self.on_pick)

    def filter_by_cplan(self, options):
        for plot in self.plots:
            for artist in filter(lambda art: type(art) == matplotlib.lines.Line2D, plot.get_children()):
                selected = False
                for cplan in options.selected_cplans:
                    if cplan in artist.get_label():
                        selected = True
                        break
                artist.set_visible(selected)

    def update_graph(self, options):
        force_full_redraw = False
        #TODO: make it so fewer options force a full redraw?
        for option in PlotOptions.defaults: #Just want to iterate through the names
            if getattr(options, option) != getattr(self.last_options, option):
                if option == 'show_axes_labels':
                    for axes in self.plots:
                        axes.set_xlabel(axes.get_xlabel(), visible = options.show_axes_labels)
                        axes.set_ylabel(axes.get_ylabel(), visible = options.show_axes_labels)
                elif option == 'show_legend':
                    for axes in self.plots:
                        axes.get_legend().set_visible(options.show_legend)
                elif option == 'show_grid':
                    for axes in self.plots:
                        axes.grid()
                elif option == 'selected_cplans':
                    self.filter_by_cplan(options)
                elif option == 'x_invert':
                    for axes in self.plots:
                        axes.invert_xaxis()
                elif option == 'y_invert':
                    for axes in self.plots:
                        axes.invert_yaxis()
                else:
                    force_full_redraw = True
                    break
                
        #TODO: figure out how to change axis locations w/o re-creating axes
        #if (options.x_invert != self.last_options.x_invert) or (options.y_invert != self.last_options.y_invert):
        #    for axes in self.plots:
        #        if operator.xor(bool(options.x_invert), bool(options.y_invert)):
        #            axes.legend(options.selected_cplans, loc='upper right')
        #        else:
        #            axes.legend(options.selected_cplans, loc='upper left')
            
        if force_full_redraw:
            self.figure.clear()
            self.draw_graph(options)
        
        self.draw()
        self.last_options = options
        
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
            iter_plots = [(vatt, plot) for vatt, plot in zip(options.varatts, self.plots)]
        else:
            '''If you want picking to just work for multiple graphs, have iter_plots just be 
            (options.varatts[i], iter_plots[0][1]) for all the varatts (drop the
            twinx/twiny), then uncomment the 'if plot is not last_plot' block in
            the for loop below so coloring works right.
            If on the other hand you want axes to work well when doing multiple 
            graphs on top of eachother, use the twiny/twinx version and change the
            'if plot is not last_plot' check to check if plot is twinned off of 
            something, somehow. I don't know how you might get picking to work 
            in this case.''' 
            iter_plots = [(options.varatts[0], self.figure.add_subplot(1,1,1))]
            #Now iterate over the rest of the varatts.
            for i in range(len(options.varatts)-1):
#                 if options.invaraxis == 'y':
#                     iter_plots.append([options.varatts[i+1], iter_plots[0][1].twiny()])
#                 elif options.invaraxis == 'x':
#                     iter_plots.append([options.varatts[i+1], iter_plots[0][1].twinx()])
                iter_plots.append([options.varatts[i+1], iter_plots[0][1]])
            self.plots = self.figure.get_axes()

#         print(iter_plots)
        #TODO: how to keep error bar & interpolation line out of the legend?
        last_plot = None
        for vatt, plot in iter_plots:
#             print("vatt: %s, plot: %s"%(vatt, plot))
            self.samples.sort(key=lambda s: (s['computation plan'], s[options.invaratt]))
            if plot is not last_plot:
                plans = []
                colors = itertools.cycle(self.colorseries)
                shapes = itertools.cycle(self.shapeseries)
            for cplan, sampleset in itertools.groupby(self.samples, key=lambda s: s['computation plan']):
                plans.append(cplan)
                color = colors.next()
                shape = shapes.next()
                args = self.extract_graph_series(sampleset, options, vatt)
                if options.invaraxis == 'y':
                    x = args['var']
                    xerr = args['varerr']
                    y = args['invar']
                    yerr = args['invarerr']
                    xlab = '%s (%s)'%(vatt, args['var_units'])
                    ylab = '%s (%s)'%(options.invaratt, args['invar_units'])
                else:
                    x = args['invar']
                    xerr = args['invarerr']
                    y = args['var']
                    yerr = args['varerr']
                    xlab = '%s (%s)'%(options.invaratt, args['invar_units'])
                    ylab = '%s (%s)'%(vatt, args['var_units'])
                lab = '%s_%s'%(cplan, vatt)
                self.picked_indices[cplan] = []
                if options.interpolation is PlotOptions.INTERP_LINEAR:
                    plot.plot(x, y, ''.join((color,shape)), label=lab, 
                          picker=5, linestyle='-')
                elif options.interpolation is PlotOptions.INTERP_CUBIC:
                    plot.plot(x, y, ''.join((color,shape)), label=lab, 
                          picker=5)
                    if len(x) > 2:
                        #can't do a cubic interpolation on <3 points!
                        plans.append('(Interpolation)')
                        interp_func = interp1d([float(i) for i in x], [float(i) for i in y], 
                                               bounds_error=False, fill_value=0, kind='cubic')
                        new_x = arange(min(x), max(x), abs(max(x)-min(x))/100.0)
                        plot.plot(new_x, interp_func(new_x), ''.join((color,'-')), label='%s_%s'%(lab,'cubic_interp'))
                else:
                    plot.plot(x, y, ''.join((color,shape)), label=lab, 
                          picker=5)
                if options.error_display is PlotOptions.ERROR_BARS:
                    plans.append('(Error Bar)')
                    plot.errorbar(x, y, xerr=zip(*xerr), yerr=zip(*yerr), 
                                  label='%s_%s'%(lab,'error_bar'),
                                  fmt=color)
                plot.set_xlabel(xlab, visible=options.show_axes_labels)
                plot.set_ylabel(ylab, visible=options.show_axes_labels)
            if options.show_grid:
                plot.grid()
                
            plot.legend(plans, loc='upper left')
            plot.get_legend().set_visible(options.show_legend)
            self.filter_by_cplan(options)
            last_plot = plot
        self.last_options =  options
        #TODO: get this thing working.
        #plt.tight_layout()
        
    def extract_graph_series(self, sampleset, options, att):
        #note -- assumes that unit for any att is the same throughout the core
        #further notes -- this iteration could be saved in some cases by looking
        #at the previous args & not-rerunning for plot options that remain
        #similar enough. However, no serious speed issues have yet been seen.
        plotargs = {'invar':[], 'invarerr':[], 'var':[], 'varerr':[], 
                    'depth':[], 'var_units':'', 'invar_units':''}
        for s in sampleset:
            if s[options.invaratt] is None or s[att] is None:
                continue
            plotargs['depth'].append(s['depth'])
            
            inv = s[options.invaratt]
            plotargs['invar'].append(getattr(inv, 'magnitude', inv))
            try:
                plotargs['invarerr'].append(inv.uncertainty.get_mag_tuple())
            except AttributeError:
                plotargs['invarerr'].append((0, 0))
            plotargs['invar_units'] = plotargs['invar_units'] or inv.dimensionality.string
            
            var = s[att]
            plotargs['var'].append(getattr(var, 'magnitude', var))
            try:
                plotargs['varerr'].append(var.uncertainty.get_mag_tuple())
            except AttributeError:
                plotargs['varerr'].append((0, 0))
            plotargs['var_units'] = plotargs['var_units'] or var.dimensionality.string
            
        return plotargs
        
    def on_pick(self, event):
        
        data = event.artist.get_data()
        label = event.artist.get_label()
        cplan, vatt = label.split('_')
        event_data = {'axes' : event.artist.get_axes(),
                      'cplan' : cplan,
                      'var_att' : vatt,
                      'xycoords' : (data[0][event.ind], data[1][event.ind]),
                      'artist' : event.artist, 
                      'idx' : event.ind}
#         print('cplan: %s, var_att: %s'%(event_data['cplan'], event_data['var_att']))
        if not wx.GetKeyState(wx.WXK_SHIFT):
            self.picked_indices = {}
            for artist in event_data['axes'].get_children():
                if artist.get_gid() is 'highlight':
                    artist.remove()
                if artist.get_gid() is 'annotate':
                    artist.remove()
                    
        if event_data['cplan'] in self.picked_indices.keys():
            self.picked_indices[event_data['cplan']].append(event_data)
        else:
            self.picked_indices[event_data['cplan']] = [event_data]
        
        '''Uncomment the below to enable drawing a circle around the selected point.'''
#         event_data['axes'].plot(xVal, yVal, marker='o', linestyle='',
#                                 markeredgecolor=[1,0.5,0,0.5],
#                                 markerfacecolor='none',
#                                 markeredgewidth=2,
#                                 markersize=10,
#                                 label='_nolegend_',
#                                 gid='highlight')
        
        xVal, yVal = event_data['xycoords']
        if(self.last_options.invaraxis == 'y'):
            xLab = event_data['var_att']
            yLab = event_data['axes'].get_ylabel().rsplit(' ', 1)[0]
        else:
            xLab = event_data['axes'].get_xlabel().rsplit(' ', 1)[0]
            yLab = event_data['var_att']
    
        xUnit = pq.Quantity(1, datastore.sample_attributes[xLab].unit).dimensionality
        yUnit = pq.Quantity(1, datastore.sample_attributes[yLab].unit).dimensionality
        
        def clean_text(val):
            return ('%f'%val).rstrip('0').rstrip('.')
        
        str = '%s: %s %s\n%s: %s %s' % (xLab, clean_text(xVal), xUnit, yLab, clean_text(yVal), yUnit)
        event_data['axes'].annotate(str, (xVal, yVal), xytext=(5, -25),
                                    xycoords='data', textcoords='offset points', 
                                    gid='annotate')
        #TODO: Detect if our annotation would be outside the viewable area and 
        #put it elsewhere if so.
        
        self.draw()
        
        


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
    ERROR_VIOLIN = 2
    INTERP_NONE = 3
    INTERP_LINEAR = 4
    INTERP_CUBIC = 5
    
    defaults = {
                       'invaratt' : 'depth',
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
                       'selected_cplans' : []
                       }
    options_list = []

    def __init__(self, **kwargs):
        self.invaratt = kwargs.get('invaratt', self.defaults['invaratt'])
        self.varatts = kwargs.get('varatts', self.defaults['varatts'])
        self.invaraxis = kwargs.get('invaraxis', self.defaults['invaraxis'])
        self.stacked = kwargs.get('stacked', self.defaults['stacked'])
        self.error_display = kwargs.get('error_display', self.defaults['error_display'])
        self.show_axes_labels = kwargs.get('show_axes_labels', self.defaults['show_axes_labels'])
        self.show_legend = kwargs.get('show_legend', self.defaults['show_legend'])
        self.show_grid = kwargs.get('show_grid', self.defaults['show_grid'])
        self.interpolation = kwargs.get('interpolation', self.defaults['interpolation'])
        self.selected_cplans = kwargs.get('selected_cplans', self.defaults['selected_cplans'])
        self.x_invert = kwargs.get('x_invert', self.defaults['x_invert'])
        self.y_invert = kwargs.get('y_invert', self.defaults['y_invert'])
        
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
        for axes in self.plots:
            axes.legend(options.selected_cplans, loc='upper left')

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
                
        if (options.x_invert != self.last_options.x_invert) or (options.y_invert != self.last_options.y_invert):
            for axes in self.plots:
                if operator.xor(bool(options.x_invert), bool(options.y_invert)):
                    axes.legend(options.selected_cplans, loc='upper right')
                else:
                    axes.legend(options.selected_cplans, loc='upper left')
            
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
        
        for vatt, plot in zip(options.varatts, self.plots):
            self.samples.sort(key=lambda s: (s['computation plan'], s[options.invaratt]))
            colors = itertools.cycle(self.colorseries)
            shapes = itertools.cycle(self.shapeseries)
            for cplan, sampleset in itertools.groupby(self.samples, key=lambda s: s['computation plan']):
                args = self.extract_graph_series(sampleset, options, vatt)
                
                if options.invaraxis == 'y':
                    x = args['var']
                    y = args['invar']
                    xlab = '%s (%s)'%(vatt, args['var_units'])
                    ylab = '%s (%s)'%(options.invaratt, args['invar_units'])
                else:
                    x = args['invar']
                    y = args['var']
                    xlab = '%s (%s)'%(options.invaratt, args['invar_units'])
                    ylab = '%s (%s)'%(vatt, args['var_units'])
                    
                self.picked_indices[cplan] = []
                color = colors.next()
                shape = shapes.next()
                if options.interpolation is PlotOptions.INTERP_LINEAR:
                    plot.plot(x, y, ''.join((color,shape)), label=cplan, 
                          picker=5, linestyle='-')
                elif options.interpolation is PlotOptions.INTERP_CUBIC:
                    plot.plot(x, y, ''.join((color,shape)), label=cplan, 
                          picker=5)
                    interp_func = interp1d(x, y, bounds_error=False, fill_value=0, kind='cubic')
                    new_x = arange(min(x), max(x), abs(max(x)-min(x))/100.0)
                    plot.plot(new_x, interp_func(new_x), ''.join((color,'-')), label='%s_%s'%(cplan,'cubic_interp'))
                else:
                    plot.plot(x, y, ''.join((color,shape)), label=cplan, 
                          picker=5)
                if options.error_display is PlotOptions.ERROR_BARS:
                    #More direct way to accomplish what the map + lambda is doing?
                    x_error = y_error = None
                    try: x_error = zip(*map(lambda ex: ex.uncertainty.get_mag_tuple(),x))
                    except AttributeError: 
                        print(xlab,": x (",type(x[0]),") doesn't have get_error")
                    try: 
                        tmp = map(lambda why: why.uncertainty.get_mag_tuple(), y)
                        y_error = zip(*tmp)
                    except AttributeError: 
                        print(ylab,": y (",type(y[0]),") doesn't have get_error")
                    plot.errorbar(x, y, xerr=x_error, yerr=y_error, label='%s_%s'%(cplan,'error_bar'),
                                  fmt=None)
                elif options.error_display is PlotOptions.ERROR_VIOLIN:
                    print("Violin plotting not yet implemented.")     
                plot.set_xlabel(xlab, visible=options.show_axes_labels)
                plot.set_ylabel(ylab, visible=options.show_axes_labels)
                #TODO: annotate points w/ their depth, if depth is not the invariant
            if options.show_grid:
                plot.grid()
            plot.legend(options.selected_cplans, loc='upper left')
            plot.get_legend().set_visible(options.show_legend)
            self.filter_by_cplan(options)
        self.last_options =  options
        #TODO: get this thing working.
        #plt.tight_layout()
        
    def extract_graph_series(self, sampleset, options, att):
        plotargs = {'invar':[], 'var':[], 'depth':[]}
        for s in sampleset:
            if s[options.invaratt] is None or s[att] is None:
                continue
            if s[options.invaratt] > 999999 or s[att] > 999999:
                #hack to exclude huge #s coming out of current calcs...
                continue
            plotargs['invar'].append(s[options.invaratt])
            plotargs['var'].append(s[att])
            plotargs['depth'].append(s['depth'])
            if not plotargs.has_key('var_units'):
                plotargs['var_units'] = s[att].dimensionality.string
            if not plotargs.has_key('invar_units'):
                plotargs['invar_units'] = s[options.invaratt].dimensionality.string
            
        return plotargs
        
    def on_pick(self, event):
        
        data = event.artist.get_data()
        event_data = {'axes' : event.artist.get_axes(),
                      'cplan' : event.artist.get_label(),
                      'xycoords' : (data[0][event.ind], data[1][event.ind]),
                      'artist' : event.artist, 
                      'idx' : event.ind} 

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
        xLab = event_data['axes'].get_xlabel()
        yLab = event_data['axes'].get_ylabel()
        
        def clean_text(val):
            return ('%f'%val).rstrip('0').rstrip('.')
        
        str = '%s: %s\n%s: %s' % (xLab, clean_text(xVal), yLab, clean_text(yVal))
        event_data['axes'].annotate(str, (xVal, yVal), xytext=(5, -25),
                                    xycoords='data', textcoords='offset points', 
                                    gid='annotate')
        #TODO: Detect if our annotation would be outside the viewable area and 
        #put it elsewhere if so.
        
        self.draw()
        
        


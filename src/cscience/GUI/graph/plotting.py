import wx

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

import options, events

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self.plot = self.figure.add_subplot(1,1,1)
        self.pointsets = [] 
        self._canvas_options = options.PlotCanvasOptions()

        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        # used to index into when there is a pick event
        self.picking_table = {} 
        self.last_pick_line = None
    
    @property
    def canvas_options(self):
        return self._canvas_options
    @canvas_options.setter
    def canvas_options(self, newval):
        self._canvas_options = newval
        self.update_graph()
        
    def clear(self):
        self.pointsets = []
        self.plot.clear()
        
    def clear_pick(self):
        if self.last_pick_line:
            try:
                self.last_pick_line.remove()
            except ValueError:
                pass
        
    def add_points(self, points, opts=options.PlotOptions(fmt='-', is_graphed=True)):
        self.pointsets.append((points, opts))
    
    def on_pick(self, evt):
        try:
            data = evt.artist.get_data()
            self.clear_pick()
            xVal, yVal = data[0][evt.ind[0]], data[1][evt.ind[0]]

            lines = evt.artist.axes.plot(xVal, yVal, marker='o', linestyle='',
                                    markeredgecolor=[1,0.5,0,0.5],
                                    markerfacecolor='none',
                                    markeredgewidth=2,
                                    markersize=10,
                                    label='_nolegend_',
                                    gid='highlight')
                
            label = evt.artist.get_label()
            index = evt.ind

            self.last_pick_line = lines[0]
            try:
                point = self.picking_table[label][index[0]]
                wx.PostEvent(self, events.GraphPickEvent(self.GetId(), point=point))
            except KeyError:
                pass
        except AttributeError:
            pass

    def update_graph(self):
        self.plot.clear()
        self.picking_table = {}

        iattrs = set()
        dattrs = set()

        # for now, plot everything on the same axis

        error_bars = self.canvas_options.show_error_bars

        for points, opts in self.pointsets:
            if not opts.is_graphed:
                continue
            self.picking_table[points.variable_name] = points
            opts.plot_with(points, self.plot, error_bars)

            iattrs.add(points.independent_var_name)
            dattrs.add(points.variable_name)

        if self.canvas_options.show_axes_labels:
            self.plot.set_xlabel(",".join(iattrs))
            self.plot.set_ylabel(",".join(dattrs))

        self.canvas_options.plot_with(self.plot)
        self.draw()

    def export_to_file(self, filename):
        self.figure.savefig(filename)

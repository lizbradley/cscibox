import wx

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

import options
import events

import traceback
import sys


def mplhandler(fn):
    def handler_maker(self, mplevent):
        def handler(event):
            return fn(self, mplevent, event)
        return handler
    return handler_maker


class PlotCanvas(wx.Panel):
# wxagg.FigureCanvasWxAgg
    def __init__(self, parent, sz = None):
        self._canvas_options = options.PlotCanvasOptions()
        matplotlib.rc('font', **self.canvas_options.fontdict)
        
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, style=wx.RAISED_BORDER)
        if not sz:
            self.delegate = wxagg.FigureCanvasWxAgg(self, wx.ID_ANY, plt.Figure(facecolor=(0.9,0.9,0.9)))
        else:
            self.delegate = wxagg.FigureCanvasWxAgg(self, wx.ID_ANY, plt.Figure(facecolor=(0.9, 0.9, 0.9), figsize=sz))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.delegate, 1, wx.EXPAND)

        self.plot = self.delegate.figure.add_axes([0.1,0.1,0.8,0.8])
        self.pointsets = []

        self.delegate.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.delegate.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        # self.figure.canvas.mpl_connect('motion_notify_event',self.on_motion)
        self.annotations = {}
        # used to index into when there is a pick event
        self.picking_table = {}
        self.dist_point = None

        self.SetSizerAndFit(sizer)

    def on_motion(self, evt):
        evt = events.GraphMotionEvent(self.GetId(), x=evt.xdata, y=evt.ydata)
        wx.PostEvent(self, evt)

    def draw(self):
        self.delegate.draw()


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

    def add_points(self, points, 
                   opts=options.PlotOptions(fmt='-', is_graphed=True)):
        self.pointsets.append((points, opts))

    def on_pick(self, event):
        if event.artist.get_label() is None or event.artist.get_label() == '':
            return

        if self.delegate.figure.canvas.HasCapture():
            if event.mouseevent.button == 1:
                # left click
                self.remove_current_annotation(event)
                self.highlight_point(event, [0.93, 0.35, 0.10, 1],
                                     msize=10, mkr='o')
                # wx.CallAfter(self.highlight_point, event, [1, 0.5, 0, 1])
            elif event.mouseevent.button == 3:
                # right click
                self.create_popup_menu(['ignore', 'important', 'clear'],
                                       [self.on_ignore, self.on_important,
                                       self.on_clear], event)
            self.delegate.figure.canvas.ReleaseMouse()
        self.draw()

    def update_graph(self):
        self.plot.clear()
        self.picking_table = {}

        iattrs = set()
        dattrs = set()
        
        matplotlib.rc('font', **self.canvas_options.fontdict)

        # for now, plot everything on the same axis

        error_bars = self.canvas_options.show_error_bars

        for points, opts in self.pointsets:
            if not opts.is_graphed:
                continue
            points = self.canvas_options.modify_pointset(self,points)
            self.picking_table[points.label] = points
            opts.plot_with(self, points, self.plot, error_bars)

            iattrs.add(points.independent_var_name)
            dattrs.add(points.variable_name)

        if self.canvas_options.show_axes_labels:
            self.plot.set_xlabel(", ".join([i or "" for i in iattrs]), 
                                 fontdict=self.canvas_options.fontdict)
            self.plot.set_ylabel(", ".join([d or "" for d in dattrs]), 
                                 fontdict=self.canvas_options.fontdict)

        self.canvas_options.plot_with(self, self.plot)
        self.draw()

    def export_to_file(self, filename):
        self.delegate.figure.savefig(filename)

    def create_popup_menu(self, values, funs, event):
        cmenu = wx.Menu()

        if not hasattr(self, "CMenuID"):
            # don't make these more than once
            self.cmenuID = []
            for i, val in enumerate(values):
                self.cmenuID.append(wx.NewId())
                self.Bind(wx.EVT_MENU, funs[i](event), id=self.cmenuID[i])

        for i, val in enumerate(values):
            item = wx.MenuItem(cmenu, id=self.cmenuID[i], text=val)
            cmenu.AppendItem(item)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        wx.CallAfter(self.PopupMenu, cmenu)

    def gid_name_gen(self, event):
        '''
        generate unique name for pick events in order to be able to find and
        remove them later
        '''
        label = event.artist.get_label()
        btn = event.mouseevent.button
        idx = event.ind[0]

        return 'btn' + str(btn) + label + str(idx)

    def highlight_point(self, event, edgeColor, msize=10, mkr='.'):
        data = event.artist.get_data()

        label = event.artist.get_label()
        btn = event.mouseevent.button
        idx = event.ind[0]
        xVal, yVal = data[0][idx], data[1][idx]

        if mkr == 'o':
            faceColor = 'none'
        else:
            faceColor = edgeColor

        pointset = None
        try:
            if btn == 1:
                for (i, _) in self.pointsets:
                    i.set_selected_point(None)

                pointset = self.picking_table[label]
                point = pointset[idx]
                pointset.set_selected_point(point)
                self.update_graph()

                self.dist_point = point
            else:
                point = self.dist_point

            wx.PostEvent(self, events.GraphPickEvent(self.GetId(),
                         distpoint=point, pointset=pointset))
        except KeyError as e:
            print ("Caught " + str(e))
            pass

    def highlight_remove(self, event):
        label = event.artist.get_label()
        idx = event.ind[0]

        btn = event.mouseevent.button

        if btn == 3:
            for line in event.artist.axes.lines:
                if line.get_gid() == self.gid_name_gen(event):
                    line.remove()
                    wx.PostEvent(self, events.GraphPickEvent(self.GetId(),
                                 distpoint=self.dist_point))
                    return
        elif btn == 1:
            for line in event.artist.axes.lines:
                try:
                    cond = line.get_gid().startswith('btn1')
                except AttributeError:
                    cond = False
                if cond:
                    line.remove()
                    point = self.picking_table[label][idx]
                    self.dist_point = point
                    wx.PostEvent(self, events.GraphPickEvent(self.GetId(),
                                 distpoint=point))
                    return

    def remove_current_annotation(self, mplevent):
        pointset = self.picking_table[mplevent.artist.get_label()]
        smpl = pointset.plotpoints[mplevent.ind[0]].sample

        pointset.unignore_point(mplevent.ind[0])
        self.update_graph()
        for key in self.annotations:
            for item in self.annotations[key]:
                if item is smpl:
                    self.annotations[key].remove(item)

        self.highlight_remove(mplevent)

    @mplhandler
    def on_ignore(self, mplevent, menuevent):
        pointset = self.picking_table[mplevent.artist.get_label()]

        if 'ignore' not in self.annotations:
            self.annotations['ignore'] = []

        # can't add a point twice
        self.remove_current_annotation(mplevent)

        pointset.ignore_point(mplevent.ind[0])
        self.update_graph()
        self.annotations['ignore'].append(pointset.plotpoints
                                          [mplevent.ind[0]].sample)

    @mplhandler
    def on_important(self, mplevent, menuevent):
        pointset = self.picking_table[mplevent.artist.get_label()]

        if 'important' not in self.annotations:
            self.annotations['important'] = []

        # can't add a point twice
        self.remove_current_annotation(mplevent)

        self.annotations['important'].append(pointset.plotpoints
                                             [mplevent.ind[0]].sample)

        self.highlight_point(mplevent, [0.21, 0.61, 0.03, 1])

    @mplhandler
    def on_clear(self, mplevent, menuevent):
        self.remove_current_annotation(mplevent)

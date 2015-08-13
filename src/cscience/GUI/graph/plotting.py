import wx

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

import options
import events


def mplhandler(fn):
    def handler_maker(self, mplevent):
        def handler(event):
            return fn(self, mplevent, event)
        return handler
    return handler_maker


class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self.plot = self.figure.add_subplot(1, 1, 1)
        self.pointsets = []
        self._canvas_options = options.PlotCanvasOptions()

        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        # self.figure.canvas.mpl_connect('motion_notify_event',self.on_motion)
        self.annotations = {}
        # used to index into when there is a pick event
        self.picking_table = {}
        self.dist_point = None

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

    def add_points(self, points, opts=options.PlotOptions(fmt='-',
                                                          is_graphed=True)):
        self.pointsets.append((points, opts))

    def on_motion(self, evt):
        # print 'motion'
        # print evt
        # if evt.button == 1:
        #     print 'left click'
        # elif evt.button == 2:
        #     print 'middle click'
        # elif evt.button == 3:
        #     print 'right click'
        pass

    def on_pick(self, event):
        if self.figure.canvas.HasCapture():
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
            self.figure.canvas.ReleaseMouse()

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

        if self.canvas_options.large_font:
            font = {'size' : 15}
        else:
            font = {'size' : 12}
        matplotlib.rc('font', **font)

        if self.canvas_options.show_axes_labels:
            self.plot.set_xlabel(",".join(iattrs))
            self.plot.set_ylabel(",".join(dattrs))

        self.canvas_options.plot_with(self.plot)
        self.draw()

    def export_to_file(self, filename):
        self.figure.savefig(filename)

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

        event.artist.axes.plot(xVal, yVal, marker=mkr, linestyle='',
                               markeredgecolor=edgeColor,
                               markerfacecolor=faceColor,
                               markeredgewidth=2,
                               markersize=msize,
                               label='_nolegend_',
                               gid=self.gid_name_gen(event))

        try:
            if btn == 1:
                point = self.picking_table[label][idx]
                self.dist_point = point
            else:
                point = self.dist_point

            wx.PostEvent(self, events.GraphPickEvent(self.GetId(),
                         distpoint=point))
        except KeyError:
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

        self.annotations['ignore'].append(pointset.plotpoints
                                          [mplevent.ind[0]].sample)

        self.highlight_point(mplevent, [0.06, 0.09, 0.61, 1])

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

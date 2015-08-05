import wx

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

import options, events

def mplhandler(fn):
    def handler_maker(self, mplevent):
        def handler(event):
            return fn(self, mplevent, event)
        return handler
    return handler_maker

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self.plot = self.figure.add_subplot(1,1,1)
        self.pointsets = []
        self._canvas_options = options.PlotCanvasOptions()
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        # self.figure.canvas.mpl_connect('motion_notify_event',self.on_motion)

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
                self.clear_pick()
                print event.ind
                self.highlight_point(event,[1,0.5,0,0.5])
            elif event.mouseevent.button == 3:
                # right click
                self.create_popup_menu(['ignore','important'], \
                                    [self.on_ignore, self.on_important], event)
            self.figure.canvas.ReleaseMouse()


    def update_graph(self):
        self.plot.clear()
        self.picking_table = {}

        iattrs = set()
        dattrs = set()

        # for now, plot everything on the same axis
        for points, opts in self.pointsets:
            if not opts.is_graphed:
                continue
            self.picking_table[points.variable_name] = points
            opts.plot_with(points, self.plot)

            iattrs.add(points.independent_var_name)
            dattrs.add(points.variable_name)

        if self.canvas_options.show_axes_labels:
            self.plot.set_xlabel(",".join(iattrs))
            self.plot.set_ylabel(",".join(dattrs))

        self.canvas_options.plot_with(self.plot)
        self.draw()

    def export_to_file(self, filename):
        self.figure.savefig(filename)

    def create_popup_menu(self, values, funs, event):
        cmenu = wx.Menu()

        if not hasattr(self,"CMenuID"):
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

    def highlight_point(self, event, edgeColor):
        data = event.artist.get_data()
        xVal, yVal = data[0][event.ind[0]], data[1][event.ind[0]]

        lines = event.artist.axes.plot(xVal, yVal, marker='o', linestyle='',
                                markeredgecolor=edgeColor,
                                markerfacecolor='none',
                                markeredgewidth=2,
                                markersize=10,
                                label='_nolegend_',
                                gid='highlight')

        label = event.artist.get_label()
        index = event.ind

        self.last_pick_line = lines[0]
        try:
            point = self.picking_table[label][index[0]]
            wx.PostEvent(self, events.GraphPickEvent(self.GetId(), point=point))
        except KeyError:
            pass


    @mplhandler
    def on_ignore(self, mplevent, menuevent):
        print 'Ignore'
        print mplevent.ind[0]
        # if not hasattr(self,"user_ignore"):
        #     self.user_ignore = []
        # self.user_ignore.append(event.ind[0])
        # print self.user_ignore
        # self.highlight_point(event,[1,0.5,0.5,0.5])

    @mplhandler
    def on_important(self, mplevent, menuevent):
        print 'Important'
        print mplevent.ind[0]
        # if not hasattr(self,"user_important"):
        #     self.user_important = []
        # self.user_important.append(event.ind[0])
        # print self.user_important
        # self.highlight_point(event,[0,0,0,0])

    @mplhandler
    def on_three(self, mplevent, menuevent):
        print 'Popup three'
        if not hasattr(self,"user_something"):
            self.user_something = []
        self.user_something.append(event.ind[0])
        self.highlight_point(event,[0.75,0.2,0.25,0.5])

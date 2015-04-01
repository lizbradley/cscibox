import wx
from cscience.GUI.Util.graph.PlotCanvasOptions import PlotCanvasOptions

import matplotlib
matplotlib.use( 'WXAgg' )
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure())

        self._m_plot = self.figure.add_subplot(1,1,1)
        self._m_pointset = {} # :: Int => (Plotter, [PlotPoint])
        self._m_canvas_options = PlotCanvasOptions()
        self._m_pick_listener = None
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self._m_pointset_table = {} # used to index into when there is a pick event

    def get_options(self):
        return self._m_canvas_options

    def set_options(self, new_canvas_options):
        print "Set options", str(new_canvas_options)
        old_canvas_options = self._m_canvas_options
        self._m_canvas_options = new_canvas_options

        self._m_canvas_options.set_invert_x_axis(
            old_canvas_options.get_invert_x_axis() ^ new_canvas_options.get_invert_x_axis()
            )

        self._m_canvas_options.set_invert_y_axis(
            old_canvas_options.get_invert_y_axis() ^ new_canvas_options.get_invert_y_axis()
            )
        print "Update graph"
        self._update_graph()
    
    # identitiy :: int - the pointset identity
    # points    :: PointSet - the list of points and their error bars
    # plotter   :: Plotter - the plotter used to plot
    def add_pointset(self, identity, points, plotter):
        # add a pointset to the dictionary of pointsets.
        # This will allow the 
        self._m_pointset[identity] = (points, plotter)

    def clear_pointset(self):
        self._m_pointset = {}

    def on_pick(self, evt):
        label = evt.artist.get_label()
        index = evt.ind
        try:
            point = self._m_pointset_table[label][index[0]]
            self._m_pick_listener(point)
        except KeyError:
            print ("[WARN] - invalid key " + label)

    def set_pick_listener(self, l):
        self._m_pick_listener = l
        
    def delete_pointset(self, identity):
        # Python! Why no haz remove!!!
        del self._m_pointset[identity]

    def update_graph(self):
        print ("Updating graph")
        self._update_graph()

    def clear(self):
        self._m_plot.clear()
        self._m_pointset.clear()
        self.draw()

    def reapply_options(self):
        print "_m_canvas_options = ", str(self._m_canvas_options)
        self._m_canvas_options.plot_with(self._m_pointset, self._m_plot)

    def _update_graph(self):
        self._m_plot.clear()
        self._m_pointset_table = {}
        print "Reapply options"

        # for now, plot everything on the same axis
        for (points, plotter) in self._m_pointset.values():
            self._m_pointset_table[points.get_variable_name()] = points
            plotter.plot_with(points, self._m_plot)

        self.reapply_options()

        self.draw()

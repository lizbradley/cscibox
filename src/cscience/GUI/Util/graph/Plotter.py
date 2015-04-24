#Embedded file name: /home/jrahm/Projects/Calvin-jrahm/src/cscience/GUI/Util/graph/Plotter.py
from cscience.GUI.Util.graph import PlotOptions

class Plotter:

    def __init__(self, opts = PlotOptions()):
        self.opts = opts

    def plot_with(self, points, plot):
        opts = self.opts
        opts.plot_with(points, plot)

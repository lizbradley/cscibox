from cscience.GUI.Util.graph.options import PlotOptions

class PointSet:

    def __init__(self, plotpoints, vname):
        self.m_plotpoints = plotpoints[:]
        self.m_plotpoints.sort(key=lambda p: p.x)
        self.m_variable_name = vname

    def __getitem__(self, i):
        return self.m_plotpoints[i]

    def get_variable_name(self):
        return self.m_variable_name

    def unzip_points(self):
        return unzip_plot_points(self.m_plotpoints)


def unzip_plot_points(points):
    return ([i.x for i in points],
     [i.y for i in points],
     [i.xorig for i in points],
     [i.yorig for i in points])
    

class PlotPoint:
    # Potenitally change to have a more robutst
    # statistical distribution than just error bars
    # perhaps maybe?
    def __init__(self, x, y, xorig, yorig, computation_plan):
        self.x = x
        self.y = y
        
        self.xorig = xorig
        self.yorig = yorig

        self.computation_plan = computation_plan

    def __str__(self):
        return "(%s,%s,%s,%s)" % (self.x, self.y, self.xorig, self.yorig)
    def __repr__(self):
        return self.__str__()

    def get_computation_plan(self):
        return self.computation_plan
    
class Plotter:

    def __init__(self, opts=PlotOptions()):
        self.opts = opts

    def plot_with(self, points, plot):
        opts = self.opts
        opts.plot_with(points, plot)

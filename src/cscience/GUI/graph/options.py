import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import splprep
from scipy.interpolate import splev
from matplotlib.legend import DraggableLegend
import matplotlib.patches as mpatches

from scipy.stats import linregress

from cscience.GUI.graph.events import R2ValueUpdateEvent
import wx

class LinearInterpolationStrategy(object):
    @staticmethod
    def interpolate(_, x, y):
        return (x, y)

class RegressionLineStrategy(object):
    def interpolate(self, evt_handler, x, y):
        slope, y_intcpt, r_value, p_value, std_err = linregress(x, y)

        evt = R2ValueUpdateEvent(evt_handler.GetId())
        evt.slope = slope
        evt.y_intcpt = y_intcpt
        evt.r_value = r_value
        evt.p_value = p_value
        evt.std_err = std_err

        wx.PostEvent(evt_handler, evt)

        return ([i for i in x], [y_intcpt + slope * i for i in x])

class SciInterpolationStrategy(object):
    def __init__(self, kind):
        self.kind = kind

    def interpolate(self, _, x, y):
        interp_func = interp1d([float(i) for i in x], [float(i) for i in y],
                               bounds_error=False, fill_value=0, kind=self.kind)
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        return (new_x, interp_func(new_x))

class SplineInterpolationStrategy(object):
    def interpolate(self, _, x, y):
        tck,u=splprep([x,y],s=200000)
        x_i,y_i= splev(np.linspace(0,1,100),tck)
        return (x_i,y_i)

class PlotCanvasOptions(object):
    def __init__(self, **kwargs):
        self.legend = kwargs.get('legend', False)
        self.invert_x_axis = kwargs.get('invert_x_axis', False)
        self.invert_y_axis = kwargs.get('invert_y_axis', False)
        self.show_axes_labels = kwargs.get('show_axes_labels', True)
        self.show_grid = kwargs.get('show_grid', False)
        self.show_error_bars = kwargs.get('show_error_bars', False)
        self.flip_axis = kwargs.get('flip_axis', False)
        self.label_font = kwargs.get('label_font',
                    wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL, face='Times New Roman'))
        self._legend = None

    @property
    def fontdict(self):
        fontdict = {'family':self.label_font.FaceName,
                    'size':self.label_font.PointSize,
                    'style':self.label_font.StyleString[12:].lower(),
                    'weight':self.label_font.WeightString[13:].lower()}
        return fontdict
    @fontdict.setter
    def fontdict(self, fd):
        self.label_font = wx.Font(fd.get('size', 15), wx.FONTFAMILY_DEFAULT,
                getattr(wx, 'FONTSTYLE_%s' % fd.get('style', 'normal').upper()),
                getattr(wx, 'FONTWEIGHT_%s' % fd.get('weight', 'normal').upper()),
                face=fd.get('family', 'Times New Roman'))

    def modify_pointset(self, wx_event_handler, pointset) :
        if self.flip_axis:
            return pointset.flip()
        return pointset

    #Hacked on Bacon
    def bacon_legend(self, handles,labels):
        for i in range(len(labels)):
            if labels[i].startswith("Bacon Distribution"):
                break
        else:
            return handles
        try:
            handles[i] = mpatches.Patch(color=handles[i].get_color())
            return handles
        except UnboundLocalError:
            #labels was a list 0 long and so i was never defined
            pass


    def plot_with(self, wx_event_handler, plot):
        if self.invert_y_axis ^ plot.yaxis_inverted():
            plot.invert_yaxis()

        if self.invert_x_axis ^ plot.xaxis_inverted():
            plot.invert_xaxis()

        if self.show_grid:
            plot.grid()

        if self.legend:
            handles, labels = plot.get_legend_handles_labels()
            handles = self.bacon_legend(handles,labels)
            self._legend = plot.legend(handles, labels)
            if self._legend:
                #might not be a legend if there are no points selected
                self._legend.draggable()
        elif self._legend:
            self._legend.remove()
            self._legend = None

class PlotOptionSet(dict):
    """
    A set of associations from (dependent variable, computation plan) -> options for graphing
    """

    fmt_lst = ['s', 'o', '^', 'd', '*']
    color_lst = [(180, 100, 100), (100, 180, 100), (100, 100, 180),
                 (180, 180, 100), (100, 180, 180)]

    @classmethod
    def from_vars(cls, varset, runs):
        default = runs[0]

        instance = cls()
        for ind, var in enumerate(varset):
            instance[var] = PlotOptions(run=default,
                                        runs=runs,
                                        dependent_variable=var,
                                        fmt=cls.fmt_lst[ind % len(cls.fmt_lst)],
                                        color=cls.color_lst[ind % len(cls.color_lst)])

        if 'Best Age' in instance:
            instance['Best Age'].is_graphed = True

        return instance

class PlotOptions(object):
    """
    Options for a single x/y plot. Not the case for the
    more global options about plotting.
    """
    interpolations = {"Piecewise-Linear": LinearInterpolationStrategy(),
                      u"R\xb2 Regression Line": RegressionLineStrategy(),
                      "Cubic": SciInterpolationStrategy('cubic'),
                      "Quadratic": SciInterpolationStrategy('quadratic'),
                      "B-Spline": SplineInterpolationStrategy(),
                      "No Line": None}

    def __init__(self, **kwargs):
        self.dependent_variable = kwargs.get('dependent_variable')
        self.is_graphed = kwargs.get('is_graphed', False)
        self.color = kwargs.get('color', (0,0,0))
        self.fmt = kwargs.get('fmt', 'o')
        self.run = kwargs.get('run', 'input')
        self.runs = kwargs.get('runs', ['input'])
        self.point_size = kwargs.get('point_size', 6)
        self.line_width = kwargs.get('line_width', 4)
        self.line_color = kwargs.get('line_color', (0,0,0))
        self.alpha = kwargs.get('alpha', 1)
        self.selected_point = None

    def plot_with(self, wx_event_handler, points, plot, error_bars):
        """
        plot points on plot under the context represented by this object
        """

        if not self.is_graphed:
            return
        (xs, ys, xorig, yorig) = points.unzip_points()
        (interp_xs, interp_ys, _, _) = points.unzip_without_ignored_points()
        (xigored, yignored, _ , _) = points.unzip_ignored_points()

        if self.color.__class__ == str:
            l_color_str = self.color
        else:
            # ghetto hack to make 3.0.0 work with 3.0.2
            l_color_tup = (self.color[0], self.color[1], self.color[2])
            l_color_str = "#%02x%02x%02x"%l_color_tup

        if self.line_color.__class__ == str:
            l_line_color_str = self.line_color
        else:
            # ghetto hack to make 3.0.0 work with 3.0.2
            l_line_color_tup = (self.line_color[0], self.line_color[1], self.line_color[2])
            l_line_color_str = "#%02x%02x%02x"%l_line_color_tup

        if error_bars:
            y_err = []
            for val in yorig:
                try:
                    y_err.append(float(val.uncertainty))
                except (IndexError, AttributeError):
                    y_err=[]

        if self.dependent_variable == 'Model Age':
            spline = points.spline
            xs=np.linspace(min(xs),max(xs),10000)
            ys = spline(xs)
            self.fmt = '-'
            l_color_str = l_line_color_str

        if self.fmt:
            plot.plot(xs, ys, self.fmt, color=l_color_str, label=points.label,
                      picker=self.point_size, markersize=self.point_size, linewidth=self.line_width, alpha=self.alpha)
            plot.plot(xigored, yignored, self.fmt, color="#eeeeee", markersize=self.point_size, alpha=self.alpha)
            if points.selected_point:
                plot.plot(points.selected_point.x, points.selected_point.y, self.fmt,
                          color=l_color_str, mec="#ff6666", mew=2, markersize=self.point_size, alpha=self.alpha)
        if error_bars:
            if len(y_err)>0:
                plot.errorbar(xs,ys, yerr = y_err, ecolor="black", fmt="none",
                              elinewidth=1.5, capthick=1.5, capsize=3, alpha=self.alpha)

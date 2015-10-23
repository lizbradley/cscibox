import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import splprep
from scipy.interpolate import splev
from matplotlib.legend import DraggableLegend

from scipy.stats import linregress

from cscience.GUI.graph.events import R2ValueUpdateEvent
from wx import PostEvent


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

        PostEvent(evt_handler, evt)

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
        self.large_font = kwargs.get('large_font', False)
        self.flip_axis = kwargs.get('flip_axis')


        self._legend = None

    def plot_with(self, wx_event_handler, plot):
        if self.invert_y_axis ^ plot.yaxis_inverted():
            plot.invert_yaxis()

        if self.invert_x_axis ^ plot.xaxis_inverted():
            plot.invert_xaxis()

        plot.grid(self.show_grid)

        if self.legend:
            self._legend = plot.legend()
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
    def from_vars(cls, varset, cplans):
        default = cplans[0]

        instance = cls()
        for ind, var in enumerate(varset):
            instance[var] = PlotOptions(computation_plan=default,
                                        computation_plans=cplans,
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
        self.interpolation_strategy = kwargs.get('interpolation_strategy', 'No Line')
        self.computation_plan = kwargs.get('computation_plan')
        self.computation_plans = kwargs.get('computation_plans')

    def plot_with(self, wx_event_handler, points, plot, error_bars):
        """
        plot points on plot under the context represented by this object
        """

        if not self.is_graphed:
            return
        (xs, ys, xorig, yorig) = points.unzip_points()
        (interp_xs, interp_ys, _, _) = points.unzip_without_ignored_points()
        l_color_tup = (self.color[0], self.color[1], self.color[2]) # ghetto hack to make 3.0.0 work with 3.0.2
        l_color_str = "#%02x%02x%02x"%l_color_tup

        if error_bars:
            y_err = []
            for val in yorig:
                try:
                    y_err.append(float(val.uncertainty))
                except IndexError:
                    y_err=[]

        interp = self.interpolations.get(self.interpolation_strategy, None)
        if interp:
            (xs_p, ys_p) = interp.interpolate(wx_event_handler, interp_xs, interp_ys)
            if not self.fmt:
                # this is the main plot then.
                plot.plot(xs_p, ys_p, '-', color=l_color_str, label=points.variable_name)
            else:
                plot.plot(xs_p, ys_p, '-', color=l_color_str)

        if self.fmt:
            plot.plot(xs, ys, self.fmt, color=l_color_str, label=points.variable_name, picker=5)
            if error_bars:
                if len(y_err)>0:
                    plot.errorbar(xs,ys, yerr = y_err, ecolor=l_color_str, fmt="none")

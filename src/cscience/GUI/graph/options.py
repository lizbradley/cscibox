import numpy as np
from scipy.interpolate import interp1d


class LinearInterpolationStrategy(object):
    @staticmethod
    def interpolate(x, y):
        return (x, y)

class SciInterpolationStrategy(object):
    def __init__(self, kind):
        self.kind = kind

    def interpolate(self, x, y):
        interp_func = interp1d([float(i) for i in x], [float(i) for i in y], 
                               bounds_error=False, fill_value=0, kind=self.kind)
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        return (new_x, interp_func(new_x))

class PlotCanvasOptions(object):
    def __init__(self, **kwargs):
        self.legend = kwargs.get('legend', False)
        self.invert_x_axis = kwargs.get('invert_x_axis', False)
        self.invert_y_axis = kwargs.get('invert_y_axis', False)
        self.show_axes_labels = kwargs.get('show_axes_labels', False)
        self.show_grid = kwargs.get('show_grid', False)
        
        self._legend = None

    def plot_with(self, plot):
        if self.invert_y_axis ^ plot.yaxis_inverted():
            plot.invert_yaxis()
        if self.invert_x_axis ^ plot.xaxis_inverted():
            plot.invert_xaxis()

        plot.grid(self.show_grid)

        if self.legend:
            self._legend = plot.legend()
        elif self._legend:
            self._legend.remove()
            self._legend = None
            
class PlotOptionSet(dict):
    """
    A set of associations from dependent variable -> options for graphing
    """
    
    fmt_lst = ['s', 'o', '^', 'd', '*']
    color_lst = [(180, 100, 100), (100, 180, 100), (100, 100, 180), 
                 (180, 180, 100), (100, 180, 180)]
            
    @classmethod
    def from_vars(cls, varset, cplans):
        default = dict([(plan, True) for plan in cplans])
        
        instance = cls()
        for ind, var in enumerate(varset):
            instance[var] = PlotOptions(computation_plans=default,
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
    interpolations = {"Linear": LinearInterpolationStrategy(), 
                      "Cubic": SciInterpolationStrategy('cubic'),
                      "Quadratic": SciInterpolationStrategy('quadratic'), 
                      "No Line": None}
    
    def __init__(self, **kwargs):
        self.is_graphed = kwargs.get('is_graphed', False)
        self.color = kwargs.get('color', (0,0,0))
        self.fmt = kwargs.get('fmt', 'o')
        self.interpolation_strategy = kwargs.get('interpolation_strategy', 'Linear')
        self.computation_plans = kwargs.get('computation_plans', {})

    def plot_with(self, points, plot):
        """
        plot points on plot under the context represented by this object
        """
        if not self.is_graphed:
            return
        (xs, ys, _, _) = points.unzip_points()
        l_color_tup = (self.color[0], self.color[1], self.color[2]) # ghetto hack to make 3.0.0 work with 3.0.2
        l_color_str = "#%02x%02x%02x"%l_color_tup

        if self.interpolation_strategy:
            (xs_p, ys_p) = self.interpolations[self.interpolation_strategy].interpolate(xs, ys)
            if not self.fmt:
                # this is the main plot then.
                plot.plot(xs_p, ys_p, '-', color=l_color_str, label=points.variable_name)
            else:
                plot.plot(xs_p, ys_p, '-', color=l_color_str)

        if self.fmt:
            plot.plot(xs, ys, self.fmt, color=l_color_str, label=points.variable_name, picker=5)
            


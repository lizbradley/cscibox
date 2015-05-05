# Options per each plotting canvas
class PlotCanvasOptions:
    def __init__(self):
        self.legend = False;
        self.invert_x_axis = False

        self._m_legend = None
        self._m_invert_x_axis = False
        self._m_invert_y_axis = False
        self._m_show_axes_labels = False
        self._m_show_grid = False

    def copy(self):
        ret = PlotCanvasOptions()
        ret.set_invert_y_axis(self.get_invert_y_axis())
        ret.set_invert_x_axis(self.get_invert_x_axis())
        ret.set_show_axis_labels(self.get_show_axis_lables())
        ret.set_show_legend(self.get_show_legend())
        ret.set_show_grid(self.get_show_grid())
        return ret
    
    def get_invert_x_axis(self):
        return self._m_invert_x_axis
        
    def get_invert_y_axis(self):
        return self._m_invert_y_axis

    def get_show_axis_lables(self):
        return self._m_show_axes_labels

    def get_show_legend(self):
        return self.legend

    def get_show_grid(self):
        return self._m_show_grid

    def set_show_axis_labels(self, yes):
        self._m_show_axes_labels = yes

    def set_show_grid(self, yes):
        self._m_show_grid = yes

    def set_show_legend(self, yes):
        self.legend = yes

    def set_invert_x_axis(self, yes):
        self._m_invert_x_axis = yes

    def set_invert_y_axis(self, yes):
        self._m_invert_y_axis = yes

    def plot_with(self, _, plot):
        if self._m_invert_y_axis:
            print "Enabling invert y axis"
            plot.invert_yaxis()
        if self._m_invert_x_axis:
            print ("Enabling invert x axis" + str(plot.__class__))
            plot.invert_xaxis()

        if self.legend:
            print "Enabling legend "
            self._m_legend = plot.legend()
        elif self._m_legend:
            print "Disable invert x axis"
            self._m_legend.remove()
            self._m_legend = None

    def enable_legend(self,yes):
        print ("Enable legend %s" % yes)
        self.legend = yes

    def __str__(self):
        return "legend: %s; invert_x: %s;" \
               "invert y: %s; show_labels: %s; " \
               "show_grid: %s;" % \
               (self._m_legend, self._m_invert_x_axis,
                self._m_invert_y_axis, self._m_show_axes_labels, self._m_show_grid)



# Options for a single xvy plot. Not the case for the
# more global options about plotting.
class PlotOptions:
    def __init__(self):
        self.color = (0,0,0)
        self.fmt = "o"
        self.interpolation_strategy = None

    # plot points on plot under the context
    # represented by this object
    #
    # points :: [PlotPoint]
    # plot :: Matplotlib plot thing
    def plot_with(self, points, plot):
        (xs, ys, _, _) = points.unzip_points()

        if self.interpolation_strategy:
            (xs, ys) = self.interpolation_strategy.interpolate(xs, ys)

        print "Plotting with variable name", points.get_variable_name()
        plot.plot(xs, ys, self.fmt, color="#%02x%02x%02x"%self.color, label=points.get_variable_name(), picker=5)


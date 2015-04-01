
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


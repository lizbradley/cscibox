import warnings

from cscience import datastore
from cscience.framework.datastructures import GraphableData
datastore = datastore.Datastore()

class PointSet(GraphableData):
    """
    A glorified list of points.
    """

    def __init__(self, plotpoints, vname=None, ivarname=None, run=None, spline=None, label=None):
        self.plotpoints = sorted(plotpoints, key=lambda p: p.x)
        self.variable_name = vname
        self.independent_var_name = ivarname
        self.ignored_points = set()
        self.selected_point = None
        self.flipped = False
        self.run = run
        self.label = "%s (%s)" % (vname, label)
        self.spline = spline

    def x_selection(self):
        return self.selected_point.x

    def y_selection(self):
        return self.selected_point.y

    def flip(self):
        def flip(point):
            ret = PlotPoint(point.y,
                            point.x,
                            point.yorig,
                            point.xorig,
                            point.sample)
            return ret
        ret = PointSet([flip(i) for i in self.plotpoints])
        ret.variable_name = self.independent_var_name
        ret.independent_var_name = self.variable_name
        ret.ignored_points = self.ignored_points
        ret.run = self.run
        ret.label = self.label
        return ret

    def __getitem__(self, i):
        return self.plotpoints[i]

    def ignore_point(self, point_idx):
        self.ignored_points.add(point_idx)

    def unignore_point(self, point_idx):
        self.ignored_points.discard(point_idx)

    def unzip_without_ignored_points(self):
        ret = ([], [], [], [])
        for idx, point in enumerate(self.plotpoints):
            if idx not in self.ignored_points:
                ret[0].append(point.x)
                ret[1].append(point.y)
                ret[2].append(point.xorig)
                ret[3].append(point.yorig)
        return ret

    def unzip_ignored_points(self):
        ret = ([], [], [], [])
        for idx in self.ignored_points:
            ret[0].append(self.plotpoints[idx].x)
            ret[1].append(self.plotpoints[idx].y)
            ret[2].append(self.plotpoints[idx].xorig)
            ret[3].append(self.plotpoints[idx].yorig)
        return ret

    def unzip_points(self):
        """
        Returns a 4-tuple of lists of x, y, xorig, yorig
        """
        numpts = len(self.plotpoints)
        ret = ([None] * numpts, [None] * numpts, [None] * numpts, [None] * numpts)
        for ind, pt in enumerate(self.plotpoints):
            ret[0][ind] = pt.x
            ret[1][ind] = pt.y
            ret[2][ind] = pt.xorig
            ret[3][ind] = pt.yorig
        return ret

    def graph_self(self, plot, options, error_bars=True):
        (xs, ys, xorig, yorig) = self.unzip_points()
        (interp_xs, interp_ys, _, _) = self.unzip_without_ignored_points()
        (xigored, yignored, _ , _) = self.unzip_ignored_points()

        if error_bars:
            y_err = []
            for val in yorig:
                try:
                    y_err.append(float(val.uncertainty))
                except (IndexError, AttributeError):
                    y_err=[]

        if options.fmt:
            plot.plot(xs, ys, options.fmt, color=options.color, label=self.label,
                      picker=options.point_size, markersize=options.point_size)
            plot.plot(xigored, yignored, options.fmt, color="#eeeeee", markersize=options.
                       point_size)
            if self.selected_point:
                plot.plot(self.selected_point.x, self.selected_point.y, options.fmt,
                          color=options.color, mec="#ff6666", mew=2,
                          markersize= options.point_size)
        if error_bars:
            if len(y_err)>0:
                plot.errorbar(xs,ys, yerr = y_err, ecolor="black", fmt="none",
                              elinewidth=1.5, capthick=1.5, capsize=3)

class PlotPoint(object):
    def __init__(self, x, y, xorig, yorig, sample):
        self.x = x
        self.y = y

        self.xorig = xorig
        self.yorig = yorig

        self.sample = sample

    @property
    def run(self):
        return self.sample['run']

class SampleCollection(object):
    """
    Convenience functions for sample <-> graphs
    """

    def __init__(self, virtual_core_list, sample_view):
        self.virtual_cores = virtual_core_list
        self.view = sample_view
        self.annotations = {}
        self.cache = {}
        self.bacon = None

    def get_pointset(self, iattr, dattr, run):
        '''Creates a list of points to be graphed.
        iattr = independant attribute
        dattr = dependant attribute
        '''
        key = (iattr, dattr, run)
        if key in self.cache:
            return self.cache[key]

        points = []
        spline = None

        for vcore in self.virtual_cores:
            if vcore.run != run:
                continue
            for sample in vcore:
                indep_var = sample[iattr]
                dep_var = sample[dattr]

                # shipping values out of quantity objects
                inv_v = getattr(indep_var, 'magnitude', indep_var)
                dev_v = getattr(dep_var, 'magnitude', dep_var)

                if inv_v is not None and dev_v is not None:
                    points.append(PlotPoint(inv_v, dev_v, indep_var, dep_var, sample))

        ps = PointSet(points, dattr, iattr, run, spline, datastore.runs[run].display_name)
        self.cache[key] = ps
        return ps

    def get_property_object(self, prop, run):
        for vcore in self.virtual_cores:
            if vcore.properties[prop] and vcore.run == run:
                return vcore.properties[prop]
        raise Exception("Property " + prop + " not found in Run " + run)



    def get_graphable_stuff(self):
        '''Collect the set of graphable attributes and properties for plotting.

        Checks is_numeric() and is_graphable()
        returns (attributes, properties)
        '''
        # if this is slow, replace with izip to test each core
        def att_exists(att):
            for c in self.virtual_cores:
                for sample in c:
                    if sample[att] is not None:
                        return True
            return False

        attset = [att for att in self.view if
                  att in datastore.sample_attributes and
                  datastore.sample_attributes[att].is_numeric() and
                  att_exists(att)]

        property_set = set()

        for vcore in self.virtual_cores:
            for prop in vcore.properties:
                if prop in datastore.core_attributes and \
                             datastore.core_attributes[prop].is_graphable():
                    property_set.add(prop)

        return (attset, list(property_set))

    def get_runs(self):
        return [(virtual_core.run, datastore.runs[virtual_core.run].display_name)
                 for virtual_core in self.virtual_cores]

import warnings

from cscience import datastore
datastore = datastore.Datastore()

class BaconSets(object):
    """
    A glorified list of lists of points.
    """

    def __init__(self, data, vname=None, ivarname=None, computation_plan=None):
        depth = data.pop(0)
        pointsets = []
        for ages in data:
            points = []
            for i in range(len(ages)):
                inv = depth[i]
                dev = ages[i]

                if inv and dev:
                    points.append(PlotPoint(inv, dev,
                                                  inv, dev, None))
            pointsets.append(points)
        self.pointsets = [PointSet(p,vname,ivarname,computation_plan) for p in pointsets]
        for p in self.pointsets:
            p.label = None
        self.variable_name = vname
        self.independent_var_name = ivarname
        self.ignored_points = NotImplemented
        self.selected_point = NotImplemented
        self.flipped = False
        self.computation_plan = computation_plan
        self.label = "%s (%s)" % (vname, computation_plan)

    def set_selected_point(self, point):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def x_selection(self):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def y_selection(self):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def flip(self):
        ret = BaconSets([p.flip() for p in self.pointsets],
            vname=self.variable_name, ivarname=self.independent_var_name, computation_plan=self.computation_plan)
        return ret

    def __iter__(self):
        for i in self.pointsets:
            yield i

    def __getitem__(self, i):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def ignore_point(self, point_idx):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def unignore_point(self, point_idx):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def unzip_without_ignored_points(self):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def unzip_ignored_points(self):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)

    def unzip_points(self):
        warnings.warn("Not Implemented - Bacon", stacklevel=2)


class PointSet(object):
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

    def set_selected_point(self, point):
        self.selected_point = point

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

    def __init__(self, virtual_sample_lst, sample_view):
        self.sample_list = virtual_sample_lst
        self.view = sample_view
        self.annotations = {}
        self.cache = {}
        self.bacon = None

    #Hacked on Bacon
    def add_bacon(self, bacon):
        self.bacon = bacon

    def get_pointset(self, iattr, dattr, run):
        key = (iattr, dattr, run)
        if key in self.cache:
            return self.cache[key]

        points = []
        spline = None
        for i in self.sample_list:
            if i['run'] == run:
                inv = i[iattr]
                dev = i[dattr]

                inv_v = getattr(inv, 'magnitude', inv)
                dev_v = getattr(dev, 'magnitude', dev)

                if inv_v and dev_v:
                    points.append(PlotPoint(inv_v, dev_v,
                                                  inv, dev, i))

                label = i.dst.runs[run].display_name

            if dattr == 'Model Age':
                spline = i.core_wide[run]['age/depth model']

        ps = PointSet(points, dattr, iattr, run, spline, label)
        self.cache[key] = ps
        return ps

    def get_numeric_attributes(self):
        attset = [att for att in self.view if
                  att in datastore.sample_attributes and
                  datastore.sample_attributes[att].is_numeric() and
                  any([sam[att] is not None for sam in self.sample_list])]
        # Hacked on Bacon
        if self.bacon:
            attset.append("Bacon Distribution")

        return attset

    def get_runs(self):
        #This is gross. Is there really not a better way to do this?
        plans = set([(sam['run'], datastore.runs[sam['run']].display_name) for sam in self.sample_list])
        return list(plans)

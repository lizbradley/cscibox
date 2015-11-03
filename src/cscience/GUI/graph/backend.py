from cscience import datastore
datastore = datastore.Datastore()

class PointSet(object):
    """
    A glorified list of points.
    """

    def __init__(self, plotpoints, vname=None, ivarname=None, computation_plan=None):
        self.plotpoints = sorted(plotpoints, key=lambda p: p.x)
        self.variable_name = vname
        self.independent_var_name = ivarname
        self.ignored_points = set()
        self.selected_point = None
        self.flipped = False
        self.computation_plan = computation_plan
        self.label = "%s (%s)" % (vname, computation_plan)

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
        ret.computation_plan = self.computation_plan
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
    def computation_plan(self):
        return self.sample['computation plan']

class SampleCollection(object):
    """
    Convenience functions for sample <-> graphs
    """

    def __init__(self, virtual_sample_lst, sample_view):
        self.sample_list = virtual_sample_lst
        self.view = sample_view
        self.annotations = {'testing':123}
        self.cache = {}

    def get_pointset(self, iattr, dattr, computation_plan):
        key = (iattr, dattr, computation_plan)
        if key in self.cache:
            return self.cache[key]

        points = []
        for i in self.sample_list:
            if i['computation plan'] == computation_plan:
                inv = i[iattr]
                dev = i[dattr]


                inv_v = getattr(inv, 'magnitude', inv)
                dev_v = getattr(dev, 'magnitude', dev)

                if inv_v and dev_v:
                    points.append(PlotPoint(inv_v, dev_v,
                                                  inv, dev, i))

        ps = PointSet(points, dattr, iattr, computation_plan)
        self.cache[key] = ps
        return ps

    def get_numeric_attributes(self):
        attset = [att for att in self.view if
                  att in datastore.sample_attributes and
                  datastore.sample_attributes[att].is_numeric() and
                  any([sam[att] is not None for sam in self.sample_list])]
        return attset

    def get_computation_plans(self):
        plans = set([sam['computation plan'] for sam in self.sample_list])
        return list(plans)

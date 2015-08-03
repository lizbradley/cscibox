from cscience import datastore
datastore = datastore.Datastore()

class PointSet(object):
    """
    A glorified list of points.
    """

    def __init__(self, plotpoints, vname=None, ivarname=None):
        self.plotpoints = sorted(plotpoints, key=lambda p: p.x)
        self.variable_name = vname
        self.independent_var_name = ivarname

    def __getitem__(self, i):
        return self.plotpoints[i]

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
    def __init__(self, x, y, xorig, yorig, computation_plan):
        self.x = x
        self.y = y

        self.xorig = xorig
        self.yorig = yorig

        self.computation_plan = computation_plan

class SampleCollection(object):
    """
    Convenience functions for sample <-> graphs
    """

    def __init__(self, virtual_sample_lst, sample_view):
        self.sample_list = virtual_sample_lst
        self.view = sample_view
        self.annotations = {'testing':123}

    def get_pointset(self, iattr, dattr, computation_plan):
        points = []
        for i in self.sample_list:
            if i['computation plan'] == computation_plan:

                inv = i[iattr]
                dev = i[dattr]

                inv_v = getattr(inv, 'magnitude', inv)
                dev_v = getattr(dev, 'magnitude', dev)

                if inv_v and dev_v:
                    points.append(PlotPoint(inv_v, dev_v,
                                                  inv, dev, computation_plan))

        return PointSet( points, dattr, iattr )

    def get_numeric_attributes(self):
        attset = [att for att in self.view if
                  att in datastore.sample_attributes and
                  datastore.sample_attributes[att].is_numeric() and
                  any([sam[att] is not None for sam in self.sample_list])]
        return attset

    def get_computation_plans(self):
        plans = set([sam['computation plan'] for sam in self.sample_list])
        return list(plans)

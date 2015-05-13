from cscience.framework.samples import VirtualSample
from cscience import datastore
from cscience.GUI.Util import graph

datastore = datastore.Datastore()

# a list of virtual samples with some convinience functions # for filtering based on attributes
class SampleCollection:

    def __init__( self, virtual_sample_lst ):
        self._m_sample_list = virtual_sample_lst

        self._m_numeric_attributtes = \
            set([ i.name for i in datastore.sample_attributes
                   if i.is_numeric() ])

    # return the PointSet ([PlotPoint]) for the independent and
    # dependent attributtes specified.
    def get_pointset(self, iattr, dattr, computation_plan):
        points = []
        for i in self._m_sample_list:
            if i['computation plan'] == computation_plan:
    
                inv = i[iattr]
                dev = i[dattr]
    
                print "INV(", inv.__class__, "): ", inv
                print "DEV(", dev.__class__, "): ", dev
    
                inv_v = getattr(inv, 'magnitude', inv)
                dev_v = getattr(dev, 'magnitude', dev)
    
                inv_v = getattr(inv_v, 'magnitude', None) or inv_v
                dev_v = getattr(dev_v, 'magnitude', None) or dev_v
    
                if inv_v and dev_v:
                    points.append(graph.PlotPoint(inv_v, dev_v, inv, dev, computation_plan))

        return graph.PointSet( points, dattr )

    def get_numeric_attributes(self):
        tmp_attrs = self.get_attributes()
        return [i for i in tmp_attrs if i in self._m_numeric_attributtes]

    # return a list of attributes in the virtual samples
    def get_attributes(self):
        ret = set()

        for i in self._m_sample_list:
            computation_plan = i['computation plan']

            for j in i.sample['input'].keys():
                ret.add(j)
            for j in i.sample[computation_plan].keys():
                ret.add(j)

        return ret
        

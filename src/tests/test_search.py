'''
Testing the search functionality for cscibox.

todo:
    everything
'''
import unittest

import cscience.datastore
import hobbes.calculations

dstore = cscience.datastore.Datastore()


class CalcTestCases(unittest.TestCase):
    ''' Test everything.  More to come.'''

    def setUp(self):
        dstore.load_from_config()
        core = dstore.cores['Harding Lake']
        #force load
        for _ in core:
            pass
        self.core = core.virtualize()[0]

    def test_graphlist(self):
        depths, ages = hobbes.calculations.graphlist(self.core, 'depth', '14C Age')
        lastd = -9999
        for d, age in zip(depths, ages):
            #cm are annoying here...
            self.assertEqual(self.core[d * 10]['14C Age'], age)
            self.assertGreater(d, lastd)
            lastd = d

    def test_slope(self):
        depths, ages = hobbes.calculations.graphlist(self.core, 'depth', '14C Age')
        slopes = hobbes.calculations.slope(self.core, 'depth', '14C Age')
        for index in xrange(len(slopes)):
            self.assertEqual(
                slopes[index],
                (ages[index+1] - ages[index])/(depths[index+1] - depths[index]))

    def test_c14_cal(self):
        flow = dstore.workflows['Simple CALIB Style Calibration']
        comp_plan = dstore.computation_plans['Simple CALIB + IntCal 2013']
        virt_core = dstore.cores['Harding Lake'].new_computation(comp_plan)
        flow.execute(comp_plan, virt_core, None)
        for sample in virt_core:
            self.assertIsNotNone(sample['Calibrated 14C Age'])

    def test_bacon(self):
        from cscience.framework.datastructures import BaconInfo
        flow = dstore.workflows['BACON Style']
        comp_plan = dstore.computation_plans[u'BACON-style Interpolation + IntCal 2013']
        virt_core = dstore.cores['Harding Lake'].new_computation(comp_plan)
        flow.execute(comp_plan, virt_core, None)
        for sample in virt_core:
            self.assertIsNotNone(sample['Calibrated 14C Age'])
            self.assertIsNotNone(sample['Model Age'])
        self.assertIsInstance(virt_core.properties['Bacon Model'], BaconInfo)

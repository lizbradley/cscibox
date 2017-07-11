'''
Testing the search functionality for cscibox.

todo:
    everything
'''
import unittest
import quantities as pq

import cscience.datastore
from cscience.framework.datastructures import BaconInfo
from hobbes import engine, environment, conclusions, rules, calculations

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
        depths, ages = calculations.graphlist(self.core, 'depth', '14C Age')
        lastd = -9999
        for d, age in zip(depths, ages):
            #cm are annoying here...
            self.assertEqual(self.core[d * 10]['14C Age'], age)
            self.assertGreater(d, lastd)
            lastd = d

    def test_slope(self):
        depths, ages = calculations.graphlist(self.core, 'depth', '14C Age')
        slopes = calculations.slope(self.core, 'depth', '14C Age')
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

    #@unittest.skip("bacon without GUI not working yet")
    def test_bacon(self):
        flow = dstore.workflows['BACON Style']
        comp_plan = dstore.computation_plans[u'BACON-style Interpolation + IntCal 2013']
        virt_core = dstore.cores['Harding Lake'].new_computation(comp_plan)
        flow.execute(comp_plan, virt_core, None,
            ai_params = {'Bacon Memory: Mean': 0.7,
                         'Bacon Memory: Strength': 4.0,
                         'Bacon Number of Iterations': 200,
                         'Bacon Section Thickness': 50.0 * pq.cm,
                         'Bacon t_a': 4})
        for sample in virt_core:
            self.assertIsNotNone(sample['Calibrated 14C Age'])
            self.assertIsNotNone(sample['Age from Model'])
        self.assertIsInstance(virt_core.properties['Bacon Model'], BaconInfo)

    def test_hobbes_need_marine_curve(self):
        env = environment.Environment(self.core)
        result = engine.build_argument(conclusions.Conclusion("need marine curve"), env)
        self.assertIsNotNone(result)
        self.assertFalse(result.confidence.is_true())

class HobbesTestCases(unittest.TestCase):
    def setUp(self):
        dstore.load_from_config()
        flow = dstore.workflows['BACON Style']
        comp_plan = dstore.computation_plans[u'BACON-style Interpolation + IntCal 2013']
        self.virt_core = dstore.cores['Harding Lake'].new_computation(comp_plan)
        flow.execute(comp_plan, self.virt_core, None,
            ai_params = {'Bacon Memory: Mean': 0.7,
                         'Bacon Memory: Strength': 4.0,
                         'Bacon Number of Iterations': 200,
                         'Bacon Section Thickness': 50.0 * pq.cm,
                         'Bacon t_a': 4})

    def test_hobbes_bacon_params(self):
        env = environment.Environment(self.virt_core)
        result = engine.build_argument(conclusions.Conclusion('bacon runs fast'), env)
        self.assertIsNotNone(result)
        self.assertFalse(result.confidence.is_true())

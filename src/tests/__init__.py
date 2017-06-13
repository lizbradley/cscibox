import unittest
import itertools

from cscience import datastore
from hobbes.reasoning import calculations, simulations

datastore = datastore.Datastore()


class CalcTestCases(unittest.TestCase):
    def setUp(self):
        datastore.load_from_config()
        core = datastore.cores['Harding Lake']
        #force load
        for sample in core:
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
            self.assertEqual(slopes[index], 
                (ages[index+1] - ages[index])/(depths[index+1] - depths[index]))
            
        print len([x for x in slopes if x < 0])
    
    def test_mse(self):
        #this is a bit nonsense, but fine for the instant.
        print calculations.mean_squared_error(self.core, 'depth', '14C Age')
        
class ComputationPlans(unittest.TestCase):
    def setUp(self):
        datastore.load_from_config()
        core = datastore.cores['Harding Lake']
        #force load
        for sample in core:
            pass
        self.core = core.virtualize()[0]
        
    def bacon(self):
        import cscience.components.cfiles.baconc
        import cscience.components.baconplugin
        interp = baconplugin.BaconInterpolation()
        data = interp.build_data_array(self.core)
        baconc.run_simulation(len(data),
                              [baconc.PreCalDet(*sample) for sample in data],
                              hiatusi, sections, memorya, memoryb,
                              -1000, 1000000, guesses[0], guesses[1],
                              mindepth, maxdepth, self.tempfile.name, num_iterations)

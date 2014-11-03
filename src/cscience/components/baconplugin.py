#import rpy2
#import rpy2.rinterface
#import rpy2.robjects

import cscience
import cscience.components
from cscience.components import UncertainQuantity

import numpy
import baconc

class BaconInterpolation(cscience.components.BaseComponent):
    visible_name = 'Interpolate Using BACON (Coming Soon!)'
    inputs = {'required':('Calibrated 14C Age',)}
    
    #def prepare(self, *args, **kwargs):
    #    super(BaconInterpolation, self).prepare(*args, **kwargs)
        
        #import bacon from plugin location instead?
        
    def run_component(self, core):
        #TODO: handle ages without distributions.
        det = [baconc.PreCalDet(str(sam['id']), float(sam['Calibrated 14C Age'].magnitude),
                                sam['Calibrated 14C Age'].uncertainty.as_single_mag(), 
                                float(sam['depth'].magnitude), 3, 4, 
                                getattr(sam['Calibrated 14C Age'].uncertainty.distribution, 'x', []),
                                getattr(sam['Calibrated 14C Age'].uncertainty.distribution, 'y', []))
               for sam in core]
        #samplelen, samples, hiatus array (5, #hiatusi), sections, a, b, minyear, maxyear
        #theta0, thetap0, c0, cm, outputfilename, how many samples to run?
        
        #Okay! now to set these parameters sanely, and then based on A to the I!
        baconc.run_simulation(len(det), det, numpy.empty((5, 0)), 20, 3, 4, 12000, 21550,
                             50, 50, 50, 50, 'baconoutofdoom', 10)
        
      
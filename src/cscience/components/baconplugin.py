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
        #should sort
        #TODO: handle ages without distributions.
        #TODO: confirm my distributions look as they should here...
        det = [(str(sam['id']), float(sam['Calibrated 14C Age'].magnitude),
                sam['Calibrated 14C Age'].uncertainty.as_single_mag(), 
                float(sam['depth'].magnitude), 3, 4, 
                getattr(sam['Calibrated 14C Age'].uncertainty.distribution, 'x', []),
                getattr(sam['Calibrated 14C Age'].uncertainty.distribution, 'y', []))
               for sam in core]
        det.sort(key=lambda x: x[3]) #sort by depth
        det = [baconc.PreCalDet(*dets) for dets in det]
        
        #samplelen, samples, hiatus array (5, #hiatusi), sections, memorya, memoryb, minyear, maxyear
        #ageguess1, ageguess2, mindepth, maxdepth, outputfilename, how many samples to run?
        
        #memorya and memoryb are calculated from "mean" and "strength" params as:
        #a = strength*mean
        #b = strength*(1-mean)
        
        #accum rate is passed per-hiatus, with a dummy hiatus at the front
        #of the array to pass the youngest such rate.
        #has alpha and beta set as: alpha = accum shape, beta = accum shape/accum mean
        
        #Okay! now to set these parameters sanely, and then based on A to the I!
        baconc.run_simulation(len(det), det, numpy.empty((5, 0)), 200, 2.8, 1.2, -1000, 999999999,
                             443, 453, 43.5, 1888.5, 'temp/baconout.txt', 10)
        
      
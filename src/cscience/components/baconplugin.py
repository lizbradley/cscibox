import rpy2
import rpy2.rinterface
import rpy2.robjects

import cscience
import cscience.components
from cscience.components import UncertainQuantity

class BaconInterpolation(cscience.components.BaseComponent):
    visible_name = 'Interpolate Using BACON (Coming Soon!)'
    inputs = {'required':('Calibrated 14C Age',)}
    
    def prepare(self, *args, **kwargs):
        super(BaconInterpolation, self).prepare(*args, **kwargs)
        
        bacon_loc = self.get_plugin_location('bacon')
        rpy2.rinterface.initr()
        rpy2.robjects.r('''setwd('%s')''' % bacon_loc)
        rpy2.robjects.r('''source('Bacon.R')''')
        
    def run_component(self, core):
        print 'Bacon should be running proply...'
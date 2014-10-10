import cscience
import cscience.components
from cscience.components import UncertainQuantity

class BaconInterpolation(cscience.components.BaseComponent):
    visible_name = 'Interpolate Using BACON (Coming Soon!)'
    inputs = {'required':('Calibrated 14C Age',)}
    
    def run_component(self, core):
        pass
    
"""
    rpy2.robjects.r('''setwd('/Users/silverrose/MacBacon_2.2')''')
<StrVector - Python:0x117e19ef0 / R:0x118f79b68>
[str]
rpy2.robjects.r('''source('Bacon.R')''')
    """
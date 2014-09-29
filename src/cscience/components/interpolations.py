import cscience.components
import scipy.interpolate
from cscience.components import UncertainQuantity


class InterpolateModelLinear(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (Linear Spline)'
    inputs = {'required':('Calibrated 14C Age',)}
    #outputs = {} #TODO: add an output type that is an object, for great justice
    
    def run_component(self, core):
        #need to have x monotonically increasing...
        xyvals = zip(*sorted([(sample['depth'], 
                               sample['Calibrated 14C Age'])
                              for sample in core]))
        interp = scipy.interpolate.interp1d(*xyvals, kind='slinear')
        core['all']['age/depth model'] = interp
    

class UseModel(cscience.components.BaseComponent):
    
    visible_name = 'Assign Ages Using Age-Depth Model'
    #inputs = {'all':('age/depth model',)}
    outputs = {'Model Age': ('float', 'years', True)}

    def run_component(self, core):
        #so this component is assuming that the age-depth model has already
        #been interpolated using some method, and is now associating ages
        #based on that model with all points along the depth curve.
        age_model = core['all']['age/depth model']
        for sample in core:
            sample['Model Age'] = UncertainQuantity(age_model(sample['depth']),
                                                    'years')
            
        #TODO: allow uncertainty...
            
    
        
        
        
        
import cscience.components
import scipy.interpolate


#TODO: now to make this actually work!

class InterpolateModel(cscience.components.BaseComponent):
    #TODO: generalize age input
    #TODO: parameter determining interpolation type
    #TODO: error?
    visible_name = 'Interpolate an Age-Depth Model'
    inputs = {'required':('Calibrated 14C Age',)}
    
    def run_component(self, core):
        core['all']['agedepth_model'] = scipy.interpolate.interp1d(
                zip(*[(sample['depth'], sample['Calibrated 14C Age'])]), kind='linear')
    

class UseModel(cscience.components.BaseComponent):
    
    visible_name = 'Assign Ages Using Age-Depth Model'
    inputs = {'all':('agedepth_model',)}
    outputs = {'Model Age': ('float', 'years', True)}

    def run_component(self, core):
        #so this component is assuming that the age-depth model has already
        #been interpolated using some method, and is now associating ages
        #based on that model with all points along the depth curve.
        age_model = core['all']['agedepth_model']
        for sample in core:
            sample['Model Age'] = age_model(sample['depth'])
            
    
        
        
        
        
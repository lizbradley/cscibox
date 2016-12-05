import cscience.components
from cscience.components import ComponentAttribute as Att
import numpy as np
import scipy.interpolate
import scipy.stats

from cscience.framework import datastructures    
    

class InterpolateModelLinear(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (Linear Spline)'
    inputs = [Att('depth', required=True), Att('Calibrated 14C Age', required=True)]
    outputs = [Att('Age/Depth Model', type='age model', core_wide=True)]

    def run_component(self, core, progress_dialog):
        #need to have x monotonically increasing...
        xyvals = zip(*sorted([(sample['depth'],
                               sample['Calibrated 14C Age'])
                              for sample in core]))
        core.properties['Age/Depth Model'] = datastructures.PointlistInterpolation(*xyvals)

class InterpolateModelSpline(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (B-Spline)'
    inputs = [Att('depth', required=True), Att('Calibrated 14C Age', required=True)]
    outputs = [Att('Age/Depth Model', type='age model', core_wide=True)]

    def run_component(self, core, progress_dialog):
        xyvals = zip(*sorted([(sample['depth'],
                               sample['Calibrated 14C Age'])
                              for sample in core]))
        tck, u = scipy.interpolate.splprep(xyvals, s=200000)
        x_i, y_i = scipy.interpolate.splev(np.linspace(0, 1, 100), tck)
        xyvals = zip(*sorted([(x_i, y_i)]))
        core.properties['Age/Depth Model'] = datastructures.PointlistInterpolation(*xyvals)

class InterpolateModelRegression(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (Linear Regression)'
    inputs = [Att('depth', required=True), Att('Calibrated 14C Age', required=True)]
    outputs = [Att('Age/Depth Model', type='age model', core_wide=True)]

    def run_component(self, core, progress_dialog):
        x = [sample['depth'].item() for sample in core]
        y = [sample['Calibrated 14C Age'] for sample in core]
        slope, y_intcpt, r_value, p_value, std_err = scipy.stats.linregress(x, y)
        xyvals = zip(*sorted([(i, y_intcpt + slope * i)
                              for i in x]))
        core.properties['Age/Depth Model'] = datastructures.PointlistInterpolation(*xyvals)

class InterpolateModelCubic(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (Cubic)'
    inputs = [Att('depth', required=True), Att('Calibrated 14C Age', required=True)]
    outputs = [Att('Age/Depth Model', type='age model', core_wide=True)]

    def run_component(self, core, progress_dialog):
        x = [sample['depth'] for sample in core]
        y = [sample['Calibrated 14C Age'] for sample in core]
        interp_func = scipy.interpolate.interp1d([float(i) for i in x], [float(i) for i in y],
                               bounds_error=False, fill_value=0, kind='cubic')
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        xyvals = zip(*sorted([(i, interp_func(i)) for i in new_x]))
        core.properties['Age/Depth Model'] = datastructures.PointlistInterpolation(*xyvals) 

class InterpolateModelQuadratic(cscience.components.BaseComponent):
    visible_name = 'Interpolate Age/Depth Model (Quadratic)'
    inputs = [Att('depth', required=True), Att('Calibrated 14C Age', required=True)]
    outputs = [Att('Age/Depth Model', type='age model', core_wide=True)]

    def run_component(self, core, progress_dialog):
        x = [sample['depth'] for sample in core]
        y = [sample['Calibrated 14C Age'] for sample in core]
        interp_func = scipy.interpolate.interp1d([float(i) for i in x], [float(i) for i in y],
                               bounds_error=False, fill_value=0, kind='quadratic')
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        xyvals = zip(*sorted([(i, interp_func(i)) for i in new_x]))
        core.properties['Age/Depth Model'] = datastructures.PointlistInterpolation(*xyvals) 

class UseModel(cscience.components.BaseComponent):

    visible_name = 'Assign Ages Using Age-Depth Model'
    inputs = [Att('Age/Depth Model', core_wide=True, required=True)]
    outputs = [Att('Model Age', type='float', unit='years', error=True)]

    def run_component(self, core, progress_dialog):
        #so this component is assuming that the age-depth model has already
        #been interpolated using some method, and is now associating ages
        #based on that model with all points along the depth curve.
        age_model = core.properties['Age/Depth Model']
        for sample in core:
            sample['Model Age'] = age_model(sample['depth'])
        

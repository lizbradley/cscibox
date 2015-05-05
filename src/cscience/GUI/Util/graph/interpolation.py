import numpy as np
from scipy.interpolate import interp1d

class LinearInterpolationStrategy:
    def __init__(self):
        pass
    def interpolate(self, x, y):
        self = self # shutup pylint
        return (x, y)

class SciInterpolationStrategy:
    def __init__(self, kind):
        self.kind = kind

    def interpolate(self, x, y):
        interp_func = interp1d([float(i) for i in x], [float(i) for i in y], 
                               bounds_error=False, fill_value=0, kind=self.kind)
        new_x = np.arange(min(x), max(x), abs(max(x)-min(x))/100.0)
        return (new_x, interp_func(new_x))

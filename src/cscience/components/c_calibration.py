import cscience
import cscience.components

import operator
import math
import heapq
import collections
import quantities as pq

import numpy as np
from scipy import stats, interpolate, integrate
from cscience.framework.samples import UncertainQuantity
from cscience.framework.samples import Uncertainty


class Distribution(stats.rv_continuous):
    
    def __init__(self, comp, avg, err, norm, sigma):
        self.component = comp
        self.average = avg
        self.error = err
        self.norm = norm
        self.sigma = sigma
        
    #TODO: this distribution is non-functional right now, and only saving a
    #few of its helpful datas; let's get it all workin all good!
    def __getstate__(self):
        return (self.average, self.error, self.norm)
    
    def __setstate__(self, state):
        self.average, self.error, self.norm = state
        self.component = None
        
    def _cdf(self, x):
        return 0
        return self.component.norm_density(self.average, self.error, self.norm, x, self.sigma[x])

class ResevoirCorrection(cscience.components.BaseComponent):
    visible_name = 'ResevoirCorrection'

    def prepare(self, *args, **kwargs):
        print "Prepare"

    def run_component(self, samples):
        try: 
            for sample in samples:
                toAdd = UncertainQuantity(data=10, units='years')
                resevoirCorrection = sample['14C Age'] + toAdd
                sample['Calibrated 14C Age'] = resevoirCorrection
        except Exception as e:
            import traceback
            print repr(e)
            print traceback.format_exc()
            

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (IntCal)'
    inputs = {'required':('14C Age')}
    outputs = {'Calibrated 14C Age':('float', 'years')}

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}
    
    def prepare(self, *args, **kwargs):
        super(IntCalCalibrator, self).prepare(*args, **kwargs)
        
        self.curve = self.paleobase[self.computation_plan['calibration curve']]
            
        self.cAge_C14Age = {}
        self.cAge_Sigma = {}
        self.c14Age_CAge = {}
        for row in self.curve.itervalues():
            self.cAge_C14Age[row['Calibrated Age']] = row['14C Age'] 
            self.cAge_Sigma[row['Calibrated Age']] = row['Sigma']
            self.c14Age_CAge[row['14C Age']] = row['Calibrated Age']
                            
        self.cAge_C14Age = collections.OrderedDict(sorted(self.cAge_C14Age.items()))
        self.cAge_Sigma = collections.OrderedDict(sorted(self.cAge_Sigma.items()))
        self.c14Age_CAge = collections.OrderedDict(sorted(self.c14Age_CAge.items()))
        
        self.firstYear = int(self.cAge_C14Age.keys()[0])
        self.lastYear = int(self.cAge_C14Age.keys()[-1])
        
        self.x = np.array(self.cAge_C14Age.keys())
        c14 = np.array(self.cAge_C14Age.values())
        sigma = np.array(self.cAge_Sigma.values())
        cAge = np.array(self.c14Age_CAge.values())
        c14_2 = np.array(self.c14Age_CAge.keys())
        
        self.g = interpolate.interp1d(self.x,c14, 'slinear')
        self.ig = interpolate.interp1d(c14_2, cAge)
        self.sigma_c = interpolate.interp1d(self.x, sigma, 'slinear')
    
    def run_component(self, samples):
        for sample in samples:
            try:
                age = sample['14C Age']
                output = self.convert_age(age)
                sample['Calibrated 14C Age'] = output
            except ValueError:
                #sample out of bounds for interpolation range? we can just
                #ignore that.
                pass

    # inputs: CAL BP and Sigma, output: un-normed probability density        
    def density(self, avg, error, x, s):
        sig2 = error**2. + s**2.
        exponent = -((self.g(x) - avg)**2.)/(2.*sig2)
        alpha = 1./math.sqrt(2.*np.pi*sig2);
        return alpha * math.exp(exponent)
    
    # inputs same as density above plus norm, output: probability density
    def norm_density(self, avg, error, norm, x, s):
        return self.density(avg, error, x, s)/norm
                      
    def convert_age(self, age):
        """
        returns a "base" calibrated age interval 
        """
        avg = age.magnitude
        error = age.uncertainty.magnitude[0].magnitude

        y = np.zeros(len(self.x))
        for index, z in enumerate(self.x):
            y[index] = self.density(avg, error, z, self.sigma_c(z))
        norm = integrate.simps(y, self.x)
        for index, z in enumerate(self.x):
            y[index] = z*y[index]/norm
            
        #TODO: this is not by any means the best way ever of representing these
        #various values, nor of calculating them -- we should try to at least
        #use the same darn algorithm for error & age, but that is just too hard
        #for me at this time, and this at least seems to work?

        #TODO: Fix me! This forces the distribution object to be recalculated
        #for graphing -- surely we should just use the existing prob dist!
        
        mean = int(round(integrate.simps(y, self.x)))
        err = self.hdr(avg, error, norm)
        err = (int(round(err[1] - mean)), int(round(mean - err[0])))
        distr = Distribution(self, mean, err, norm, self.sigma_c)
        cal_age = cscience.components.UncertainQuantity(data=mean, units='years', uncertainty=distr)
        return cal_age
    
    def hdr(self, age, error, norm):
        alpha = 0
        center = self.ig(age)
        year_before = center - 1
        year_after = center + 1
        theta = [(self.norm_density(age, error, norm, center, self.sigma_c(center)), center)]
        alpha += theta[0][0]
        while alpha < 0.69:
            before = (self.norm_density(age, error, norm, year_before, self.sigma_c(year_before)), year_before)
            after = (self.norm_density(age, error, norm, year_after, self.sigma_c(year_after)), year_after)
            alpha += before[0] + after[0]
            heapq.heappush(theta, before)
            heapq.heappush(theta, after)
            year_before -=1
            year_after +=1
        while alpha > 0.68:
            alpha -= heapq.heappop(theta)[0]
        theta.sort(key=operator.itemgetter(1))
        return (theta[0][1], theta[-1][1])
        
        

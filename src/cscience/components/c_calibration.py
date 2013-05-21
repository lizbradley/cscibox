import itertools

import cscience.components
from cscience.components import datastructures
import collections
import numpy as np
import scipy.interpolate as interp
import scipy.integrate as integ

#TODO: it appears that the "correct" way of doing this is to run a probabilistic
#model over the calibration set to get the best possible result
class SimpleIntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Simple Carbon 14 Calibration (IntCal)'
    inputs = {'required':('14C Age',), 'optional':('14C Age Error',)}
    outputs = ('Calibrated 14C Age', 'Calibrated 14C Age Error-', 
               'Calibrated 14C Age Error+')
    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Error')}
    params = {'calibration curve 2':('CAL BP', '14C age', 'Sigma')}
    
    def run_component(self, samples):
        self.curve = datastructures.collection_to_bintree(
                    self.paleobase[self.computation_plan['calibration curve']], 
                    '14C Age')
        
        for sample in samples:
            age, baseerr = self.convert_age(sample['14C Age'])
            sample['Calibrated 14C Age'] = age
            sample['Calibrated 14C Age Error-'] = baseerr 
            sample['Calibrated 14C Age Error+'] = baseerr
            if sample['14C Age Error']:
                minage = self.convert_age(sample['14C Age'] - sample['14C Age Error'])[0]
                sample['Calibrated 14C Age Error-'] += (age - minage)
                maxage = self.convert_age(sample['14C Age'] + sample['14C Age Error'])[0]
                sample['Calibrated 14C Age Error+'] += (maxage - age)
            
    def convert_age(self, age):
        """
        returns a "base" calibrated age and an error +/- 
        """
        #for this age value, what I want are:
        #min cal age, max cal age, max error
        data = self.curve.get_range_nodes(age)
        #56000 is the approx max dating range of c14
        maxerr = 0
        if not data[0]:
            #guess
            minage = age - 10000
            d0 = []
        else:
            minage = 56000
            d0 = data[0].data
        if not data[1]:
            #guess
            maxage = age + 10000
            d1 = []
        else:
            maxage = 0
            d1 = data[1].data
        
        #TODO: this is a mathematical hack because probability is hard.
        for entry in itertools.chain(d0, d1):
            minage = min(minage, entry['Calibrated Age'])
            maxage = max(maxage, entry['Calibrated Age'])
            maxerr = max(maxerr, entry['Error'])
        diff = (maxage - minage) / 2
        maxerr += diff
        return (minage + diff, maxerr)

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (IntCal)'
    inputs = {'required':('14C Age', '14C Age Error')}
    outputs = ('Calibrated 14C Age', 'Calibrated 14C Age Error', 
              'Calibrated 14C 95th percentile', 'Calibrated 14C Median', 
              'Calibrated 14C Highest Posterior Density')
    params = {'calibration curve':('CAL BP', '14C age', 'Sigma')}
    
    def run_component(self, samples):
        self.curve = self.computation_plan['calibration curve']
        data = self.curve.values()
        xyz = {}
        for row in data:
            xyz[row['CAL BP']] = (row['14C age'], row['Sigma'])
        xyz = collections.OrderedDict(sorted(xyz.items()))
        cal_bp = np.array([])
        c14 = np.array([])
        sigma = np.array([])
        for k,v in xyz.iteritems():
            cal_bp = np.append(cal_bp, k)
            c14 = np.append(c14, v[1])
            sigma = np.append(sigma, v[2])       
        cal_bp = np.delete(cal_bp, 0)
        c14 = np.delete(c14, 0)
        sigma = np.delete(sigma, 0)
        g = interp.interp1d(cal_bp,c14, 'slinear')
        norm, nerr = integ.quad(p, x[0], x[-1])
        
        for sample in samples:
            age, baseerr, sigma2, median, posterior = self.convert_age(sample['14C Age'], 
                                                            sample['14C Age Error'])
            sample['Calibrated 14C Age'] = age
            sample['Calibrated 14C Age Error'] = baseerr 
            sample['Calibrated 14C 95th percentile'] = sigma2
            sample['Calibrated 14C Median'] = median
            sample['Calibrated 14C Highest Posterior Density'] = posterior
            
                
    def convert_age(self, age, error):
        """
        returns a "base" calibrated age and an error +/- 
        """
        #for this age value, what I want are:
        #min cal age, max cal age, max error
        
        
        mean = 1
        sigma1 = mean
        sigma2 = mean
        median = mean
        posterior = mean
        return (mean, sigma1, sigma2, median, posterior)
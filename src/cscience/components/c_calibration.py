import itertools

import cscience.components
from cscience.components import datastructures
import collections
import numpy as np
import scipy.interpolate as interp
import scipy.integrate as integ
import operator
import time
from scipy.stats import norm
import math
import heapq
#TODO: it appears that the "correct" way of doing this is to run a probabilistic
#model over the calibration set to get the best possible result
class SimpleIntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Simple Carbon 14 Calibration (IntCal)'
    inputs = {'required':('14C Age',), 'optional':('14C Age Error',)}
    outputs = ('Calibrated 14C Age', 'Calibrated 14C Age Error-', 
               'Calibrated 14C Age Error+')
    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Error')}
    
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
    outputs = ('Calibrated 14C HDR 68%-',
               'Calibrated 14C HDR 68%+', 'Relative Area 68%',
               'Calibrated 14C HDR 95%-', 'Calibrated 14C HDR 95%+',
               'Relative Area 95%')

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}
    
    def run_component(self, samples):
        try:
            self.curve = self.paleobase[self.computation_plan['calibration curve']]
            data = self.curve.values()
            
            self.cAge_C14Age = {}
            self.cAge_Sigma = {}
            self.c14Age_CAge = {}
            for row in data:
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
            
            self.g = interp.interp1d(self.x,c14, 'slinear')
            self.ig = interp.interp1d(c14_2, cAge)
            self.sigma_c = interp.interp1d(self.x, sigma, 'slinear')
            
            for sample in samples:
                (hdr_68, relative_area_68, 
                 hdr_95, relative_area_95) = self.convert_age(sample['14C Age'], sample['14C Age Error'])
                sample['Calibrated 14C HDR 68%-'] = hdr_68[0]
                sample['Calibrated 14C HDR 68%+'] = hdr_68[1]
                sample['Relative Area 68%'] = relative_area_68
                sample['Calibrated 14C HDR 95%-'] = hdr_95[0]
                sample['Calibrated 14C HDR 95%+'] = hdr_95[1]
                sample['Relative Area 95%'] = relative_area_95
                
        except:
            import traceback
            print traceback.format_exc()
    
    # inputs: CAL BP and Sigma, output: unnormed density        
    def density(self, avg, error, x, s):
            sig2 = error**2. + s**2.
            exponent = -((self.g(x) - avg)**2.)/(2.*sig2)
            alpha = 1./math.sqrt(2.*np.pi*sig2);
            return alpha * math.exp(exponent)

                      
    def convert_age(self, age, error):
        """
        returns a "base" calibrated age interval 
        """

        y = np.zeros(len(self.x))
        for index, z in enumerate(self.x):
            y[index] = self.density(age, error, z, self.sigma_c(z))

        norm = integ.simps(y, self.x)

        def norm_density(x,s):
            return self.density(age, error, x, s)/norm

        alpha = 0
        center = self.ig(age)
        year_before = center - 1
        year_after = center + 1
        theta = [(norm_density(center, self.sigma_c(center)), center)]
        alpha += theta[0][0]
        while alpha < 0.96:
            before = (norm_density(year_before, self.sigma_c(year_before)), year_before)
            after = (norm_density(year_after, self.sigma_c(year_after)), year_after)
            alpha += before[0] + after[0]
            heapq.heappush(theta, before)
            heapq.heappush(theta, after)
            year_before -=1
            year_after +=1
        while alpha > 0.95:
            alpha -= heapq.heappop(theta)[0]
        upsilon = list(theta)
        while (alpha > 0.68):
            alpha -= heapq.heappop(theta)[0]
            
        upsilon.sort(key=operator.itemgetter(1))
        theta.sort(key=operator.itemgetter(1))
        
        hdr_68 = [theta[0][1]]
        relative_area_68 = []
        temp = 0
        for r in range(1,len(theta)):
            temp += theta[r-1][0]
            if (theta[r][1] - theta[r-1][1]) > 1:
                hdr_68.append(theta[r-1][1])
                hdr_68.append(theta[r][1])
                relative_area_68.append(temp)
                temp = 0
        hdr_68.append(theta[-1][1])
        relative_area_68.append(temp)
        index, value = max(enumerate(relative_area_68), key=operator.itemgetter(1))
        relative_area_68 = value
        hdr_68 = (int(round(hdr_68[2*index])), int(round(hdr_68[2*index + 1])))
                  
        hdr_95 = [upsilon[0][1]]
        relative_area_95 = []
        temp = 0
        for r in range(1,len(upsilon)):
            temp += upsilon[r-1][0]
            if (upsilon[r][1] - upsilon[r-1][1]) > 1:
                hdr_95.append(upsilon[r-1][1])
                hdr_95.append(upsilon[r][1])
                relative_area_95.append(temp)
                temp = 0
        hdr_95.append(upsilon[-1][1])
        relative_area_95.append(temp)
        index, value = max(enumerate(relative_area_95), key=operator.itemgetter(1))
        relative_area_95 = value
        hdr_95 = (int(round(hdr_95[2*index])), int(round(hdr_95[2*index + 1])))
        return (hdr_68, relative_area_68,hdr_95, relative_area_95)
        
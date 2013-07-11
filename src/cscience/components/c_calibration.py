import itertools

import cscience.components
from cscience.components import datastructures
import collections
import numpy as np
import scipy.interpolate as interp
import scipy.integrate as integ
import operator

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
    outputs = ('Calibrated 14C Age', 'Calibrated 14C Age Error',
               'Calibrated 14C Two Sigma', 'Calibrated 14C HDR 68%-',
               'Calibrated 14C HDR 68%+', 'Relative Area 68%',
               'Calibrated 14C HDR 95%- 1', 'Calibrated 14C HDR 95%+ 1',
               'Relative Area 95% 1','Calibrated 14C HDR 95%- 2', 
               'Calibrated 14C HDR 95%+ 2', 'Relative Area 95% 2',
               'Calibrated 14C HDR 95%- 3', 'Calibrated 14C HDR 95%+ 3',
               'Relative Area 95% 3')

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}
    
    def run_component(self, samples):
        try:
            self.curve = self.paleobase[self.computation_plan['calibration curve']]
            data = self.curve.values()
            xyz = {}
            for row in data:
                xyz[row['Calibrated Age']] = (row['14C Age'], row['Sigma'])
            xyz = collections.OrderedDict(sorted(xyz.items()))
            cal_bp = np.array([])
            c14 = np.array([])
            sigma = np.array([])
            for k,v in xyz.iteritems():
                cal_bp = np.append(cal_bp, k)
                c14 = np.append(c14, v[0])
                sigma = np.append(sigma, v[1])       
            self.cal_bp = np.delete(cal_bp, 0)
            c14 = np.delete(c14, 0)
            sigma = np.delete(sigma, 0)
            self.g = interp.interp1d(self.cal_bp,c14, 'slinear')
            self.sigma_c = interp.interp1d(c14, sigma, 'slinear')
            self.intervals = range(int(self.cal_bp[0]), int(self.cal_bp[-1]),100)
            if self.intervals[-1] != int(self.cal_bp[-1]):
                self.intervals.append(int(self.cal_bp[-1]))
            self.partition = range(1,len(self.intervals))
            
            for sample in samples:
                (mean, sigma1, sigma2, hdr_68, relative_area_68, 
                 hdr_95, relative_area_95) = self.convert_age(sample['14C Age'], sample['14C Age Error'])
                sample['Calibrated 14C Age'] = round(mean)
                sample['Calibrated 14C Age Error'] = round(sigma1)
                sample['Calibrated 14C Two Sigma'] = round(sigma2)
                sample['Calibrated 14C HDR 68%-'] = hdr_68[0]
                sample['Calibrated 14C HDR 68%+'] = hdr_68[1]
                sample['Relative Area 68%'] = relative_area_68[0]
                sample['Calibrated 14C HDR 95%- 1'] = hdr_95[0]
                sample['Calibrated 14C HDR 95%+ 1'] = hdr_95[1]
                sample['Relative Area 95% 1'] = relative_area_95[0]
                if len(hdr_95) > 2:
                    sample['Calibrated 14C HDR 95%- 2'] = hdr_95[2]
                    sample['Calibrated 14C HDR 95%+ 2'] = hdr_95[3]
                    sample['Relative Area 95% 2'] = relative_area_95[1]
                else:
                    sample['Calibrated 14C HDR 95%- 2'] = 0
                    sample['Calibrated 14C HDR 95%+ 2'] = 0
                    sample['Relative Area 95% 2'] = 0
                if len(hdr_95) > 4: 
                    sample['Calibrated 14C HDR 95%- 3'] = hdr_95[4]
                    sample['Calibrated 14C HDR 95%+ 3'] = hdr_95[5]
                    sample['Relative Area 95% 3'] = relative_area_95[2]
                else:
                    sample['Calibrated 14C HDR 95%- 3'] = 0
                    sample['Calibrated 14C HDR 95%+ 3'] = 0
                    sample['Relative Area 95% 3'] = 0
        except:
            import traceback
            print traceback.format_exc()
            
                
    def convert_age(self, age, error):
        """
        returns a "base" calibrated age and an error +/- 
        """
        #for this age value, what I want are:
        #min cal age, max cal age, max error
        
        def density(x):
            sigma = np.sqrt(error**2. + (self.sigma_c(age))**2.)
            exponent = -((self.g(x) - np.float64(age))**2.)/(2.*sigma**2)
            alpha = 1./np.sqrt(2.*np.pi*sigma**2);
            return alpha * np.exp(exponent)

        norm,temp = 0,0
        for i in self.partition:
            (temp,_) = integ.quad(density, self.intervals[i-1], self.intervals[i], limit=200)
            norm += temp

        def norm_density(x):
            return density(x)/norm
        def weighted_density(x):
            return x * norm_density(x)
        
        mean, temp = 0,0
        for i in self.partition:
            (temp,_) = integ.quad(weighted_density, self.intervals[i-1], self.intervals[i], limit=200)
            mean += temp
        
        def weighted2_density(x):
            return x**2. * norm_density(x)
            
        variance, temp = 0,0
        for i in self.partition:
            (temp,_) = integ.quad(weighted2_density, self.intervals[i-1], self.intervals[i], limit=200)
            variance += temp
        
        variance = variance - mean**2.
        sigma1 = np.sqrt(variance)
        sigma2 = 2.*sigma1
        
        #Find the highest density regions (hdr) for 68% and 95% confidence
        
        #Creat list of pairs with first element being bp date and second
        #the probaility of that date
        theta = [(x,norm_density(x)) for x in range(int(self.cal_bp[-1])+1)]
        #Sort pairs by probability
        theta.sort(key=operator.itemgetter(1))
        
        #Determine index of 68% confidence and create list of pairs
        #sorted by bp date.
        alpha = 0
        m = len(theta)/2
        while((alpha < 0.675) or (alpha > 0.695)):
            alpha = 0
            for x in range(len(theta)-1, (len(theta)-1 - m), -1):
                alpha += theta[x][1]
            if alpha < 0.675:
                m += (m/2)
            elif alpha > 0.695:
                m -= (m/2)
        m = len(theta)-1 - m
        upsilon = theta[m:]
        upsilon.sort(key=operator.itemgetter(0))
        
        #Determine index of 95% confidence and create list of pairs
        #sorted by bp date.
        alpha = 0
        m = len(theta)/2
        while((alpha < 0.945) or (alpha > 0.965)):
            alpha = 0
            for x in range(len(theta)-1, (len(theta)-1 - m), -1):
                alpha += theta[x][1]
            if alpha < 0.945:
                m += (m/2)
            elif alpha > 0.965:
                m -= (m/2)
        m = len(theta)-1 - m
        phi = theta[m:]
        phi.sort(key=operator.itemgetter(0))
        
        #Determine interval of 68% confidence as list of bp dates
        #which should only be two dates and relative area which
        #should be 0.68
        hdr_68 = [upsilon[0][0]]
        relative_area_68 = []
        temp = 0
        for r in range(1,len(upsilon)):
            temp += upsilon[r-1][1]
            if (upsilon[r][0] - upsilon[r-1][0]) > 1:
                hdr_68.append(upsilon[r-1][0])
                hdr_68.append(upsilon[r][0])
                relative_area_68.append(temp)
                temp = 0
        hdr_68.append(upsilon[-1][0])
        relative_area_68.append(temp)
        
        #Determine interval(s) of 95% confidence as list of bp dates
        #which may be more than one interval and relative areas of
        #those intervals which should add up to 0.95
        hdr_95 = [phi[0][0]]
        relative_area_95 = []
        temp = 0
        for r in range(1,len(phi)):
            temp += phi[r-1][1]
            if (phi[r][0] - phi[r-1][0]) > 1:
                hdr_95.append(phi[r-1][0])
                hdr_95.append(phi[r][0])
                relative_area_95.append(temp)
                temp = 0
        hdr_95.append(phi[-1][0])
        relative_area_95.append(temp)
        return (mean, sigma1, sigma2, hdr_68, relative_area_68,hdr_95, relative_area_95)
    
    
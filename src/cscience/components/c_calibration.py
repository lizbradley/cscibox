import cscience
import cscience.components
import operator
import math
import heapq
import collections
import numpy as np
from scipy import stats, interpolate, integrate


class Distribution(object):
    
    def __init__(self, comp, density, avg, err, norm, sigma):
        self.component = comp
        self.density = density
        self.average = avg
        self.error = err
        
    # TODO: this distribution is non-functional right now, and only saving a
    # few of its helpful datas; let's get it all workin all good!
    def __getstate__(self):
        return (self.average, self.error)
    
    def __setstate__(self, state):
        self.average, self.error, _ = state
        self.component = None
        
    def _pdf(self, x):
        return self.density(x)

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (IntCal)'
    inputs = {'required':('14C Age')}
    outputs = {'Calibrated 14C Age':('float', 'years')}

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}
    
    def prepare(self, *args, **kwargs):
        super(IntCalCalibrator, self).prepare(*args, **kwargs)
        
        self.curve = self.paleobase[self.computation_plan['calibration curve']]
        #Dictionaries with keys and values from columns in self.curve.
        calibratedAgesToCarbon14Ages = {}
        calibratedAgesToSigmas = {}
        carbon14AgesToCalibratedAges = {}
        for row in self.curve.itervalues():
            calibratedAgesToCarbon14Ages[row['Calibrated Age']] = row['14C Age'] 
            calibratedAgesToSigmas[row['Calibrated Age']] = row['Sigma']
            carbon14AgesToCalibratedAges[row['14C Age']] = row['Calibrated Age']
        #Sort dictionaries by keys.                    
        calibratedAgesToCarbon14Ages = collections.OrderedDict(sorted(calibratedAgesToCarbon14Ages.items()))
        calibratedAgesToSigmas = collections.OrderedDict(sorted(calibratedAgesToSigmas.items()))
        carbon14AgesToCalibratedAges = collections.OrderedDict(sorted(carbon14AgesToCalibratedAges.items()))
        #These are the first and last years of the calibrated (true) age ranges.
        self.firstYear = int(calibratedAgesToCarbon14Ages.keys()[0])
        self.lastYear = int(calibratedAgesToCarbon14Ages.keys()[-1])
        #Convert keys and values of dictionaries to numpy arrays.
        self.sortedCalibratedAges = np.array(calibratedAgesToCarbon14Ages.keys())
        carbon14Ages = np.array(calibratedAgesToCarbon14Ages.values())
        sigmas = np.array(calibratedAgesToSigmas.values())
        calibratedAges = np.array(carbon14AgesToCalibratedAges.values())
        sortedCarbon14Ages = np.array(carbon14AgesToCalibratedAges.keys())
        #These are linear interpolation functions using numpy arrays.
        self.interpolatedC14AgesToCalibratedAges = interpolate.interp1d(self.sortedCalibratedAges, carbon14Ages, 'slinear')
        self.interpolatedCalibratedAgesToC14Ages = interpolate.interp1d(sortedCarbon14Ages, calibratedAges)
        self.interpolatedCalibratedAgesToSigmas = interpolate.interp1d(self.sortedCalibratedAges, sigmas, 'slinear')
    
    def run_component(self, samples):
        for sample in samples:
            try:
                age = sample['14C Age']
                output = self.convert_age(age)
                sample['Calibrated 14C Age'] = output
            except ValueError:
                # sample out of bounds for interpolation range? we can just
                # ignore that.
                pass

    # inputs: CAL BP and Sigma, output: un-normed probability density        
    def density(self, avg, error, x, s):
        sigmaSquared = error ** 2. + s ** 2.
        exponent = -((self.interpolatedC14AgesToCalibratedAges(x) - avg) ** 2.) / (2.*sigmaSquared)
        alpha = 1. / math.sqrt(2.*np.pi * sigmaSquared);
        return alpha * math.exp(exponent)
    
    # inputs same as density above plus norm, output: probability density
    def norm_density(self, avg, error, norm, x, s):
        return self.density(avg, error, x, s) / norm
                      
    def convert_age(self, age):
        """
        returns a "base" calibrated age interval 
        """
        avg = age.magnitude
        error = age.uncertainty.magnitude[0].magnitude
        unnormedDensity = np.zeros(len(self.sortedCalibratedAges))
        for index, year in enumerate(self.sortedCalibratedAges):
            unnormedDensity[index] = self.density(avg, error, year, self.interpolatedCalibratedAgesToSigmas(year))
        norm = integrate.simps(unnormedDensity, self.sortedCalibratedAges)
        normedDensity = unnormedDensity / norm
        weightedDensity = np.zeros(len(self.sortedCalibratedAges))
        for index, year in enumerate(self.sortedCalibratedAges):
            weightedDensity[index] = year * normedDensity[index]
        mean = integrate.simps(weightedDensity, self.sortedCalibratedAges)
        interpolatedNormedDensity = interpolate.interp1d(self.sortedCalibratedAges, normedDensity, 'slinear')
        #def distribution(x, s):
        #    self.norm_density(avg, error, norm, x, s)
        calibratedAgeError = self.hdr(interpolatedNormedDensity, avg)[0]
        distr = Distribution(self, interpolatedNormedDensity, mean, calibratedAgeError)
        cal_age = cscience.components.UncertainQuantity(data=mean, units='years', uncertainty=distr)
        return cal_age
    
    def high_density_region(self, dist, age):
        pass
    hdr = high_density_region
        
    def hdr(self, distribution, age):
        alpha = 0
        center = self.interpolatedCalibratedAgesToC14Ages(age)
        year_before = center - 1
        year_after = center + 1
        theta = [(distribution(center), center)]
        alpha += theta[0][0]
        while alpha < 0.96:
            before = (distribution(year_before), year_before)
            after = (distribution(year_after), year_after)
            alpha += before[0] + after[0]
            heapq.heappush(theta, before)
            heapq.heappush(theta, after)
            year_before -= 1
            year_after += 1
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
        for r in range(1, len(theta)):
            temp += theta[r - 1][0]
            if (theta[r][1] - theta[r - 1][1]) > 1:
                hdr_68.append(theta[r - 1][1])
                hdr_68.append(theta[r][1])
                relative_area_68.append(temp)
                temp = 0
        hdr_68.append(theta[-1][1])
        relative_area_68.append(temp)
        index, value = max(enumerate(relative_area_68), key=operator.itemgetter(1))
        relative_area_68 = value
        hdr_68 = (int(round(hdr_68[2 * index])), int(round(hdr_68[2 * index + 1])))
                  
        hdr_95 = [upsilon[0][1]]
        relative_area_95 = []
        temp = 0
        for r in range(1, len(upsilon)):
            temp += upsilon[r - 1][0]
            if (upsilon[r][1] - upsilon[r - 1][1]) > 1:
                hdr_95.append(upsilon[r - 1][1])
                hdr_95.append(upsilon[r][1])
                relative_area_95.append(temp)
                temp = 0
        hdr_95.append(upsilon[-1][1])
        relative_area_95.append(temp)
        index, value = max(enumerate(relative_area_95), key=operator.itemgetter(1))
        relative_area_95 = value
        hdr_95 = (int(round(hdr_95[2 * index])), int(round(hdr_95[2 * index + 1])))
        
        return (hdr_68, relative_area_68, hdr_95, relative_area_95)
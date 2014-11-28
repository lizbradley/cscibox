import cscience
import cscience.components
from cscience.components import UncertainQuantity

import numpy as np
from scipy import stats, interpolate, integrate
import calvin.argue
import time

class Distribution(object):
    
    def __init__(self, years, density, avg, range):
        self.x = years
        self.y = density
        self.average = avg
        self.error = (range[1]-avg, avg-range[0])
    
    def __setstate__(self, state):
        if 'x' in state:
            self.__dict__ = state
        else:
            try:
                self.average = state[0]
                self.error = state[1]
            except KeyError:
                print state
                self.__dict__ = state
            except:
                print state
                self.x = []
                self.y = []
                self.average = 0
                self.error = 0
        
class ReservoirCorrection(cscience.components.BaseComponent):
    visible_name = 'Reservoir Correction'
    inputs = {'required':('14C Age',)}
    outputs = {'Corrected 14C Age': ('float', 'years', True), 
               'Reservoir Correction':('float', 'years', True)}

    def run_component(self, core):
        adjustment = calvin.argue.find_value('reservoir adjustment', core)
        adj = UncertainQuantity(adjustment['Adjustment'], 'years',
                                adjustment['+/- Adjustment Error'])
      
        for sample in core:
            sample['Reservoir Correction'] = adj
            sample['Corrected 14C Age'] = sample['14C Age'] + (-adj)
            

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (CALIB Style)'
    inputs = {'required':('14C Age',), 'optional':('Corrected 14C Age',)}
    outputs = {'Calibrated 14C Age':('float', 'years', True)}

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}
    
    def prepare(self, *args, **kwargs):
        super(IntCalCalibrator, self).prepare(*args, **kwargs)
        
        #set up 3 lists, correlated by index, sorted by calibrated age, containing:
        #calibrated age, carbon 14 age, sigma value
        #from the configured calibration curve.
        curve = [(r['Calibrated Age'], r['14C Age'], r['Sigma']) for r in 
                 self.paleobase[self.computation_plan['calibration curve']].itervalues()]
        curve.sort()
        self.calib_age_ref, self.c14_age, self.sigmas = map(np.array, zip(*curve))

    def run_component(self, core):
        interval = 0.683
        for sample in core:
            try:
                age = sample['Corrected 14C Age'] or sample['14C Age']
                sample['Calibrated 14C Age'] = self.convert_age(age, interval)
            except ValueError:
                # sample out of bounds for interpolation range? we can just
                # ignore that.
                pass

    # inputs: CAL BP and Sigma, output: un-normed probability density        
    def density(self, avg, error):
        sigmasq = error ** 2. + self.sigmas ** 2.
        exponent = -((self.c14_age - avg) ** 2.) / (2.*sigmasq)
        alpha = 1. / np.sqrt(2.*np.pi * sigmasq);
        return alpha * np.exp(exponent)
                 
    def convert_age(self, age, interval):
        """
        returns a "base" calibrated age interval 
        """

        #Assume that Carbon 14 ages are normally distributed with mean being
        #Carbon 14 age provided by lab and standard deviation from intCal CSV.
        #This probability density is mapped to calibrated (true) ages and is 
        #no longer normally (Gaussian) distributed or normalized.
        unnormed_density = self.density(*age.unitless_normal())

        #unnormed_density is mostly zeros so need to remove but need to know years removed.
        nz_ages = []
        nz_density = []

        for calage, dens in zip(self.calib_age_ref, unnormed_density):
            if dens:
                #TODO: should this be done in some more efficient way? probably
                nz_ages.append(calage)
                nz_density.append(dens)

        calib_age_ref = np.array(nz_ages)
        unnormed_density = np.array(nz_density)
        # interpolate unnormed density to annual resolution
        annual_calib_ages = np.array(
                    range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))
        unnormed_density = np.interp(annual_calib_ages, 
                                     calib_age_ref, unnormed_density)
        calib_age_ref = np.array(
                    range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))
                                
        #Calculate norm of density and then divide unnormed density to normalize.
        norm = integrate.simps(unnormed_density, calib_age_ref)
        normed_density = unnormed_density / norm
        #Calculate mean which is the "best" true age of the sample.

        #this could be done vectorized instead of with a loop.
        weighted_density = np.zeros(len(calib_age_ref))
        for index, year in enumerate(calib_age_ref):
            weighted_density[index] = year * normed_density[index]
        mean = integrate.simps(weighted_density, calib_age_ref)

        #The HDR is used to determine the error for the mean calculated above.
        calib_age_error = self.hdr(normed_density, calib_age_ref, interval)
        distr = Distribution(self.calib_age_ref, normed_density, 
                             mean, calib_age_error)
    
        cal_age = cscience.components.UncertainQuantity(data=mean, units='years', 
                                                        uncertainty=distr)
        return cal_age
    
    #calcuate highest density region
    def hdr(self, density, years, interval):
        #Need to approximate integration by summation so need all years in range

        yearly_pdensity = np.array([years, density])
        yearly_pdensity = np.fliplr(yearly_pdensity[:,yearly_pdensity[1,:].argsort()])
        
        summation_array = np.cumsum(yearly_pdensity[1,:])
        
        index_of_win = np.searchsorted(summation_array, interval)
        good_years = yearly_pdensity[0,:index_of_win]
        return (min(good_years), max(good_years))
    

        

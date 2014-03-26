"""
All modules need a run_component function
"""
import cscience
import cscience.components
from cscience.components import UncertainQuantity

import bisect
import operator
import math
import heapq
import collections

import numpy as np
from scipy import stats, interpolate, integrate
import calvin.argue
from calvin.reasoning import engine, conclusions


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
    outputs = {'Corrected 14C Age': ('float', 'years'), 
               'Reservoir Correction':('float', 'years')}

    def run_component(self, core):
        engine.build_argument(conclusions.get('correction magnitude', core))
        adjustment = calvin.argue.find_value('reservoir adjustment', core)
        adj = UncertainQuantity(adjustment['Adjustment'], 'years',
                                adjustment['+/- Adjustment Error'])
      
        for sample in core:
            sample['Reservoir Correction'] = adj
            sample['Corrected 14C Age'] = sample['14C Age'] + (-adj)
            

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (CALIB Style)'
    inputs = {'required':('14C Age',), 'optional':('Corrected 14C Age',)}
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
        interval = 0.687
        for sample in samples:
            try:
                age = sample['Corrected 14C Age'] or sample['14C Age']
                sample['Calibrated 14C Age'] = self.convert_age(age, interval)
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
                 
    def convert_age(self, age, interval):
        """
        returns a "base" calibrated age interval 
        """
        avg = age.magnitude
        error = age.uncertainty.magnitude[0].magnitude

        #Assume that Carbon 14 ages are normally distributed with mean being
        #Carbon 14 age provided by lab and standard deviation from intCal CSV.
        #This probability density is mapped to calibrated (true) ages and is 
        #no longer normally (Gaussian) distributed or normalized.
        unnormed_density = np.zeros(len(self.sortedCalibratedAges))
        for index, year in enumerate(self.sortedCalibratedAges):
            unnormed_density[index] = self.density(avg, error, year, self.interpolatedCalibratedAgesToSigmas(year))
        #unnormed_density is mostly zeros so need to remove but need to know years removed.
        nz_ages = []
        nz_density = []
        for calage, dens in zip(self.sortedCalibratedAges, unnormed_density):
            if dens:
                #TODO: should this be done in some more efficient way? probably
                nz_ages.append(calage)
                nz_density.append(dens)
        sortedCalibratedAges = np.array(nz_ages)
        unnormed_density = np.array(nz_density)
        #Calculate norm of density and then divide unnormed density to normalize.
        norm = integrate.simps(unnormed_density, sortedCalibratedAges)
        normed_density = unnormed_density / norm
        #Calculate mean which is the "best" true age of the sample.
        weightedDensity = np.zeros(len(sortedCalibratedAges))
        for index, year in enumerate(sortedCalibratedAges):
            weightedDensity[index] = year * normed_density[index]
        mean = round(integrate.simps(weightedDensity, sortedCalibratedAges), 1)
        #Interpolate norm density for use in calculating the highest density region (HDR)
        #The HDR is used to determine the error for the mean calculated above.
        interpolatedNormedDensity = interpolate.interp1d(sortedCalibratedAges, 
                                                         normed_density, 'slinear')
        calibratedAgeError = self.hdr(interpolatedNormedDensity, 
                                      round(sortedCalibratedAges[0], 1), 
                                      round(sortedCalibratedAges[-1], 1), interval)
        distr = Distribution(self.sortedCalibratedAges, normed_density, 
                             mean, calibratedAgeError)
        cal_age = cscience.components.UncertainQuantity(data=mean, units='years', 
                                                        uncertainty=distr)
        return cal_age
    
    #calcuate highest density region
    def hdr(self, density, firstYear, lastYear, interval):
        #Need to approximate integration by summation so need all years in range
        years = range(int(firstYear), int(lastYear+1))
        #Create list of pairs of (year,probability density)
        years_and_probability_density = zip(*sorted(zip(years, 
                                                        [density(x) for x in years]),
                                            key=operator.itemgetter(1),
                                            reverse=True))
        summation_array = np.cumsum(years_and_probability_density[1])
        index_of_awesome = bisect.bisect(summation_array, interval)
        years_we_like = years_and_probability_density[0][:index_of_awesome]
        return (min(years_we_like), max(years_we_like))
        
        

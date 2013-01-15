import itertools

import cscience.components
from cscience.components import datastructures

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


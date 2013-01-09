import itertools

from cscience import components
from cscience.components import datastructures

class SimpleIntCalCalibrator(components.BaseComponent):
    def __call__(self, samples):
        self.curve = datastructures.collection_to_bintree(
                    self.experiment['calibration curve'], '14C Age')
        
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
        minage, maxage, maxerr = 56000, 0, 0
        #TODO: this is a mathematical hack because probability is hard.
        for entry in itertools.chain(data[0].data, data[1].data):
            minage = min(minage, entry['Calibrated Age'])
            maxage = max(maxage, entry['Calibrated Age'])
            maxerr = max(maxerr, entry['Error'])
        diff = (maxage - minage) / 2
        maxerr += diff
        return (minage + diff, maxerr)


components.library['Simple Carbon 14 Calibration (IntCal)'] = SimpleIntCalCalibrator



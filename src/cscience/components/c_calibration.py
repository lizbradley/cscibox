

from cscience import components

class FairbanksCalibrator(components.BaseComponent):
    def __call__(self, samples):
        for sample in samples:
            sample['Calibrated 14C Age'] = sample['uncalibrated 14C age']


components.library['Fairbanks Carbon 14 Calibration'] = FairbanksCalibrator



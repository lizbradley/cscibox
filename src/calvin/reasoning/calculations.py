"""
calculations.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials pro# P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 - integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc),.25)
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            # we are almost close enough
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            # we're sort of far away
            return confidence.applicability.weaklyagainst
        else:
            # we're really far away
            return confidence.Applicability.highlyagainst
    def __eq__(self, value, perc):
        pass
    def __ne__(self, value, perc):
        return Applicability.highlyfor

def synth_gaussian(core, mean, variation):
    return GaussianThreshold(mean, variation)


def past_avg_temp(core):
    return 'cake'
    


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
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

#forces all division to be floating-point
from __future__ import division
import numpy as np
import scipy.integrate as integrate
import confidence
from numpy import NaN, Inf, arange
import warnings
warnings.simplefilter('ignore', np.RankWarning)
# note: we might want sklearn eventually
#from sklearn.preprocessing import normalize

class ListComparison(object):
    def __init__(self,normal_list_matrix):
        self.normal_matrix = normal_list_matrix

    def within(self, currentlist):
        '''
        currentlist should be same length as previous
        output : normal or not
        return applicabilities. How normal is this?
        '''
        # make each row sum to 1
        # could use sklearn package, like this:
        #new_matrix = normalize(normal_matrix, axis=1, norm='l1')
        # or, do it the stupid way:
        rows,columns = np.shape(self.normal_matrix)
        normalizedMatrix = []
        for i in xrange(rows):
            newList = list(self.normal_matrix[i,:])
            newList = [a/sum(newList) for a in newList]
            normalizedMatrix.append(newList)
        new_matrix = np.array(normalizedMatrix)
        currentlist = [a/sum(currentlist) for a in currentlist]
        
        # see if currentlist is within previous ranges at each index
        mins = np.min(new_matrix,0)
        maxes = np.max(new_matrix,0)
        inside_range = 0
        for i in xrange(len(currentlist)):
            if currentlist[i]<=maxes[i] and currentlist[i]>=mins[i]:
                inside_range += 1
        probability = inside_range / len(currentlist)

        if probability >= .9:
            return confidence.Applicability.highlyfor
        elif probability >= .8:
            return confidence.Applicability.mostlyfor
        elif probability >= .7:
            return confidence.Applicability.partlyfor
        elif probability >= .6:
            return confidence.Applicability.partlyagainst
        elif probability >= .3:
            return confidence.Applicability.mostlyagainst
        else:
            return confidence.Applicability.highlyagainst

class GaussianThreshold(object):
    def __init__(self, mean, variation):
        self.mean = mean
        self.variation = variation
    
    def __lt__(self, value, perc):
        # P will be the probability that the Gaussian variable is less than "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 + integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            # almost close enough
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            # not very close
            return confidence.applicability.weaklyagainst
        else:
            # very far off
            return confidence.Applicability.highlyagainst
    def __le__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 + integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            return confidence.applicability.weaklyagainst
        else:
            return confidence.Applicability.highlyagainst
    def __gt__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 - integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            return confidence.applicability.weaklyagainst
        else:
            return confidence.Applicability.highlyagainst
    def __ge__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
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


def past_avg_temp(core, *args):    
    return None #comment to see arguments overriding each other! 
    return core.properties['average temperature'] - 25

def get_normal_peak_behavior(core, depths):
    '''
    returns a peak comparison object
    warning: doesn't work right if you're too close to the top
    or if the core doesn't have very many samples
    or if the given depthlist is very long relative to the whole core
    '''
    # find peaks 3 times
    # give list of dictionaries? to peak comparison object creator
    # get current peak dict
    depthlist, proxylist = depths

    alldepths = sorted(core.keys())
    length = len(depthlist)
    # get the index of the depth halfway up
    smallestdepth = alldepths[0]
    i = next(x[0] for x in enumerate(alldepths) if x[1] > (smallestdepth + depthlist[0])/2)
    
    depthlist1 = alldepths[i-length:i]
    depthlist2 = alldepths[i:i+length]
    depthlist3 = alldepths[i+length:i+2*length]

    peaklist1 = count_peaks_per_proxy(core,(depthlist1,proxylist))
    peaklist2 = count_peaks_per_proxy(core,(depthlist2,proxylist))
    peaklist3 = count_peaks_per_proxy(core,(depthlist3,proxylist))

    normalpeakmatrix = np.array([peaklist1,peaklist2,peaklist3])
    comparison_object = ListComparison(normalpeakmatrix)
    return comparison_object

def count_peaks(core,depthlist,proxy_name,strictness=10):
    """
    The peak detection algorithm is originally from https://gist.github.com/endolith/250860
    I've modified it a bit ( - Kathleen)
    """
    # I don't know if this is the right way to grab the data
    datalist = [core[depth][proxy_name] for depth in depthlist]

    # detrend the dataseries with low-degree polynomial
    degree = np.min([7,np.round(len(datalist)/10)])
    #print depthlist
    #print datalist
    p = np.polyfit(depthlist,datalist,degree)
    p_evaluated = np.polyval(p,depthlist)
    datalist -= p_evaluated
    datarange = np.max(datalist)-np.min(datalist)
    delta = datarange/strictness

    numPeaks = 0
    mn, mx = Inf, -Inf
    lookformax = True

    for i in arange(len(datalist)):
        this = datalist[i]
        if this > mx:
            mx = this
        if this < mn:
            mn = this

        if lookformax:
            if this < mx-delta:
                numPeaks += 1
                mn = this
                lookformax = False
        else:
            if this > mn+delta:
                mx = this
                lookformax = True

    return numPeaks

def count_peaks_per_proxy(core, depths):
    # call count_peaks for each proxy
    depthlist, proxylist = depths
    peaklist = [count_peaks(core,depthlist,proxy_name) for proxy_name in proxylist]
    return peaklist

def number_of_peaks_is_normal(core, depths):
    '''
    go back to half the depth
    look at 3 other depth intervals, each proxy series in those depth intervals
    see if your current interval has 'not enough bumps' in each data series, in comparison to 'normal'
    if current number of bumps per series is not normal, return evidence AGAINST
    if it IS normal,  return evidence FOR
    '''
    depthlist, proxylist = depths
    currentpeaklist = count_peaks_per_proxy(core,depths)
    NormalPeakComparer = get_normal_peak_behavior(core,depths)
    result = NormalPeakComparer.within(currentpeaklist)
    return result

def known_depth_proxies(core,depth_interval):
    #print 'hey'
    #print core.keys()
    #print '\n'
    depthlist = sorted(core.keys())
    #print depthlist
    #print depthlist
    #print min(depthlist)
    #print max(depthlist)
    #print depth_interval[0], depth_interval[1]
    depthlist = [a for a in depthlist if a >= depth_interval[0] and a <= depth_interval[1]]
    #print 'depthlist is now ', depthlist
    proxylist = sorted(core[depthlist[0]].keys())
    proxylist = ["nh4","hno3","BCconc30","BCgeom30","Mg","nssS","nssS_Na","Cl","nssCa","Mn","Na","Sr","I","LightREE"]
    return depthlist,proxylist
    
#TODO: make a useful auto-currier thing
def min(core, *args):
    return np.min(*args)
def max(core, *args):
    return np.max(*args)

def graphlist(core, var1, var2):
    points = [(float(sample[var1]), float(sample[var2])) for sample in core if 
               sample[var1] is not None and sample[var2] is not None]
    points.sort()
    
    return map(np.array, zip(*points))
    
def find_angles(core, var1, var2):
    """
    Calculates the "bends"/angles of variables graphed against each other
    (e.g. depth v age to look for sharp elbows)
    """
    x, y = graphlist(core, var1, var2)
    x1 = np.ediff1d(x)
    y1 = np.ediff1d(y)
    a = x1[:-1] ** 2 + y1[:-1] ** 2
    b = x1[1:] ** 2 + y1[1:] ** 2
    c = (x[2:] - x[:-2]) ** 2 + (y[2:] - y[:-2]) ** 2
    return np.degrees(np.arccos((a + b - c) / np.sqrt(4 * a * b)))

def normalize_angles(core, angles):
    return np.abs(angles - 180)

def slope(core, var1, var2):
    x, y = graphlist(core, var1, var2)
    return np.ediff1d(y) / np.ediff1d(x)

def is_ocean(core, latitude, longitude):
    #doing the import here for now so not having pillow doesn't crash anyone :P
    #(this is the easiest way to make that so)
    from PIL import Image
    img = Image.open('../resources/ocean.png')
    x = (longitude + 180) / 360 * 6000
    y = (latitude + 90) / 180 * 3000
    return bool(img.getpixel((x, 3000-y))) # 255 = ocean, 0 = land

def mean_squared_error(core, targetvar, predictionvar):
    targets, predictions = graphlist(core, targetvar, predictionvar)
    return np.sqrt(np.mean((predictions-targets)**2))








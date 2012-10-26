"""
simulations.py

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

Simulations live here. A simulation should always be defined as a function that returns a single
SimResult object.
"""

import confidence
import samples
import engine
import conclusions
import calculations
import observations

import math
import scipy
from scipy import stats

from ACE.GUI.Util.Graphing import Plot
from ACE.Framework import Nuclide

#TODO: fiddle with these so they suck fewer balls

class SimResult:
    """
    Represents the result of the simulation. Eventually this will contain not only confidence
    and some sort of value stuff, but also things like how to display the simulation on the pretty
    user interface
    """
    
    def __init__(self, conf, simName, shortDesc, guiDesc):
        self.confidence = conf
        self.simName = simName
        self.shortDesc = shortDesc
        self.params = []
        self.guiItem = guiDesc
        
    def getSimName(self):
        return self.simName
        
    def getDisplayString(self):
        return self.shortDesc
    
    def getConfidence(self):
        return self.confidence
    
    def getDisplay(self):
        return self.guiItem

#this is disgusting. Let's see if we can do a bit better.
def __getConfidence(tvals, value, quality):
    """
    Returns a truth value from a range of truth values
    tvals should be a tuple containing the 5 dividing values between each of the truth value
    ranges, from most false to most true dividers
    """
    
    if scipy.isnan(value):
        match = confidence.Applic.cf
    elif value < tvals[0]:
        match = confidence.Applic.cf
    elif value < tvals[1]:
        match = confidence.Applic.ff
    elif value < tvals[2]:
        match = confidence.Applic.df
    elif value < tvals[3]:
        match = confidence.Applic.dt
    elif value < tvals[4]:
        match = confidence.Applic.ft
    else:
        match = confidence.Applic.ct
        
    return confidence.Confidence(match, quality)
    
def __getQuality(sig):
    """
    Converts a measure of statistical significance into a measure of simulation
    quality. Significance is assumed to be from 0-1, with larger values indicating
    less significance.
    
    ranges (for now) are:
    absolute 0-.01
    good .01-.05
    okay .05-.1
    poor .1+
    """
    
    if scipy.isnan(sig):
        return confidence.Validity.plaus
    elif sig > .1:
        return confidence.Validity.plaus
    elif sig > .05:
        return confidence.Validity.prob
    elif sig > .01:
        return confidence.Validity.sound
    else:
        return confidence.Validity.accept
    
def __getAge():
    return samples.initEnv['age']

def __getPlot(x, y):
    return Plot([sample.aceSam for sample in samples.sampleList], x, y)
    

def correlated(fldA, fldB, dir):
    """
    What this needs to do is identify whether there is some trend between fldA and fldB in the
    appropriate direction. If dir is positive, this is a direct correlation; if it is negative,
    it is an inverse correlation.
    """

    correlation = stats.pearsonr(samples.getAllFlds(fldA), samples.getAllFlds(fldB))
    
    conf = __getConfidence((-.1, .2, .5, .7, .85), correlation[0] * dir,
                           __getQuality(correlation[1] / 2))
    
    plot = __getPlot(fldA, fldB)
    
    return SimResult(conf, (dir > 0 and "positive" or "negative") + 
                     " correlation between " + fldA + " and " + fldB,
                     (abs(correlation[0]) < .5 and 'minimal' or
                      (correlation[0] > 0 and "positive" or "negative")) + 
                     " correlation between " + fldA + " and " + fldB + 
                     '; significance: ' + str(correlation[1]), plot)
    #significance should really go in the plot somewhere; this is a hack for right now

def isLinearGrowth(fld, minRange):
    """
    This function looks at how linearly fld grows. The closer it can come to a straight line that
    goes through all the values of fld (assuming even growth along the other axis), the higher th
    confidence.
    """
    
    samples.sampleList.sort(key=lambda x: samples.extractField(x, fld))
    plot = __getPlot('id', fld)
    
    if (samples.sampleList[-1][fld] - samples.sampleList[0][fld]) < minRange:
        return SimResult(confidence.Confidence(confidence.Applic.cf, confidence.Validity.sound), 
                         "even distribution of sample property '" + fld + "'",
                         'insufficient distribution of samples', plot)
    
    fldList = samples.getAllFlds(fld)
    if len(fldList) < 3:
        #can't check for *even* distribution, but they are not right next to each other
        #if we got here at all, I think.
        if len(fldList) == 2:
            app = -observations.neareq(fldList[0], fldList[1])
            return SimResult(confidence.Confidence(app, confidence.Validity.plaus), 
                         "even distribution of sample property '" + fld + "'",
                         '2 samples ' + (app.isTrue() and '' or 'not ') + 'about equal', plot)
        else:
            return SimResult(confidence.Confidence(confidence.Applic.df, confidence.Validity.prob), 
                         "even distribution of sample property '" + fld + "'",
                         'fewer than 2 samples', '')
    #fldList.sort()
    
    line = stats.linregress(range(len(fldList)), fldList)
    
    #line[0] is slope
    #line[1] is intercept
    
    qual = __getQuality(line[3])
    if len(fldList) < 5:
        qual -= 1
    
    conf = __getConfidence((.8, .85, .9, .95, .99), line[2], qual)
    
    plot.plotLine(line[0], line[1])
    
    """
    visDesc = "Graph of " + fld + " spaced out evenly, plus the best fit line"
    visDesc += "\npoints are:\n"
    visDesc += "\n".join([str(tup) for tup in zip(range(len(fldList)), fldList)])
    visDesc += "\nLine is slope " + str(line[0]) + " intercept " + str(line[1]) 
    """
    """
    visDesc += '\nfits ' + fld + ' within ' + str(line[2])
    visDesc += '.\nStatistical significance: ' + str(line[3])
    """
    
    return SimResult(conf, "even distribution of sample property '" + fld + "'",
                     "'" + fld + "' is " + (line[2] < .9 and 'not ' or '') +
                     "evenly distributed among all samples", plot)
    


#calcium potassium chlorine
#%of cl36 from different targets: trend with age
#PCA PK Pn
#sounds like different chemistry might be a conclusion of its own?
#big difference for at least some elements
#look at range in real world; may be different for different minerals
#Cl all over the place
#vs pot and cal are usually within 50% of mean 
#SiO 20%


def differentChemistry(sample):
    """
    Checks whether this sample has noticeably different chemical composition from all the other
    samples.
    """
    
    chemAtts = ['Al2O3', 'B', 'CO2', 'CaO', 'Cl', 'Fe2O3', 'Gd', 'K2O', 'MgO', 
                'MnO', 'Na2O', 'P2O5', 'SiO2', 'Sm', 'Th', 'TiO2', 'U']
    
    plot = None
    differs = []
    anyRun = False
    conf = confidence.Confidence(confidence.Applic.cf, confidence.Validity.plaus)
    for att in chemAtts:
        try:
            result = skewsField(sample, att)
            anyRun = True
            if result.confidence.isTrue():
                differs.append(att)
                
            #this comparison may or may not actually work, here
            if conf < result.confidence or plot is None:
                #mild hack for cases where chemistries are all the same
                plot = result.guiItem
                conf = result.confidence
        except KeyError:
            #we don't have this chemistry item; ignore and continue.
            pass
    
    if not anyRun:
        #so for this case, we had no chemical data at all...
        #this should really never happen in real life, mind.
        raise KeyError()
    
    if len(differs) > 0:
        shortDesc = str(sample) + ' has different chemical properties: ' + ', '.join(differs)
    else:
        shortDesc = str(sample) + ' has the same chemical composition as other samples in the set'
        
    return SimResult(conf, str(sample) + " has a different chemical composition",
                     shortDesc, plot)

def argueWithoutSample(sample, conclusion):
    """
    Builds an argument for conclusion (assumed to be passed in as a string, NOT a full conclusion
    (so no parameters can be attached to the conclusion, currently...), but this may change), after 
    removing the given sample from the dataset.
    """
    
    #first let's check that we need to remove samples
    arg = engine.buildArgument(conclusions.Conclusion(conclusion))
    name = "can argue for '" + conclusion + "' without sample " + str(sample)
    
    if arg.getSingleConfidence().isStrongly(True):
        return SimResult(-arg.getSingleConfidence(), name,
                         "good argument for '" + conclusion + "' before removing any samples",
                         arg)
    
    savedSamples = samples.sampleList[:]
    samples.sampleList.remove(sample)
    
    arg = engine.buildArgument(conclusions.Conclusion(conclusion))
    samples.sampleList = savedSamples
    
    return SimResult(arg.getSingleConfidence(), name,
                     (arg.getSingleConfidence().isTrue() and 'valid' or 'invalid') + 
                     " argument for " + conclusion + " without " + str(sample), arg)

def skewsField(sample, field):
    """
    Checks whether the value of field in the passed in sample is significantly different from the
    value of field for the rest of the samples under consideration.
    """
    
    savedSamples = samples.sampleList[:]
    samples.sampleList.remove(sample)
    
    try:
        flds = samples.getAllFlds(field)
        
        mean = stats.mean(flds)
        stddev = stats.std(flds)
        val = sample[field]
        
        if stddev == 0:
            devs = 0
        else:
            devs = abs(val - mean) / stddev
    
    finally:
        #we should be fixing the sample list even when I crash!
        samples.sampleList = savedSamples
    
    if len(samples.sampleList) < 3:
        qual = confidence.Validity.plaus
    elif len(samples.sampleList) < 6:
        qual = confidence.Validity.prob
    else:
        qual = confidence.Validity.sound
        
    conf = __getConfidence((.5, 1, 2, 3, 5), devs, qual)
    
    samples.sampleList.sort(key=lambda x: samples.extractField(x, field))
    
    plot = __getPlot('id', field)
    plot.plotLine(0, mean)
    plot.plotLine(0, mean-stddev)
    plot.plotLine(0, mean+stddev)
    plot.plotLine(0, sample[field])
    
    return SimResult(conf, str(sample) + " has a different " + field + " from other samples",
                     str(sample) + "'s value for " + field + ' is ' + str(devs) + 
                     ' standard deviations from the mean', plot)
    
def distantFromOthers(sample, field, spread):
    """
    Discover how different (based on spread) this sample is from the sample nearest to it
    """
    
    value = sample[field]
    spr = sample[spread]
    
    minDist = 50
    
    samples.sampleList.sort(key=lambda x: samples.extractField(x, field))
    plot = __getPlot('id', field)
    
    if any([sam[field] > sample[field] for sam in samples.sampleList]) and \
       any([sam[field] < sample[field] for sam in samples.sampleList]):
        return SimResult(confidence.Confidence(confidence.Applic.cf, confidence.Validity.sound), 
                         str(sample) + " has a different " + field + " from any other sample",
                         str(sample) + "'s value for " + field + ' is between that of other samples', 
                         plot)
    
    for sam in samples.sampleList:
        if sam == sample:
            continue
        
        distance = abs(sample[field] - sam[field])
        spr = sample[spread] + sam[spread]
        
        if spr == 0:
            continue
        
        minDist = min(minDist, distance / float(spr))
        
    if len(samples.sampleList) < 3:
        qual = confidence.Validity.plaus
    elif len(samples.sampleList) < 6:
        qual = confidence.Validity.prob
    else:
        qual = confidence.Validity.sound
        
    minDist *= 2
    conf = __getConfidence((1, 2, 3, 4, 6), minDist, qual)
    
    plot.plotLine(0, sample[field])
    plot.plotLine(0, sample[field]-sample[spread])
    plot.plotLine(0, sample[field]+sample[spread])
    
    return SimResult(conf, str(sample) + " has a different " + field + " from any other sample",
                     str(sample) + "'s value for " + field + ' is ' + str(minDist) + 
                     ' times ' + spread + ' from any other sample', plot)
        
    
def longTail(direction):
    """
    Examine the shape of this set of samples to see if it matches a gaussian with a long tail
    to one direction, indicated by the parameter. +1 is a long, older tail and -1 is a long,
    younger tail
    """
    
    name = "long tail of " + (direction > 0 and 'older' or 'younger') + ' samples'
    
    if len(samples.sampleList) < 8:
        return SimResult(confidence.Confidence(confidence.Applic.df, confidence.Validity.plaus),
                     name, 'not enough samples to check for tail', 'minimum of 8 samples needed')
    
    res = stats.skewtest([sample[__getAge()] for sample in samples.sampleList])
    qual = __getQuality(res[1]/2)
    conf = __getConfidence((-1.5, -1, 0, 1, 1.5), res[0], qual)
    
    plot = __getPlot('id', __getAge())
    
    if direction < 0:
        conf = -conf
    
    return SimResult(conf, name, (qual < confidence.Validity.sound and 'weak' or 'strong') +
                     ' evidence of a' + (res[0] < 0 and ' younger' or 'n older') + ' tail found',
                     plot) #should be a plot of my samples and a gaussian

def quantizedInheritance():
    """
    Checks whether we can remove only a small percentage of samples from the oldest end of the 
    sample set and, in so doing, get a successful "no process" argument.
    """
    
    #first let's check that we need to remove samples
    arg = engine.buildArgument(conclusions.Conclusion("no process"))
    name = "removal of groups of older samples allows argument for 'no process'"
    
    if arg.getSingleConfidence().isProbably(True):
        return SimResult(-arg.getSingleConfidence(), name,
                         "good argument for 'no process' before removing any samples",
                         arg)
    
    savedSamples = samples.sampleList[:]
    
    samples.sampleList.sort(cmp = lambda x, y: cmp(x[__getAge()], y[__getAge()]))
    
    while len(samples.sampleList) > 0:
        curMax = samples.sampleList[-1][__getAge()] - \
                   samples.sampleList[-1][__getAge() + ' uncertainty']
        #delete in chunks, not one at a time
        samples.sampleList = [sample for sample in samples.sampleList if sample[__getAge()] < curMax]
        
        arg = engine.buildArgument(conclusions.Conclusion("no process"))
        if arg.getSingleConfidence().isProbably(True):
            break
    
    reduction = len(samples.sampleList) / float(len(savedSamples))
    #removed = len(savedSamples) - len(samples.sampleList)
    
    samples.sampleList = savedSamples
    
    conf = __getConfidence((.1, .2, .4, .65, .80), reduction, confidence.Validity.accept)
    
    #oldest n samples appear to be outliers
    
    return SimResult(conf, name, "removed " + str(100 - (reduction * 100)) + 
                     "% of samples before finding a good argument for 'no process'", arg)
    
def centralAgreement(sample):
    """
    Checks whether we can remove samples at the edges to get a reasonably large group with
    a single central tendency.
    
    Should pay attention to whether removed samples have similar ages to each other or not
    
    Also, this should be run once and the results saved, instead of being run again for every
    single sample...
    """
    #first let's check that we need to remove samples

        
    arg = engine.buildArgument(conclusions.Conclusion("no process"))
    name = "removal of youngest and oldest samples allows argument for 'no process'"
    
    if arg.getSingleConfidence().isStrongly(True):
        return SimResult(-arg.getSingleConfidence(), name,
                         "good argument for 'no process' before removing any samples",
                         arg)
    
    savedSamples = samples.sampleList[:]
    
    samples.sampleList.sort(cmp = lambda x, y: cmp(x[__getAge()], y[__getAge()]))
    
    while len(samples.sampleList) > 0:
        mean = calculations.calcMean(__getAge())
        younger = mean - samples.sampleList[0][__getAge()]
        older = samples.sampleList[-1][__getAge()] - mean
        if younger > older:
            del samples.sampleList[0]
        else:
            del samples.sampleList[-1]
        arg = engine.buildArgument(conclusions.Conclusion("no process"))
        if arg.getSingleConfidence().isStrongly(True):
            break
        
    if sample in samples.sampleList:
        res = SimResult(confidence.Confidence(confidence.Applic.cf, confidence.Validity.sound), name,
                        str(sample) + " does not need to be removed to have good argument for 'no process'",
                        arg)
        samples.sampleList = savedSamples
        return res
    
    reduction = len(samples.sampleList) / float(len(savedSamples))
    #removed = len(savedSamples) - len(samples.sampleList)
    
    samples.sampleList = savedSamples
    
    conf = __getConfidence((.2, .35, .6, .8, .9), reduction, confidence.Validity.prob)
    
    #print reduction, conf
    
    #oldest n samples appear to be outliers
    
    return SimResult(conf, name, "removed " + str(100 - (reduction * 100)) + 
                     "% of samples before finding a good argument for 'no process'", arg)
    
def checkOverlap(anchor, spread):
    """
    Checks that every sample overlaps with every other sample at at least one point 
    in anchor/spread (or spread * 2)
    """
    
    if len(samples.sampleList) == 0:
         return SimResult(confidence.Confidence(confidence.Applic.cf, confidence.Validity.sound), 
                          'sample ' + anchor + ' plus or minus ' + spread + ' overlaps for all samples', 
                          'No samples in set', "")

    samples.sampleList.sort(key=lambda x: samples.extractField(x, anchor))
    plot = __getPlot('id', anchor)
    
    range = [0, samples.sampleList[0][anchor] + samples.sampleList[0][spread]]
    range2 = [0, samples.sampleList[0][anchor] + 2 * samples.sampleList[0][spread]]
    
    for sample in samples.sampleList:
        sAnch = sample[anchor]
        sSpre = sample[spread]
        
        range[0] = max(range[0], sAnch-sSpre)
        range[1] = min(range[1], sAnch+sSpre)
        range2[0] = max(range2[0], sAnch-2*sSpre)
        range2[1] = min(range2[1], sAnch+2*sSpre)
        
    if range[1] > range[0]:
        dif = abs(range[1] - range[0]) / float(range[0] + range[1])
        qual = dif >= .05 and confidence.Validity.accept or confidence.Validity.sound
        desc = 'Samples overlap within 1 sigma'
        plot.plotLine(0, range[0])
        plot.plotLine(0, range[1])
        conf = True
    elif range2[1] > range2[0]:
        dif = abs(range2[1] - range2[0]) / float(range2[0] + range2[1])
        qual = dif >= .5 and confidence.Validity.sound or confidence.Validity.prob
        desc = 'Samples overlap within 2 sigma'
        plot.plotLine(0, range2[0])
        plot.plotLine(0, range2[1])
        conf = True
    else:
        dif = abs(range2[1] - range2[0]) / float(range2[0] + range2[1])
        desc = 'Samples do not overlap within 2 sigma'
        #plot.plotLine(0, range2[0])
        #plot.plotLine(0, range2[1])
        
        if dif > .2:
            qual = confidence.Validity.accept
        elif dif > .1:
            qual = confidence.Validity.sound
        elif dif > .02:
            qual = confidence.Validity.prob
        else:
            qual = confidence.Validity.plaus
        conf = False
        
    confid = confidence.Confidence(confidence.Applic.ft, qual)
    if not conf:
        confid = -confid
    
    return SimResult(confid, 'sample ' + anchor + ' plus or minus ' 
                     + spread + ' overlaps for all samples', desc, plot)
    
def chiSquaredTest(field):
    """
    Gets the chi-squared value for field to test if it is normally distributed.
    """
    name = "chi squared of  '" + field + "' < 2"
    
    if len(samples.sampleList) < 20:
        return SimResult(confidence.Confidence(confidence.Applic.df, confidence.Validity.plaus),
                     name, 'not enough samples to check for tail', 'minimum of 20 samples needed')
        
    
    res = stats.normaltest([sample[field] for sample in samples.sampleList])
    qual = __getQuality(res[1]/2)
    conf = -(__getConfidence((1, 1.5, 2, 3, 5), res[0], qual))
    
    #should probably plot this with a gaussian overlay
    plot = __getPlot('id', field)
    
    return SimResult(conf, name, 'chi squared value is ' + str(res[0]), plot)

def highConfidence(field):
    """
    Returns the user-reported level of confidence in field, if any
    note that the field needs to have been entered for this to actually fire.
    """
    samples.getLandformField(field)
    if field in samples.confidenceEntry:
        val = samples.confidenceEntry[field]
    else:
        val = confidence.Validity.accept
    conf = confidence.Confidence(confidence.Applic.ct, val)
    
    return SimResult(conf, 'high confidence in ' + field, 'your confidence was ' + str(val), '')

def inheritancePossible():
    """
    Checks whether it is possible for the oldest sample to in fact be the product of
    inheritance (based on saturation constraints), both from the youngest sample and
    from the mean.
    """
    
    name = 'amount of inheritance required to explain spread is possible'
    oldest = calculations.calcMaxSample(__getAge())
    
    if Nuclide.stable(oldest['nuclide']):
        return SimResult(confidence.Confidence(confidence.Applic.ct, confidence.Validity.accept),
                         name, 'nuclide is stable', 'nuclide is ' + str(oldest['nuclide']))
    
    saturation = 3.0 / Nuclide.decay[oldest['nuclide']] 

    spread = oldest[__getAge()] - calculations.calcMin(__getAge())
    if spread < saturation:
        return SimResult(confidence.Confidence(confidence.Applic.ct, confidence.Validity.sound),
                         name, 'total spread of ' + str(spread) + 
                         ' is less than saturation age of about ' + str(saturation), 
                         'saturation: ' + str(saturation) + ', spread: ' + str(spread))
    
    spread = oldest[__getAge()] - calculations.calcMean(__getAge())
    if spread < saturation:
        return SimResult(confidence.Confidence(confidence.Applic.dt, confidence.Validity.sound),
                         name, 'total amount > mean age of ' + str(spread) + 
                         ' is less than saturation age of about ' + str(saturation), 
                         'saturation: ' + str(saturation) + ', spread: ' + str(spread))
        
    return SimResult(confidence.Confidence(confidence.Applic.cf, confidence.Validity.sound),
                     name, 'spread in ages is impossible via inheritance', 
                     'saturation (about): ' + str(saturation) + ', spread: ' + str(spread))
    
    
    
    





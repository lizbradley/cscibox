#import rpy2
#import rpy2.rinterface
#import rpy2.robjects

import cscience
import cscience.components
from cscience.components import UncertainQuantity

import numpy
import tempfile
import operator

try:
    import cfiles.baconc
except ImportError:
    print 'No BACON plugin available'
else:
    class BaconInterpolation(cscience.components.BaseComponent):
        visible_name = 'Interpolate Using BACON'
        inputs = {'required':('Calibrated 14C Age',)}
            
        def run_component(self, core):
            #create a temporary file for BACON to write its output to, so as
            #to read it back in later.
            #for the curious, this is not in prepare() because we want a new
            #file for every run of BACON, not every instance of this component.
            self.tempfile = tempfile.NamedTemporaryFile(delete=False)
            #close the file so that BACON can open it (thus the delete=False)
            self.tempfile.close()
            
            data = self.build_data_array(core)
            memorya, memoryb = self.find_mem_params(core)
            hiatusi = self.build_hiatus_array(core, data)
            
            mindepth = data[0][3]
            maxdepth = data[-1][3]
            minage = data[0][1] - (10 * data[0][2])
            maxage = data[-1][1] + (10 * data[-1][2])
            
            guesses = numpy.round(numpy.random.normal(data[0][1], data[0][2], 2))
            guesses.sort()
            core['all']['BACON guess 1'] = guesses[0]
            core['all']['BACON guess 2'] = guesses[1]
            
            #section thickness is the expected granularity of change within the
            #core. currently, we are using the default BACON parameter of 5 (cm);
            #note that we can use a v large thickness to do a ballpark fast,
            #and that BACON suggests limiting # of sections/core to between 10
            #and 200.
            
            #manual suggests for "larger" (>~2-3 m) cores, a good approach is
            #to start thick very high (say, 50) and lower it until a "smooth
            #enough" model is found.
            thick = 5
            sections = (maxdepth - mindepth) / thick
            if sections < 10:
                thick = min(self.prettynum((sections / 10.0) * thick))
            elif sections > 200:
                thick = max(self.prettynum((sections / 200.0) * thick))
            core['all'].setdefault('BACON segment thickness', thick)
            sections = (maxdepth - mindepth) / thick
            
            #the size given is the # of (I think) accepted iterations that we
            #want in our final output file. BACON defaults this to 2000, so that's
            #what I'm using for now. Note the ability to tweak this value to
            #do quick-and-dirty vs. "good" models
            
            baconc.run_simulation(len(data), [baconc.PreCalDet(*sample) for sample in data], 
                                  sections, memorya, memoryb, minage, maxage,
                                  guesses[0], guesses[1], mindepth, maxdepth, 
                                  self.tempfile.name, 2000)
            #I should do something here to clip the undesired burn-in off the
            #front of the file (default ~200)
            
            #for now, use scipy.optimize.curve_fit to create a curve to save
            #for this data, instead of alllllll the data.
            
            #output file as I understand it:
            #something with hiatuses I need to work out.
            #some number of rows of n columns. the last column is (?)
            #the 2nd to last column is possibly a likelihood, or maybe a memory
            #notation of some kind. (if a likelihood, smaller values should be
            #more likely...)
            #the 1st column appears to be the "correct" age of the youngest
            #point in the core
            #following columns up to the likelihood/memory col are the
            #accepted *accumulation rate per cm* for that segment of the core.
            
        def build_data_array(self, core):
            """
            Extracts BACON-friendly data from our core samples.
            """
            data = []
            #values for t dist; user can add for core or by sample,
            # or we default to 3 & 4
            #TODO: add error checking and/or AI setting on these
            core['all'].setdefault('t.a', 3)
            core['all'].setdefault('t.b', 4)
            for sample in core:
                id = str(sample['id'])
                depth = float(sample['depth'].magnitude)
                ta = sample['t.a']
                tb = sample['t.b']
                
                unitage = sample['Calibrated 14C Age']
                age = float(unitage.rescale('years').magnitude)
                #rescaling is currently not set up to work with uncerts. No idea
                #what subtle bugs that might be causing. sigh.
                uncert = float(unitage.uncertainty.as_single_mag())
                ucurvex = getattr(unitage.uncertainty.distribution, 'x', [])
                ucurvey = getattr(unitage.uncertainty.distribution, 'y', [])
                    
                data.append([id, age, uncert, depth, ta, tb, ucurvex, ucurvey])
            
            data.sort(key=operator.itemgetter(3)) #sort by depth
            return data
            
        def build_hiatus_array(self, core, data):
            """
            Builds an array describing the hiatusi and associated expected
            accumulation rates we'd like BACON to consider.
            Currently a specifying no hiatus; more might want to
            be added via AI *or* user input...
            """
            # accumulation rate is passed per-hiatus, with a dummy hiatus at 
            # the end of the array to pass the youngest such rate.
            # We include one dummy hiatus at this time to pass the single
            # accumulation rate for a core with no hiatus.
            
            # accumulation shape is the degree to which accumulation rates cluster
            # at the left (smaller) end of possible values; accumulation mean
            # is the expected mean accumulation rate. Higher shape parameters
            # will more strongly peak the distribution; means are suggested as
            # round values.
            
            # hiatus info is given as:
            # expected depth
            # accum. rate alpha (= accum shape)
            # accum. rate beta (= accum shape/ accum mean)
            # ha (= hiatus shape parameter)
            # hb (= hiatus shape / hiatus mean)
            
            # hiatuses are expected to be passed in *descending* order by depth,
            # with a dummy hiatus last to give the last acc rate (think fencepost)
            
            # hiatus shape default = 1; <1 is not advised as it will force
            # hiatuses to never have 0 yr gaps (per manual)
            # (changing shape parameter is usually not advised)
            # hiatus mean is the mean expected # of years for the given hiatus
            
            # find an expected acc. rate
            avgrate = (data[-1][3] - data[0][3]) / (data[-1][1] - data[0][1])
            core['all'].setdefault('accumulation rate mean', self.prettynum(avgrate)[0])
            core['all'].setdefault('accumulation rate shape', 1.5)
            
            accmean = core['all']['accumulation rate mean']
            accshape = core['all']['accumulation rate shape']
            
            #depth and hiatus shape are ignored for the top segment
            top_hiatus = [-10, accshape, accshape/accmean, 0, 0]
            
            #make sure the array is the right dimensions.
            return numpy.array([zip(top_hiatus)])
        
        def find_mem_params(self, core):
            #memorya and memoryb are calculated from "mean" and "strength" params as:
            #a = strength*mean
            #b = strength*(1-mean)
            #BACON uses defaults of 4 for strength and .7 for mean; it does not
            #appear to suggest other values for these variables.
            #Per the BACON manual, we increase either value to assume
            #more-constant accumulation rates. Increasing the mean will move the
            #acceptable rate change distribution to the right (correlation between
            #accumulation rates is higher); increasing the strength will give
            #the distribution a higher peak (the correlation rate is more
            #consistent with itself).
            #for now, we use the defaults; in future, we should AI-ify things!
            core['all'].setdefault('accumulation memory mean', .7)
            core['all'].setdefault('accumulation memory strength', 4)
            
            str = core['all']['accumulation memory strength']
            mean = core['all']['accumulation memory mean']
            
            memorya = str * mean
            memoryb = str * (1-mean)
            
            return (memorya, memoryb)
        
        def prettynum(self, value):
            guessmag = .1
            while value / guessmag > 10:
                guessmag *= 10
            vals = numpy.array([1, 2, 5, 10]) * guessmag
            vals.sort(key=lambda x: abs(x-value))
            return vals
            
            
        
        
          
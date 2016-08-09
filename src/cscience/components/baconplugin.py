#import rpy2
#import rpy2.rinterface
#import rpy2.robjects

import cscience
import cscience.components
from cscience.framework import datastructures

import csv
import warnings
import numpy
import scipy
import scipy.interpolate
import tempfile
import operator
import quantities
import wx.lib.delayedresult as delayedresult

warnings.filterwarnings("always",category=ImportWarning) # remove filter on ImportWarning

# Custom formatting on the warning (http://pymotw.com/2/warnings/)
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s:%s \n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

try:
    import cfiles.baconc
except ImportError as ie:
    print 'No BACON plugin available'
    class BaconInterpolationHack(cscience.components.BaseComponent):
        visible_name = 'Interpolate Using BACON'

        def run_component(self, *args, **kwargs):
            raise ie
else:
    class BaconInterpolation(cscience.components.BaseComponent):
        visible_name = 'Interpolate Using BACON'
        inputs = {'required':('Calibrated 14C Age',)}
        outputs = {'Model Age': ('float', 'years', True)}
        citations = ['Bacon (Blaauw and Christen, 2011)']

        def run_component(self, core, progress_dialog):
            parameters = self.user_inputs(core,
                        [('Number of Iterations', ('integer', None, False), 200),
                         ('Memory Mean', ('float', None, False), 0.7),
                         ('Memory Strength', ('float', None, False), 4),
                         ('t_b', ('integer', None, False), 4)])

            num_iterations = parameters['Number of Iterations']
            mem_mean = parameters['Memory Mean']
            mem_strength = parameters['Memory Strength']
            t_b = parameters['t_b']
            t_a = t_b - 1

            self.set_value(core, 'accumulation memory mean', mem_mean)
            self.set_value(core, 'accumulation memory strength', mem_strength)
            self.set_value(core, 't_a', t_a)
            self.set_value(core, 't_b', t_b)

            progress_dialog.Update(1, "Initializing BACON")
            #TODO: make sure to actually use the right units...
            data = self.build_data_array(core)
            memorya, memoryb = self.find_mem_params(core)
            hiatusi = self.build_hiatus_array(core, data)

            mindepth = data[0][3]
            maxdepth = data[-1][3]
            #minage = data[0][1] - (10 * data[0][2])
            #maxage = data[-1][1] + (10 * data[-1][2])

            guesses = numpy.round(numpy.random.normal(data[0][1], data[0][2], 2))
            guesses.sort()

            self.set_value(core, 'BACON guess 1', guesses[0])
            self.set_value(core, 'BACON guess 2', guesses[1])

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
            self.set_value(core, 'BACON segment thickness', thick)
            sections = int(numpy.ceil((maxdepth - mindepth) / thick))

            #create a temporary file for BACON to write its output to, so as
            #to read it back in later.
            #for the curious, this is not in prepare() because we want a new
            #file for every run of BACON, not every instance of this component.
            #self.tempfile = tempfile.NamedTemporaryFile()
            self.tempfile = open('tempfile', 'w+')
            #the size given is the # of (I think) accepted iterations that we
            #want in our final output file. BACON defaults this to 2000, so that's
            #what I'm using for now. Note the ability to tweak this value to
            #do quick-and-dirty vs. "good" models

            #minage & maxage are meant to indicate limits of calibration curves;
            #just giving really big #s there is okay.
            progress_dialog.Update(2, "Running BACON Simulation")
            cfiles.baconc.run_simulation(len(data), 
                        [cfiles.baconc.PreCalDet(*sample) for sample in data], 
                        hiatusi, sections, memorya, memoryb, 
                        -1000, 1000000, guesses[0], guesses[1], 
                        mindepth, maxdepth, self.tempfile.name, num_iterations)
            progress_dialog.Update(8, "Writing Data")
            #I should do something here to clip the undesired burn-in off the
            #front of the file (default ~200)

            #for now, doing a lazy haxx where I'm just taking the trivial mean
            #of each depth=point age and calling that the "model age" at that
            #depth. Lots of interesting stuff here; plz consult a real statistician

            #read in data output by bacon...
            #print dir(self.tempfile)
            #self.tempfile.open()
            reader = csv.reader(self.tempfile, dialect='excel-tab', skipinitialspace=True)
            truethick = float(maxdepth - mindepth) / sections
            sums = [0] * (sections + 1)
            total_info = []

            depth = [mindepth + (truethick*i) for i in range(sections+1)]

            total_info.append(depth)

            total = 0

            for it in reader:
                if not it:
                    continue
                path_ls = [0] * (sections + 1)
                total += 1
                #as read by csv, the bacon output file has an empty entry as its
                #first column, so we ignore that. 1st real column is a special case,
                #a set value instead of accumulation
                cumage = float(it[1])
                sums[0] += cumage
                #last 2 cols are not acc rates; they are "w" and "U"; currently
                #ignored, but related to it probability
                for ind, acc in enumerate(it[2:-2]):
                    cumage += truethick * float(acc)
                    sums[ind+1] += cumage
                    path_ls[ind+1] += cumage
                total_info.append(path_ls)
            sums = [sum / total for sum in sums]
            self.tempfile.close()

            #test saving bacon info to file
            with open("eggs.csv", "wb") as eggs:
                total_out = csv.writer(eggs)
                for i in total_info:
                    total_out.writerow(i)

            #TODO: are these depths fiddled with at all in the alg? should I make
            #sure to pass "pretty" ones?
            core['all']['age/depth model'] = \
                datastructures.PointlistInterpolation(
                        [mindepth + truethick*ind for ind in range(len(sums))],
                        sums)

            #test saving bacon to database
            core['all']['eggs'] = total_info

            #output file as I understand it:
            #something with hiatuses I need to work out.
            #some number of rows of n columns. the last column is (?)

            #the 1st column appears to be the "correct" age of the youngest
            #point in the core
            #following columns up to the last 2 cols, which I am ignoring, are the
            #accepted *accumulation rate (years per cm)* for that segment of the core.
            progress_dialog.Update(9)

        def build_data_array(self, core):
            """
            Extracts BACON-friendly data from our core samples.
            """
            data = []
            #values for t dist; user can add for core or by sample,
            # or we default to 3 & 4
            #TODO: add error checking and/or AI setting on these
            for sample in core:
                id = str(sample['id'])
                depth = float(sample['depth'].magnitude)
                ta = sample['t_a']
                tb = sample['t_b']
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

            # find an expected acc. rate -- years/cm
            avgrate = (data[-1][1] - data[0][1]) / (data[-1][3] - data[0][3])
            self.set_value(core, 'accumulation rate mean', self.prettynum(avgrate)[0])
            self.set_value(core, 'accumulation rate shape', 1.5)

            accmean = core['all']['accumulation rate mean']
            accshape = core['all']['accumulation rate shape']

            #depth and hiatus shape are ignored for the top segment
            top_hiatus = [-10, accshape, accshape/accmean, 0, 0]

            #make sure the array is the right dimensions.
            return numpy.array(zip(top_hiatus))

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
            
            stren = core['all']['accumulation memory strength']
            mean = core['all']['accumulation memory mean']
            
            memorya = stren * mean
            memoryb = stren * (1-mean)
            
            return (memorya, memoryb)

        def prettynum(self, value):
            guessmag = .1
            while value / guessmag > 10:
                guessmag *= 10
            vals = numpy.array([1, 2, 5, 10]) * guessmag
            #apparently numpy arrays don't have a key in their sort :P
            vals = list(vals)
            vals.sort(key=lambda x: abs(x-value))
            return vals

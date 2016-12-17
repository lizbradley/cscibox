import cscience
import cscience.components
from cscience.components import ComponentAttribute as Att
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
        inputs = [Att('Calibrated 14C Age')]
        user_vars = [Att('Bacon Number of Iterations', type='integer', core_wide=True),
                     Att('Bacon Memory: Mean', core_wide=True),
                     Att('Bacon Memory: Strength', core_wide=True),
                     Att('Bacon t_a', core_wide=True),
                     Att('Bacon Segment Thickness', core_wide=True),
                     Att('Bacon Accumulation Rate: Mean', unit='years/cm', core_wide=True),
                     Att('Bacon Accumulation Rate: Shape', core_wide=True)]
        outputs = [Att('Age/Depth Model', type='age model', core_wide=True), 
                   Att('Bacon Model', type='age model', core_wide=True),
                   Att('Bacon guess 1', unit='years', core_wide=True),
                   Att('Bacon guess 2', unit='years', core_wide=True)]
        
        citations = [datastructures.Publication(authors=[("Blaauw", "Maarten"), ("Christen", "J. Andres")], 
                        title="Flexible paleoclimate age-depth models using an autoregressive gamma process", 
                        journal="Bayesian Analysis", volume="6", issue="3", year="2011",
                        pages="457-474", doi="10.1214/ba/1339616472")]

        def run_component(self, core, progress_dialog):
            '''Run BACON on the given core.

            core: the core data
            progress_dialog: a dialog box. Used to update progress on BACON. 

            This calls the SWIG wrapper to BACON.
            It then updates 
            core['all']['eggs'] = total_info
            and
            core.properties['Age/Depth Model']
            '''
            #build a guess for thickness similar to how Bacon's R code does it
            #section thickness is the expected granularity of change within the
            #core. currently, we are using the default BACON parameter of 5 (cm);
            #note that we can use a v large thickness to do a ballpark fast,
            #and that BACON suggests limiting # of sections/core to between 10
            #and 200.

            #manual suggests for "larger" (>~2-3 m) cores, a good approach is
            #to start thick very high (say, 50) and lower it until a "smooth
            #enough" model is found.
            def scaledepth(key):
                return float(core[key]['depth'].rescale('cm').magnitude)
            thickguess = 5
            mindepth = scaledepth(min(core.keys()))
            maxdepth = scaledepth(max(core.keys()))
            sections = (maxdepth - mindepth) / thickguess
            if sections < 10:
                thickguess = min(self.prettynum((sections / 10.0) * thickguess))
            elif sections > 200:
                thickguess = max(self.prettynum((sections / 200.0) * thickguess))
            
            parameters = self.user_inputs(core,
                        [('Bacon Number of Iterations', ('integer', None, False), 200),
                         ('Bacon Segment Thickness', ('float', 'cm', False), thickguess),
                         ('Bacon Memory: Mean', ('float', None, False), 0.7),
                         ('Bacon Memory: Strength', ('float', None, False), 4),
                         ('Bacon t_a', ('integer', None, False), 4, {'helptip':'t_b = t_a + 1'})])
            

            num_iterations = parameters['Bacon Number of Iterations']
            sections = int(numpy.ceil((maxdepth - mindepth) / parameters['Bacon Segment Thickness'].magnitude))

            progress_dialog.Update(1, "Initializing BACON")
            #TODO: make sure to actually use the right units...
            data = self.build_data_array(core)
            memorya, memoryb = self.find_mem_params(core)
            hiatusi = self.build_hiatus_array(core, data)

            guesses = numpy.round(numpy.random.normal(data[0][1], data[0][2], 2))
            guesses.sort()

            self.set_value(core, 'Bacon guess 1', guesses[0])
            self.set_value(core, 'Bacon guess 2', guesses[1])


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

            core.properties['Bacon Model'] = datastructures.BaconInfo(total_info)

            #TODO: are these depths fiddled with at all in the alg? should I make
            #sure to pass "pretty" ones?
            core.properties['Age/Depth Model'] = \
                datastructures.PointlistInterpolation(
                        [mindepth + truethick*ind for ind in range(len(sums))],
                        sums)

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
                ta = sample['Bacon t_a']
                #if depth in (73.5, 93.5, 118.5, 120.5, 351.5, 383.5):
                #    print 'skipping depth', depth
                #    continue

                unitage = sample['Calibrated 14C Age']
                age = float(unitage.rescale('years').magnitude)
                #rescaling is currently not set up to work with uncerts. No idea
                #what subtle bugs that might be causing. sigh.
                uncert = float(unitage.uncertainty.as_single_mag())
                ucurvex = getattr(unitage.uncertainty.distribution, 'x', [])
                ucurvey = getattr(unitage.uncertainty.distribution, 'y', [])

                data.append([id, age, uncert, depth, ta, ta + 1, ucurvex, ucurvey])

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
            # hb (= hiatus shape / hiatus mean) -- hiatus mean is in *years*, not cm

            # hiatuses are expected to be passed in *descending* order by depth,
            # with a dummy hiatus last to give the last acc rate (think fencepost)

            # hiatus shape default = 1; <1 is not advised as it will force
            # hiatuses to never have 0 yr gaps (per manual)
            # (changing shape parameter is usually not advised)
            # hiatus mean is the mean expected # of years for the given hiatus

            # find an expected acc. rate -- years/cm
            avgrate = (data[-1][1] - data[0][1]) / (data[-1][3] - data[0][3])

            self.set_value(core, 'Bacon Accumulation Rate: Mean', 
                           quantities.Quantity(self.prettynum(avgrate)[0], 'years/cm'))
                #quantities.Quantity(50, 'years/cm'))#self.prettynum(avgrate)[0]
            self.set_value(core, 'Bacon Accumulation Rate: Shape', 1.5)

            accmean = float(core.properties['Bacon Accumulation Rate: Mean'].magnitude)
            accshape = core.properties['Bacon Accumulation Rate: Shape']

            #depth and hiatus shape are ignored for the top segment
            #top_hiatus = [[387, accshape, accshape/accmean, 1, 1./10000.],
            #              [-10, accshape, accshape/accmean, 1, .1]]
            top_hiatus = [[-10, accshape, accshape/accmean, 1, .1]]

            #make sure the array is the right dimensions.
            return numpy.array(zip(*top_hiatus))

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

            #strength = core.properties['accumulation memory strength']
            #mean = core.properties['accumulation memory mean']
            strength = core.properties['Bacon Memory: Strength']
            mean = core.properties['Bacon Memory: Mean']

            memorya = strength * mean
            memoryb = strength * (1-mean)

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

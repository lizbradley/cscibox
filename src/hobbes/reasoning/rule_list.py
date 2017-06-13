from confidence import Validity
from rules import Observation, Argument, Simulation, make_rule
from environment import define, calc, lookup, metadata, db
plausible, probable, sound, accepted = \
    Validity.plausible, Validity.probable, Validity.sound, Validity.accepted
obs, arg, sim = Observation, Argument, Simulation
r = make_rule

# I don't know what this is -- THN
NOT = (True, True, 0)
OR = (False, False, 0)

define('core site', lookup(metadata('Core Site')))
define('age/depth model', lookup(metadata('Age/Depth Model')))
define(('model age', 'depth'),
       calc('valueat', 'age/depth model', 'depth'))
define('run', lookup(metadata('run')))

"""
CALVIN API

r = make_rule
def make_rule(conc, rhs_list, validity, template=()):
  rhs_list is a list of arg() or obs()
  validity = plausible, probable, sound, accepted
  template (OR NOT)
  conc created from string or tuple

arg(name, *params) == list of strings

strings from arg are looked up in ?
You can have multiple rules with the same conclusion

define(fname, *params)
    uses reflection to find function matching fname
    if that fails, it tries param[0].fname

obs(name, *params)

calc(fname, *params)
  looks up using reflection
  if that fails, it tries looking in param[0].__dict__

metadata(v) checks core.properties[v]

sim() is not used as

lookup returns model or none

db() maybe not implemented?
"""

r('invalid model',
  arg('model prediction'), accepted, NOT)

r('bacon runs fast', arg('high section thickness'), accepted)
r('high section thickness',obs('>', 'section thickness', 30), accepted)
r('bacon runs fast', arg('low bacon iterations'), sound)
r('low bacon iterations', obs('<', 'bacon iterations', 300), sound)

# viv rule - not done
r('increase core thickness', obs('<', 'section thickness', 5), accepted)
r('increase section thickness to 50', obs('<', 'bacon diff', 3), accepted)
r('increase number of sections', obs('<', 'bacon section', 10), accepted)
r('decrease number of sections', obs('>', 'bacon section', 200), accepted)

define('section thickness', calc('section_thickness','run'))
define('bacon iterations', calc('bacon_iterations','run'))
define('bacon memory mean', calc('bacon_memory_mean','run'))
define('bacon memory strength', calc('bacon_memory_strength','run'))
define('bacon diff', calc('bacon_diff','run'))
define('bacon section', calc('bacon_section','run'))

r('sensible defaults', obs('~=', 'bacon memory mean', 0.7), plausible)
r('sensible defaults', obs('~=', 'bacon memory strength', 4), plausible)
r('decrease section width', arg('invalid model'), plausible)
r('Increase iterations', arg('invalid model'), plausible)
r('Increase iterations', 'converging to different distributions', plausible) # (Need Simulation)
r('Increase memory' , 'smooth accumulation rate', plausible, NOT)
r('Decrease memory', 'Invalid Model', plausible)

define('accumulation prior mean', calc('accumulation_mean','run'))

r('model prediction', arg('model covers origin'), accepted)
r('model prediction', arg('reversal'), accepted, NOT)

# From Sediment Core Rules.rtf:
# Age at the surface of the core should be 0, but a tolerance of (?~2k) years is sensible, since the cores are actually basically mush

r('model covers origin', obs('<', ('model age', 'depth'), 2000), sound)


r(('hiatus at depth', 'depth', 'age'),
  [obs('>', ('model age', 'depth'), 'age'),
   arg('hiatus at depth', 'depth')], sound)
r(('hiatus at depth', 'depth'),
  arg('hiatus'), probable)

r('reversal',
  obs('<', 'min age slope', 0), accepted)

r('model prediction', arg('smooth accumulation rate'), accepted)

r('smooth accumulation rate',
  obs('<', 'max accumulation elbow', 20), sound)
define('min age slope',
       calc('min', ('slope', 'depth', 'Best Age')))
define(('slope', 'var1', 'var2'),
       calc('slope', 'var1', 'var2'))
define('max accumulation elbow',
       calc('max', 'normalized accumulation angles'))
define('normalized accumulation angles',
       calc('normalize_angles', 'accumulation angles'))
define('accumulation angles',
       calc('find_angles', 'depth', 'Best Age'))

# see harding_example_notes.txt
r('need marine curve',
  obs('is true', 'in ocean'), accepted)
define('in ocean',
       calc('is_ocean', 'core site'))


r('mean squared error is positive', obs('>', 'mean squared error', 0), sound)
define('mean squared error',
        calc('mean_squared_error', 'Calibrated 14C Age', 'Best Age'))

r('normalized error is positive', obs('>', 'normalized error', 0), sound)
define('normalized error',
        calc('normalized_error', 'Calibrated 14C Age', 'Best Age'))

"""ice cores below"""

r('no snow melt',
  arg('current temperature rarely above freezing'), sound)
r('no snow melt',
  arg('past temperature rarely above freezing'), accepted)

r('current temperature rarely above freezing',
  obs('<', 'current temperature gaussian', 0, .95), accepted)
r('current temperature rarely above freezing',
  obs('<', 'current average temperature', 0), plausible)
define('current temperature gaussian',
  calc('synth_gaussian', 'current average temperature', 'current temperature variability'))
define('current average temperature',
  lookup(metadata('average temperature'),
         db('NOAA temperatures', 'average', 'latitude', 'longitude')))
define('current temperature variability',
  lookup(metadata('temperature variability'),
         db('NOAA temperatures', 'variability', 'latitude', 'longitude')))
'''
data for temperature avg & variability options --
http://www.worldclim.org/formats
https://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=obs_m&theme=ghcndms
http://www.ncdc.noaa.gov/cag/mapping/global
http://nsidc.org/data/nsidc-0536
 -- plan to chain an undergrad to extract this data from appropriate api

#remember models assume mean annual temp as given is the mean annual temp 10m below surface
'''


r('past temperature rarely above freezing',
  obs('<', 'past/current temperature gaussian', 0, .95), sound)
r('past temperature rarely above freezing',
  obs('<', 'past average temperature', -2), probable)
define('past average temperature',
  calc('past_avg_temp', '?')) #RULE: ask expert how to calc past temp from core temps
define('past/current temperature gaussian',
  calc('synth_gaussian', 'past average temperature', 'current temperature variability'))


r(('no annual signal', 'depth interval'),
  obs('within %', ('counted years', 'depth interval'), ('known timescale', 'depth interval'), .15), probable,
  NOT)


r(('stop layer counting', 'depth interval'),
  arg('number of peaks per series is normal', 'depth interval'), sound, NOT)
r(('number of peaks per series is normal', 'depth interval'),
  obs('within', ('normal peak count', 'depth interval'),
      ('current peak count', 'depth interval')), sound)
define(('known depth list', 'proxy list'),
       calc('known_depth_proxies', 'depth interval'))
define(('normal peak count', 'depth interval'),
       calc('get_normal_peak_behavior', ('known depth list', 'proxy list')))
define(('current peak count', 'depth interval'),
       calc('count_peaks_per_proxy', ('known depth list', 'proxy list')))

define(('counted years', 'depth interval'),
       'run straticounter on the depth interval!!!')
'''
define(('known timescale', 'depth interval'),
       lookup(metadata('known timescale', 'depth interval')))
'''

"""

<token name> <= [<observation>, <data lookup>, <argument>, <simulation?>]xn,
                [<validity>], [and/or];

<data lookup> := (description of how to read from metadata/sample(s)/db/ask user)
    should set token name value := data looked up
    allow for avgs, min, max from sample data... as well as an extracted list?
<argument> := <token name>
<observation> := <token-or-value> <function> <token-or-value> [<other data for function>]
<simulation> := <function name> <function params (as tokens or values)>
    to consider -- allow passing of actual functions here? scary ick...

<function> := (currently have) <, >, <=, >=, =
    -- also need for-all and there-exists, probably

Parameters to firn models -> they typically need a mean annual temp & an initial snow density
 - mean annual temp is actually intended as the mean annual temp @ 10m below surface
 - initial snow density is the limit of the snow density at the very surface; often
  an approx is used that is the density of the top ~1m of snow-ice

Former Ice Rules

#ice comes from greenland or antarctica

add_cheap_model('Herron-Langway')
add_cheap_model('Li and Zwally (2004)')#?!??!
add_cheap_model('Spencer 2001')
#Herron Langway and Li and Zwally are firn models

#climate model firn models
#need to use these ones for predicting seasonality
'Helsen 2008'
'Ligtenberg' #includes slow melt

#non-cheap firn?
'Barnola 91'
'Morris 2014'
'Arthern 2010' #good for low accum rate


add_cheap_model('Dansgaard-Johnsen')
#simple flow model -- good for extremely simple first-pass age modelling
#http://www.iceandclimate.nbi.ku.dk/research/flowofice/modelling_ice_flow/ice_flow_models_for_dating/

#mean annual temp is 10 m below surface
#initial snow density lim of density at surface (approx) -- often meas as top ~meter
add_reqs('Herron-Langway', ['mean annual temp', 'mean annual accum rate', 'initial snow density'])
add_reqs('Helsen 2008', ['time series of temp & accum rates (avail since 1980)'])
 #done using a climate model

model_quality('Herron-Langway', 'accurate to 30% in antarct (uncert greenland)')
 #have to take into account uncert in input data (mean temp etc)
model_quality('Herron-Langway', 'thinning rate <5mm/day over top 20 m -- antarct') #if that's not true your model is trash
model_quality('Li and Zwally', 'mean annual temp > 256.8K') #produces physically impossible results
 #predicts too low a compaction rate as you approach said temp
model_quality('firn, in antarctica', 'density should increase smoothly w/ depth') #"firn quakes" are rare
model_usefulness('Helsen 2008', 'year over year density changes (high precision)')
#in general running firn models against each other gives an estimate of overall
#uncertainty -- expectation based on error correlation based on model similarity
 # expected Barnola has very uncorrelated error w/ Spencer
 #models generally fall in a group w/ Herron-Langway or Li and Zwally; run models
  #in different groups to get some kind of useful uncert estimate
#herron-langway, spencer, and barnola all use ~same methodology

add_assumption('Spencer 2001', 'mean temp 216-256')
add_assumption('Spencer 2001', 'mean accum rate 0.022-1.2 m w.e./a')
 #best for these ranges! -- especially on the edges? wheeeeeeeeeeeeee
 #relationship should be ~"right" between temp & accum
 #this is a KNN fit type model...
 #don't extrapolate outside vv bad
 #not quite right at v surface; better than other models at greater depths

add_assumption('Herron-Langway', Conclusion('no ice flow'), Validity.sound)
add_assumption('Herron-Langway', Conclusion('steady state solution'), Validity.accept)


add_rule('ice <dense glacier', 'depth<25m', Validity.sound)
add_rule('never use a firn model in a blue ice region -- ask intertubes')
add_rule('best for warm firn -- Ligtenberg 2011')

#dynamic steady-state relationship?
add_rule('greenland: over time at a depth-point, density varies by ~5%')
add_rule('greenland: only top 3.5 water-meters varies within a year')
add_rule('antarct: seasonal variations contained to upper 5 m')


add_rule(Conclusion('no ice flow'), 'inland core', Validity.prob)
add_rule(Conclusion('constant temperature'), 'not true')
add_rule(Conclsuion('constant temperature'), 'more likely in vv cold antarctic')
add_rule(Conclusion('constant accumulation'), 'more likely inland?')
add_rule(Conclusion('constant accumulation'), 'not true')
#dynamicity -- year/year, decade, sometimes millenial
add_rule(Conclusion('steady state solution'), 'granularity of solution is reduced...', Validity.accept)
#within a year or between years? --> dynamic == steady if constant temp & accum
add_rule(Conclusion('steady state solution'), 'constant temperature' & 'constant accumulation', Validity.sound)
#steady state is often good enough for delta-age


add_assumption('Bacon', Conclusion('smooth change', ('accumulation rate',)),
                     Validity.sound)

add_rule(Conclusion('smooth change', 'variablething'),
               'abs(2nd derivative) < x', Validity.sound)



<with not-great conf, can try both ways and poll user with results>

"""

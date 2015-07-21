from rules import *
from conclusions import Conclusion
from confidence import Validity

"""
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
 
add_assumption('(most) firn models', Conclusion('no snow melt'), Validity.accept)
add_assumption('firn models', Conclusion('ice <dense than glacier ice'), Validity.accept)
add_assumption('Herron-Langway', Conclusion('no ice flow'), Validity.sound)
add_assumption('Herron-Langway', Conclusion('steady state solution'), Validity.accept)


add_rule('ice <dense glacier', 'depth<25m', Validity.sound)
add_rule('no snow melt', 'temp < x')
add_rule('never use a firn model in a blue ice region -- ask intertubes')
add_rule('if the site is too warm there will be a lot of melting and you should not use most firn models')
 # how warm is too warm?
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


"""
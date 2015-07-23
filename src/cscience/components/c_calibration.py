import cscience
import cscience.components
from cscience.components import UncertainQuantity

import math
import numpy as np
from scipy import interpolate, integrate
import wx, wx.html
import urllib2, httplib

THRESHOLD = .0000001

class Distribution(object):

    def __init__(self, years, density, avg, range):
        #trim out values w/ probability density small enough it might as well be 0.
        #note that these might want to be re-normalized, though the effect *should*
        #be essentially negligible
        #only trims the long tails at either end; 0-like values mid-distribution
        #will be conserved
        minvalid = 0
        maxvalid = len(years)
        #first, find the sets of indices where the values are ~0
        for index, prob in enumerate(density):
            if prob >= THRESHOLD:
                minvalid = index
                break
        for index, prob in enumerate(reversed(density)):
            if prob >= THRESHOLD:
                maxvalid = len(years) - index
                break

        #make sure we have 0s at the ends of our "real" distribution for my
        #own personal sanity.
        if minvalid > 0:
            minvalid -= 1
            density[minvalid] = 0
        if maxvalid < len(years):
            density[maxvalid] = 0
            maxvalid += 1

        #TODO: do this as part of a component, and allow long tails (a smaller
        #threshold) on samples we are less confident in the goodness of
        self.x = years[minvalid:maxvalid]
        self.y = density[minvalid:maxvalid]
        self.average = avg
        self.error = (range[1]-avg, avg-range[0])

    def __setstate__(self, state):
        if 'x' in state:
            self.__dict__ = state
        else:
            try:
                self.average = state[0]
                self.error = state[1]
            except KeyError:
                self.__dict__ = state
            except:
                self.x = []
                self.y = []
                self.average = 0
                self.error = 0
                
class ReservoirCorrection(cscience.components.BaseComponent):
    visible_name = 'Reservoir Correction'
    inputs = {'required':('14C Age',)}
    outputs = {'Corrected 14C Age': ('float', 'years', True),
               'Reservoir Correction':('float', 'years', True)}
    
    params = {'reservoir database':('Latitude', 'Longitude', 'Delta R', 'Error')}

    def run_component(self, core):
        latlng = (core['all']['Latitude'], core['all']['Longitude'])
        if latlng[0] is None or latlng[1] is None:
            self.user_inputs(core, [('Latitude', ('float', None, False, (-90, 90))),
                                    ('Longitude', ('float', None, False, (-180, 180)))])
            latlng = (core['all']['Latitude'], core['all']['Longitude'])
            
        adj_point = self.get_closest_adjustment(*latlng)
        dlg = ReservoirCorrection.MapDialog(latlng, adj_point)
        if dlg.ShowModal() == wx.ID_OK:
            core['all']['Reservoir Correction'] = UncertainQuantity(adj_point.get('Delta R', 0), 'years',
                                                                    adj_point.get('Error', [0]))
        else:
            self.user_inputs(core, [('Reservoir Correction', ('float', 'years', True))])
        dlg.Destroy()
            
        for sample in core:
            sample['Corrected 14C Age'] = sample['14C Age'] + (-sample['Reservoir Correction'])
            
    def get_closest_adjustment(self, core_lat, core_lng):
        def haversine(lat1, lng1, lat2, lng2):
            """ 
            Calculate the great circle distance between two points
            on the earth (inputs in decimal degrees)
            """
            lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
            a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1) * \
                math.cos(lat2) * math.sin((lng2-lng1)/2)**2 
            haver = 2 * math.asin(math.sqrt(a))
            
            #6367 --> approx radius of earth in km
            return 6367 * haver
            
        distance = 50000 #max distance between 2 points on earth is ~20k km
        closest_point = None
        
        for val in self.paleobase['reservoir database'].itervalues():    
            if val['Delta R'] is not None and val['Error'] is not None:
                new_distance = haversine(core_lat, core_lng, 
                                         val['Latitude'], val['Longitude'])
                if new_distance < distance:
                    distance = new_distance
                    closest_point = val

        return closest_point
    
    class MapDialog(wx.Dialog):
        """
        A nice user-friendly map to show where the reservoir correction point
        we're using from our database turns out to be
        """
        MAP_FORMAT = """<html xmlns="http://www.w3.org/1999/xhtml">
            <img src="http://maps.googleapis.com/maps/api/staticmap?size=400x300&markers=color:blue|label:S|{0},{1}&markers=color:red|label:R|{2},{3}"
            </img></html>"""
    
        def __init__(self, core_loc, closest_data):
            super(ReservoirCorrection.MapDialog, self).__init__(
                        None, title="Reservoir Location Map", style=wx.CAPTION)
    
            sizer = wx.BoxSizer(wx.VERTICAL)
            try:
                urllib2.urlopen('http://www.google.com', timeout=1)
            except (urllib2.URLError, httplib.BadStatusLine) as err:
                # No network connection, fallback to textual display (no map)
                sizer.Add(wx.StaticText(self, label="Selected Reservoir Coordinates:"),
                          flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                sizer.Add(wx.StaticText(self, label="{0}, {1}".\
                            format(closest_data['Latitude'], closest_data['Longitude'])),
                          flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                sizer.Add(wx.StaticText(self, label="Reservoir Age: {0}, Error: {1}".\
                            format(self.closest_data['Delta R'], self.closest_data['Error'])),
                          flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
            else:
                #google works, anyway...
                self.browser = wx.html.HtmlWindow(self, wx.ID_ANY, size=(400, 300))
                sizer.Add(self.browser, flag=wx.EXPAND | wx.ALL, border=0)
    
                h_sizer = wx.BoxSizer(wx.HORIZONTAL)
                h_sizer.Add(wx.StaticText(self, label="R = Reservoir Location"),
                            flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                h_sizer.Add(wx.StaticText(self, label="S = Sample Location"),
                            flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                sizer.Add(h_sizer)
    
                html_string = self.MAP_FORMAT.format(core_loc[0], core_loc[1], 
                                closest_data['Latitude'], closest_data['Longitude'])
                self.browser.SetPage(html_string)
    
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            button_sizer.Add(wx.Button(self, wx.ID_CANCEL, 
                              label="Reject Selection (Input Manual Correction)"), 
                             flag=wx.CENTER | wx.ALL, border=5)
            button_sizer.Add(wx.Button(self, wx.ID_OK, label="Accept Selection"), 
                             flag=wx.CENTER | wx.ALL, border=5)
    
            sizer.Add(button_sizer, flag=wx.CENTER | wx.TOP, border=5)
    
            self.SetSizer(sizer)
            self.Centre()
            self.SetSize((420, 400))

class IntCalCalibrator(cscience.components.BaseComponent):
    visible_name = 'Carbon 14 Calibration (CALIB Style)'
    inputs = {'required':('14C Age',), 'optional':('Corrected 14C Age',)}
    outputs = {'Calibrated 14C Age':('float', 'years', True)}

    params = {'calibration curve':('14C Age', 'Calibrated Age', 'Sigma')}

    def prepare(self, *args, **kwargs):
        super(IntCalCalibrator, self).prepare(*args, **kwargs)

        #set up 3 lists, correlated by index, sorted by calibrated age, containing:
        #calibrated age, carbon 14 age, sigma value
        #from the configured calibration curve.
        curve = [(r['Calibrated Age'], r['14C Age'], r['Sigma']) for r in
                 self.paleobase['calibration curve'].itervalues()]
        curve.sort()
        self.calib_age_ref, self.c14_age, self.sigmas = map(np.array, zip(*curve))

    def run_component(self, core):
        interval = 0.683
        for sample in core:
            try:
                age = sample['Corrected 14C Age'] or sample['14C Age']
                sample['Calibrated 14C Age'] = self.convert_age(age, interval)
            except ValueError:
                # sample out of bounds for interpolation range? we can just
                # ignore that.
                pass

    # inputs: CAL BP and Sigma, output: un-normed probability density
    def density(self, avg, error):
        sigmasq = error ** 2. + self.sigmas ** 2.
        exponent = -((self.c14_age - avg) ** 2.) / (2.*sigmasq)
        alpha = 1. / np.sqrt(2.*np.pi * sigmasq);
        return alpha * np.exp(exponent)

    def convert_age(self, age, interval):
        """
        returns a "base" calibrated age interval
        """

        #Assume that Carbon 14 ages are normally distributed with mean being
        #Carbon 14 age provided by lab and standard deviation from intCal CSV.
        #This probability density is mapped to calibrated (true) ages and is
        #no longer normally (Gaussian) distributed or normalized.
        unnormed_density = self.density(*age.unitless_normal())

        #unnormed_density is mostly zeros so need to remove but need to know years removed.
        nz_ages = []
        nz_density = []

        for calage, dens in zip(self.calib_age_ref, unnormed_density):
            if dens:
                #TODO: should this be done in some more efficient way? probably
                nz_ages.append(calage)
                nz_density.append(dens)

        calib_age_ref = np.array(nz_ages)
        unnormed_density = np.array(nz_density)
        # interpolate unnormed density to annual resolution
        annual_calib_ages = np.array(
                    range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))
        unnormed_density = np.interp(annual_calib_ages,
                                     calib_age_ref, unnormed_density)
        calib_age_ref = np.array(
                    range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))

        #Calculate norm of density and then divide unnormed density to normalize.
        norm = integrate.simps(unnormed_density, calib_age_ref)
        normed_density = unnormed_density / norm
        #Calculate mean which is the "best" true age of the sample.

        #this could be done vectorized instead of with a loop.
        weighted_density = np.zeros(len(calib_age_ref))
        for index, year in enumerate(calib_age_ref):
            weighted_density[index] = year * normed_density[index]
        mean = integrate.simps(weighted_density, calib_age_ref)

        #The HDR is used to determine the error for the mean calculated above.
        calib_age_error = self.hdr(normed_density, calib_age_ref, interval)
        #TODO: these are at annual resolution; we could get by with 5-year
        #no problem...
        distr = Distribution(calib_age_ref, normed_density,
                             mean, calib_age_error)

        cal_age = cscience.components.UncertainQuantity(data=mean, units='years',
                                                        uncertainty=distr)
        return cal_age

    #calcuate highest density region
    def hdr(self, density, years, interval):
        #Need to approximate integration by summation so need all years in range

        yearly_pdensity = np.array([years, density])
        yearly_pdensity = np.fliplr(yearly_pdensity[:,yearly_pdensity[1,:].argsort()])

        summation_array = np.cumsum(yearly_pdensity[1,:])

        index_of_win = np.searchsorted(summation_array, interval)
        good_years = yearly_pdensity[0,:index_of_win]
        return (min(good_years), max(good_years))




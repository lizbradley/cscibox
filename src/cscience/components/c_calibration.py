"""Components for computations.

This module contains the ReservoirCorrection and IntCalCalibrator components.
For more on creating components see writing_components.txt in src/ .

"""

import urllib2
import httplib
import wx
import wx.html
import numpy as np
from scipy import integrate

import cscience
import cscience.components
from cscience.components import ComponentAttribute as Att
from cscience.framework import datastructures



class ReservoirCorrection(cscience.components.BaseComponent):
    """"A component to add Reservoir Correction for a sample.

    This component uses the Latitude and Longitude for the core to look up the correction.
    It pops up a map with the nearest location in the database.
    If that choice is incorrect, the user can put in a manual correction.
    If the core has no Lat/Long, run_component will error.

    """

    visible_name = 'Reservoir Correction'
    # what uses inputs?
    inputs = [Att('14C Age'),
              #Although we can set this at the core level, we also take it as
              #a sample-granularity input here.
              Att('Reservoir Correction', required=False),
              Att('Core Site', required=False, core_wide=True)]
    outputs = [Att('Corrected 14C Age', type='float', unit='years', error=True)]

    params = {'reservoir database':('Latitude', 'Longitude', 'Delta R', 'Error')}

    def run_component(self, core, progress_dialog):
        """Main entry point for the component."""

        geo = core.properties['Core Site']
        if not geo:
            raise AttributeError("Core Site Not Found!")
        else:
            adj_point = self.get_closest_adjustment(geo)
            dlg = ReservoirCorrection.MapDialog(geo, adj_point)
            if dlg.ShowModal() == wx.ID_OK:
                self.set_value(core, 'Reservoir Correction',
                               datastructures.UncertainQuantity(
                                   adj_point.get('Delta R', 0),
                                   'years', adj_point.get('Error', [0])))
                self.set_value(core, 'Manual Reservoir Correction', False)
            else:
                self.user_inputs(core, [('Reservoir Correction', ('float', 'years', True))])
                self.set_value(core, 'Manual Reservoir Correction', True)
            dlg.Destroy()
        for sample in core:
            sample['Corrected 14C Age'] = sample['14C Age'] + (-sample['Reservoir Correction'])

    def get_closest_adjustment(self, core_loc):

        distance = 50000 #max distance between 2 points on earth is ~20k km
        closest_point = None

        for val in self.paleobase['reservoir database'].itervalues():
            if val['Delta R'] is not None and val['Error'] is not None:
                new_distance = core_loc.haversine_distance(val['Latitude'], val['Longitude'])
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
            except (urllib2.URLError, httplib.BadStatusLine):
                # No network connection, fallback to textual display (no map)
                sizer.Add(wx.StaticText(self, label="Selected Reservoir Coordinates:"),
                          flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                sizer.Add(wx.StaticText(self, label="{0}, {1}".\
                            format(closest_data['Latitude'], closest_data['Longitude'])),
                          flag=wx.EXPAND | wx.CENTER | wx.ALL, border=5)
                sizer.Add(wx.StaticText(self, label="Reservoir Age: {0}, Error: {1}".\
                            format(closest_data['Delta R'], closest_data['Error'])),
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

                html_string = self.MAP_FORMAT.format(core_loc.lat, core_loc.lon,
                                                     closest_data['Latitude'],
                                                     closest_data['Longitude'])
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
    inputs = [Att('14C Age'),
              Att('Corrected 14C Age', required=False)]
    outputs = [Att('Calibrated 14C Age', type='float', unit='years', error=True)]

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

    def run_component(self, core, progress_dialog):
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
        alpha = 1. / np.sqrt(2.*np.pi * sigmasq)
        return alpha * np.exp(exponent)

    def convert_age(self, age, interval):
        """Returns a "base" calibrated age interval. """

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
                nz_ages.append(calage)
                nz_density.append(dens)

        calib_age_ref = np.array(nz_ages)
        unnormed_density = np.array(nz_density)
        # interpolate unnormed density to annual resolution
        annual_calib_ages = np.array(range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))
        unnormed_density = np.interp(annual_calib_ages, calib_age_ref, unnormed_density)
        calib_age_ref = np.array(range(int(calib_age_ref[0]), int(calib_age_ref[-1]+1)))

        #Calculate norm of density and then divide unnormed density to normalize.
        norm = integrate.simps(unnormed_density, calib_age_ref)
        normed_density = unnormed_density / norm
        #Calculate mean which is the "best" true age of the sample.

        weighted_density = np.array([year*dens for year, dens in 
                                     zip(calib_age_ref, normed_density)])

        mean = integrate.simps(weighted_density, calib_age_ref)

        #The HDR is used to determine the error for the mean calculated above.
        calib_age_error = hdr(normed_density, calib_age_ref, interval)

        distr = datastructures.ProbabilityDistribution(calib_age_ref, normed_density,
                                                       mean, calib_age_error)

        return datastructures.UncertainQuantity(data=mean, units='years',
                                                uncertainty=distr)

#calcuate highest density region
def hdr(density, years, interval):
    #Need to approximate integration by summation so need all years in range

    yearly_pdensity = np.array([years, density])
    yearly_pdensity = np.fliplr(yearly_pdensity[:, yearly_pdensity[1, :].argsort()])

    summation_array = np.cumsum(yearly_pdensity[1, :])

    index_of_win = np.searchsorted(summation_array, interval)
    good_years = yearly_pdensity[0, :index_of_win]
    return (min(good_years), max(good_years))

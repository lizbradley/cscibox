import quantities as pq
import numpy as np
import csv
import scipy.interpolate
import time
from dateutil import parser as timeparser
import math

#Add units woo
micrograms = pq.UnitMass('micrograms', pq.gram*pq.micro, symbol='ug')
kiloyears = pq.UnitTime('kiloyears', pq.year*pq.kilo, symbol='ky')
megayears = pq.UnitTime('megayears', pq.year*pq.mega, symbol='My')

len_units = ('millimeters', 'centimeters', 'meters')
time_units = ('years', 'kiloyears', 'megayears')
mass_units = ('micrograms', 'milligrams', 'grams', 'kilograms')
loc_units = ('degrees',)
standard_cal_units = ('dimensionless',) + len_units + time_units + mass_units + loc_units
unitgroups = (len_units, time_units, mass_units)

#user-visible list of types
SIMPLE_TYPES = ("Float", "String", "Integer", "Boolean", "Time")
TYPES = SIMPLE_TYPES + ("Geography", "Publication List", "Age Model")

def is_numeric(type_):
    #TODO: this is a copy of an Attribute method...
    return type_.lower() in ('float', 'integer')

def get_conv_units(unit):
    """
    Returns a list of units that can be converted to/from the passed unit
    """
    unit = str(unit)
    for group in unitgroups:
        if unit in group:
            return group
    return (unit,)


class UncertainQuantity(pq.Quantity):

    def __new__(cls, data, units='', uncertainty=0, dtype='d', copy=True):
        ret = pq.Quantity.__new__(cls, data, units, dtype, copy)
        ret.uncertainty = Uncertainty(uncertainty, units)
        return ret

    def __add__(self, other):
        # If there is no uncertainty on other
        if (not hasattr(other, "uncertainty")) or (not other.uncertainty.magnitude):
            mag = super(UncertainQuantity, self).__add__(other)
            return UncertainQuantity(mag, units=mag.units, uncertainty = self.uncertainty)

        #okay, so this should handle the units okay...
        mag = super(UncertainQuantity, self).__add__(other)
        if len(self.uncertainty.magnitude) == 1 and \
           len(other.uncertainty.magnitude) == 1:
              #now, new uncertainty is the two squared, added, sqrted
            error = float(np.sqrt(self.uncertainty.magnitude[0] ** 2 +
                                  other.uncertainty.magnitude[0] ** 2))
        else:
            stup = self.uncertainty.get_mag_tuple()
            otup = other.uncertainty.get_mag_tuple()
            error = [float(np.sqrt(stup[0] ** 2 + otup[0] ** 2)),
                     float(np.sqrt(stup[1] ** 2 + otup[1] ** 2))]
        return UncertainQuantity(mag, units=mag.units, uncertainty=error)

    def __neg__(to_negate):
        return UncertainQuantity(super(UncertainQuantity, to_negate).__neg__(),
                                 units=to_negate.units,
                                 uncertainty=to_negate.uncertainty.magnitude)

    def unitless_normal(self):
        """
        Get the value and a one-dimensional error of this quantity, without
        units. This is useful when you know the value you have should have a
        Gaussian error distribution and you need the values stripped of metadata
        for computation ease
        """
        value = self.magnitude
        uncert = self.uncertainty.as_single_mag()
        return (value, uncert)

    def __repr__(self):
        return '%s(%s, %s, %s)'%(
            self.__class__.__name__,
            repr(self.magnitude),
            self.dimensionality.string,
            repr(self.uncertainty)
        )

    #Copy pasted from the superclass to get the overwriting of (the setter of) units to work.
    @property
    def units(self):
        return pq.Quantity(1.0, (self.dimensionality))
    @units.setter
    #End the copy paste above!
    def units(self, new_unit):
        #Copy pasted from the superclass function we're overwriting
        try:
            assert not isinstance(self.base, pq.Quantity)
        except AssertionError:
            raise ValueError('can not modify units of a view of a Quantity')
        try:
            assert self.flags.writeable
        except AssertionError:
            raise ValueError('array is not writeable')
        to_dims = pq.quantity.validate_dimensionality(new_unit)
        if self._dimensionality == to_dims:
            return
        to_u = pq.Quantity(1.0, to_dims)
        from_u = pq.Quantity(1.0, self._dimensionality)
        try:
            cf = pq.quantity.get_conversion_factor(from_u, to_u)
        except AssertionError:
            raise ValueError(
                'Unable to convert between units of "%s" and "%s"'
                %(from_u._dimensionality, to_u._dimensionality)
            )
        mag = self.magnitude
        mag *= cf
        self._dimensionality = to_u.dimensionality
        #END copy paste
        self.uncertainty.units(new_unit) #All of that so we could run this line when our units were changed.

    def __getstate__(self):
        """
        Return the internal state of the quantity, for pickling
        purposes.

        """
        cf = 'CF'[self.flags.fnc]
        state = (1,
                 self.shape,
                 self.dtype,
                 self.flags.fnc,
                 self.tostring(cf),
                 self._dimensionality,
                 self.uncertainty
                 )
        return state

    def __setstate__(self, state):
        (ver, shp, typ, isf, raw, units, uncert) = state
        np.ndarray.__setstate__(self, (shp, typ, isf, raw))
        self.uncertainty = uncert
        self._dimensionality = units

    def user_display(self):
        #force 2 decimals, then strip off trailing 0s
        #using this instead of n or g because I don't want se notation basically
        #ever.
        my_str = ('%.2f'%self.magnitude.item()).rstrip('0').rstrip('.')
        if hasattr(self, 'uncertainty'):
            return '%s%s'%(my_str, str(self.uncertainty))
        else:
            return '%s%s'%(my_str, "0")

    def __str__(self):
        dims = self.dimensionality.string
        if dims == 'dimensionless':
            return self.user_display()
        return '%s %s'%(self.user_display(), dims)


class Uncertainty(object):

    def __init__(self, uncert, units):
        self.distribution = None
        self.magnitude = []
        self._units = units
        if uncert:
            try:
                mag = uncert.error
            except AttributeError:
                if not hasattr(uncert,'__len__'):
                    mag = [uncert]
                else:
                    try:
                        if len(uncert)>2:
                            raise ValueError('Uncert must be a single value, '
                                             'pair of values, or matplotlib distribution')
                    except TypeError:
                        mag = [uncert] #Quantity has __len__ but is unsized?!?!?!
                    else:
                        mag = uncert
            else:
                self.distribution = uncert
            self.magnitude = [pq.Quantity(val, units) for val in mag]

    def __add__(self,other):
        # TODO make add much more robust
        mag = self.magnitude[0] + other.magnitude[0]
        return(Uncertainty(mag, self._units))

    def units(self, new_unit):
        for quant in self.magnitude:
            quant.units = new_unit
        self._units = new_unit

    def __float__(self):
        return self.magnitude[0].magnitude.item()

    def __repr__(self):
        if self.distribution:
            uncert = repr(self.distribution)
        else:
            uncert = str(self.magnitude)
        return '%s(%s)' % (self.__class__.__name__, uncert)

    def get_mag_tuple(self):
        #strip units for great justice (AKA graphing sanity)
        if not self.magnitude:
            return (0, 0)
        elif len(self.magnitude) > 1:
            return (self.magnitude[0].magnitude, self.magnitude[1].magnitude)
        else:
            return (self.magnitude[0].magnitude, self.magnitude[0].magnitude)

    def as_single_mag(self):
        if not self.magnitude:
            return 0
        else:
            return float(sum([it.magnitude for it in self.magnitude])) / len(self.magnitude)

    def __str__(self):
        if not self.magnitude:
            return ''
        elif len(self.magnitude) == 1:
            if not self.magnitude[0]:
                return ''
            else:
                mag = self.magnitude[0].magnitude.item()
                return '+/-' + ('%.2f'%mag).rstrip('0').rstrip('.')
        else:
            return '+{}/-{}'.format(*[('%.2f'%mag.magnitude). \
                            rstrip('0').rstrip('.') for mag in self.magnitude])


class GeographyData(object):
    typename = 'geo'

    def __init__(self, lat=None, lon=None, elev=None, sitename=None):
        self.lat = lat
        self.lon = lon
        self.elev = elev
        self.sitename = sitename

        self.validate()

    @classmethod
    def parse_value(cls, value):
        val = cls()

        coords = value['geometry']['coordinates']
        val.lat = coords[0]
        val.lon = coords[1]

        try:
            #TODO: is this required, and therefore we don't need to error-check it?
            val.elev = coords[2]
        except IndexError:
            pass
        val.sitename = value.get('properties', {}).get('siteName', None)
        val.validate()

        return val

    def validate(self):
        try:
            self.lat = float(self.lat) if self.lat is not None else None
            self.lon = float(self.lon) if self.lon is not None else None
        except ValueError:
            raise ValueError("Latitude and Longitude must be numeric")

        if self.lat is not None and abs(self.lat) > 90:
            print "Latitude must be between -90 and 90"
        if self.lon is not None and abs(self.lon) > 180:
            print "Longitude must be between -180 and 180"

        if self.elev is not None:
            try:
                self.elev = float(self.elev)
            except ValueError:
                raise ValueError("Elevation must be numeric or not given")

    def user_display(self):
        dispstr = ''
        if self.sitename:
            dispstr = self.sitename + ': '
        #TODO: number formatting; sextant units?
        if self.lat is not None:
            #currently assuming we never set lat w/o also setting lon
            dispstr += unicode(abs(self.lat)) + ('N ' if self.lat > 0 else 'S ')
            dispstr += unicode(abs(self.lon)) + ('E' if self.lon > 0 else 'W')
        else:
            'No Location Known'
        if self.elev is not None:
            dispstr += ' ' + unicode(self.elev)
        return dispstr

    def haversine_distance(self, otherlat, otherlng):
        """
        Calculate the great circle distance between two points
        on the earth (inputs in decimal degrees)
        """
        lat1, lng1, lat2, lng2 = map(math.radians, [self.lat, self.lon, otherlat, otherlng])
        a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1) * \
            math.cos(lat2) * math.sin((lng2-lng1)/2)**2
        haver = 2 * math.asin(math.sqrt(a))

        #6367 --> approx radius of earth in km
        return 6367 * haver

    def LiPD_tuple(self):
        value = {"type": "Feature",
                 "geometry": {"type": "Point",
                              "coordinates": [self.lat, self.lon, self.elev]},
                 "properties": {"siteName": self.sitename}}
        return ('geo', value)

    def __repr__(self):
        return 'Geo: (' + str(self.lat) + ', ' + \
            str(self.lon) + ', ' + str(self.elev) + ')'


class TimeData(object):
    typename = 'time'
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    USER_FORMAT = '%a, %b %d %I:%M %p'

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def parse_value(cls, value):
        val = cls()
        try:
            val.value = timeparser.parse(value).timetuple()
        except ValueError:
            #couldn't parse the input string as a time; give up like a wuss.
            pass
        return val

    def user_display(self):
        return time.strftime(self.USER_FORMAT, self.value)

    def LiPD_tuple(self):
        return ('timestamp', time.strftime(self.ISO_FORMAT, self.value))


class Publication(object):
    #TODO: implement alternate citation method
    def __init__(self, title='', authors=[], journal='', year='',
                       volume='', issue='', pages='', report_num=None, doi=None,
                       alternate=None):
        self.title = title
        self.authors = authors
        self.journal = journal
        self.year = year
        self.volume = volume
        self.issue = issue
        self.pages = pages
        self.report_num = report_num
        self.doi = doi
        self.alternate = alternate

    @classmethod
    def parse_value(cls, value):
        val = value.copy()
        authors = val.pop('author', [])
        val['authors'] = [auth['name'] for auth in authors]
        val['report_num'] = val.pop('report number', '')
        val['doi'] = val.pop('DOI', val.get('doi', ''))
        val['alternate'] = val.pop('alternate citation', '')
        val['journal'] = val.pop('Journal', val.get('journal', ''))

        if 'identifier' in val:
            id = val.pop('identifier')[0]
            if id.get('type', '') == 'doi':
                val['doi'] = id.get('id', '')

        return cls(**val)

    def is_valid(self):
        #Not doing a great deal of error checking on these; if you want
        #to set up a publication that makes no sense, we will let you
        # (but we do screen to keep out completely empty entries from users)
        return any((self.title, self.authors, self.journal, self.year,
                    self.volume, self.issue, self.pages, self.report_num,
                    self.doi, self.alternate))

    def user_display(self):
        #TODO: this should build lovely citations for purties.
        if self.alternate:
            return ' '.join(('(Unstructured citation data)', str(self.alternate)))
        return '%s. %s. %s %s (%s), no. %s, %s. doi:%s' % (
                 '; '.join([', '.join(names) for names in self.authors]),
                 self.title, self.journal, self.volume, self.year,
                 self.issue, self.pages, self.doi)

    def __repr__(self):
        return self.user_display()

    def LiPD_dict(self):
        value = {'author': [{'name':name} for name in self.authors],
                 'title': self.title,
                 'Journal': self.journal,
                 'year': self.year,
                 'volume':self.volume,
                 'issue':self.issue,
                 'pages':self.pages,
                 'report number': self.report_num,
                 #not ideal here but this works.
                 'identifier': [{'type':'doi', 'id':self.doi}],
                 'alternate citation': self.alternate}
        return value


class PublicationList(object):
    typename = 'publication list'
    def __init__(self, pubs=[]):
        #TODO: maintain reason-for-this-pub type data?
        #pointers, man. Pointers are the worst.
        self.publications = pubs[:]

    def __nonzero__(self):
        """
        Boolean function -- used so you can 'if' a publist to find out if there
        are any pubs in it :)
        """
        return bool(self.publications)

    def addpub(self, pub):
        #TODO: set handling?
        self.publications.append(pub)

    def addpubs(self, pubs):
        #TODO: set handling is nice here...
        self.publications.extend(pubs)

    def __repr__(self):
        return self.user_display()

    @classmethod
    def parse_value(cls, value):
        return cls([Publication.parse_value(pub) for pub in value])

    def user_display(self):
        return '\n'.join([pub.user_display() for pub in self.publications]) or 'None'

    def LiPD_tuple(self):
        #TODO: publications: what look?
        return ('pub', [pub.LiPD_dict() for pub in self.publications])

class GraphableData(object):
    '''
    Interface for graphable data.

    Needs to be able to plot itself by implementing these functions:
    '''
    def __init__(self):
        self.label = "Implement Label"
        self.independent_var_name = 'Depth'
        self.variable_name = 'Implement variable name'

    def set_selected_point(self, point):
        self.selected_point = point

    def graph_self(self, plot, options, errorbars=None):
        raise Exception("GraphableData Interface Not Implemented")

class PointlistInterpolation(GraphableData):

    def __init__(self, xs, ys, run=None, xunits='cm', yunits='years'):
        self.xpoints = xs
        self.ypoints = ys
        self.variable_name = 'Age Model'
        self.label = self.variable_name + " (" + run + ")"
        self.xunits = xunits
        self.yunits = yunits
        self.spline = scipy.interpolate.InterpolatedUnivariateSpline(
                                            self.xpoints, self.ypoints, k=1)
        self.independent_var_name = 'Depth'

    @classmethod
    def parse_value(cls, value):
        #TODO: read units
        xs = []
        ys = []
        with open(value, 'rU', newline='') as input_file:
            #TODO: define a dialect here...
            reader = csv.reader(input_file, dialect=None)
            for line in reader:
                xs.append(line[0])
                ys.append(line[1])
        return cls(xs, ys)

    def user_display(self):
        return "(Distribution Data)"

    def graph_self(self, plot, options, errorbars=False):
        xs = np.linspace(min(self.xpoints),max(self.xpoints),10000)
        ys = self.spline(xs)
        plot.plot(xs, ys, '-', color=options.color, label=self.label, linewidth=options.line_width)


    def LiPD_columns(self):
        val = {'columns': [{'number':ind, 'parameter':p, 'parameterType':'inferred',
                            'units':u, 'datatype':'csvw:NumericFormat'} for
                                ind, (p, u) in enumerate([('x', self.xunits),
                                                    ('y', self.yunits)], 1)]}

        return ('xydistribution', val)

    def __call__(self, xval):
        return self.valueat(xval)

    def valueat(self, xval):
        #TODO: figure out uncertainty...
        return UncertainQuantity(self.spline(xval), self.yunits)

class BaconInfo(GraphableData):
    def __init__(self, data, run):
        self.csv_data = data
        depths = self.csv_data[0]
        data = self.csv_data[1:]
        xs = []
        ys = []

        for ages in data:
            for (d,a) in zip(depths, ages):
                xs.append(d)
                ys.append(a)

        bacon_hist, xedges, yedges = np.histogram2d(xs,ys,bins=100)

        self.bacon_hist = bacon_hist
        # removing first element
        # maybe it's better to take the midpoints somehow
        self.xcenters = xedges[:-1] + 0.5 * (xedges[1:] - xedges[:-1])
        self.ycenters = yedges[:-1] + 0.5 * (yedges[1:] - yedges[:-1])
        self.label = 'Bacon Model' + " (" + run + ")"
        self.independent_var_name = 'Depth'
        self.variable_name = 'Bacon Model'

    @classmethod
    def parse_value(cls, value):
        # Needs to do the same as PoinListInterpolation
        pass

    def user_display(self):
        return "(Bacon Distribution)"

    def LiPD_tuple(self):
        pass

    def __call__(self, xval):
        return self.valueat(xval)

    def valueat(self, xval):
        #TODO: make this actually work
        return None

    def graph_self(self, plot, options, errorbars=None):
        # np.log to make the variables scale better
        if options.fmt:
            plot.plot(0, 0, options.fmt, color=options.color, label=self.label,
                      picker=options.point_size, markersize=options.point_size)
            plot.plot(0, 0, options.fmt, color="#eeeeee", markersize=options.
                       point_size)

        plot.contourf(self.xcenters, self.ycenters,
                np.log(1 + self.bacon_hist).T, cmap=options.colormap, alpha=0.5)

class ProbabilityDistribution(object):
    #TODO: convert this to also use a PointlistInterpolation for storing x/y
    #values, so we can use the same code all over.
    THRESHOLD = .0000001

    def __init__(self, years, density, avg, range, trim=True):
        minvalid = 0
        maxvalid = len(years)

        if trim:
            #trim out values w/ probability density small enough it might as well be 0.
            #note that these might want to be re-normalized, though the effect *should*
            #be essentially negligible
            #only trims the long tails at either end; 0-like values mid-distribution
            #will be conserved

            #first, find the sets of indices where the values are sub-threshold
            for index, prob in enumerate(density):
                if prob >= self.THRESHOLD:
                    minvalid = index
                    break
            for index, prob in enumerate(reversed(density)):
                if prob >= self.THRESHOLD:
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
        self.range = range
        self.error = (range[1]-avg, avg-range[0])

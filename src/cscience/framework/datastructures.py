import quantities as pq
import numpy as np

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

    def unitless_str(self):
        my_str = ('%.2f'%self.magnitude.item()).rstrip('0').rstrip('.')
        if hasattr(self, 'uncertainty'):
            return '%s%s'%(my_str, str(self.uncertainty))
        else:
            return '%s%s'%(my_str, "0")

    def __str__(self):
        dims = self.dimensionality.string
        if dims == 'dimensionless':
            return self.unitless_str()
        return '%s %s'%(self.unitless_str(), dims)
    

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
            

class PointlistInterpolation(object):
    
    def __init__(self, xs, ys):
        self.xpoints = xs
        self.ypoints = ys
        self.spline = scipy.interpolate.InterpolatedUnivariateSpline(
                                            self.xpoints, self.ypoints, k=1)
        
    def __call__(self, depth):
        return self.findage(depth)
        
    def findage(self, depth):
        #TODO: figure out uncertainty...
        return UncertainQuantity(self.spline(depth), 'years')
    

class ProbabilityDistribution(object):
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

    
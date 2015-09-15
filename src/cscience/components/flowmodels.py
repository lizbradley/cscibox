import cscience.components
import numpy as np
from cscience.components import UncertainQuantity

class HerronLangway (cscience.components.BaseComponent):
    # very much not finished! - Kathleen
    # built from paper HerronLangway1980 in Dropbox (folder: Papers about Firn Modelling)

    visible_name = 'Herron & Langway 1980 firn depth/age profile'
    inputs = {'required':('depth',)}
    outputs = {'Flow Model Age': ('float', 'kyears', True),
               'Flow Model Density': ('float', 'Mg/m^3', True)} #this quantity format works

    def run_component(self, core):
        parameters = self.user_inputs(core, 
                                      [('Mean Annual Temperature',('float','degC',False)),
                                       ('Annual Accumulation Rate (water)',('float','m/year',False)),
                                       ('Initial Snow Density',('float','kg/m^3',False))]) #changed from Mg - adjust accordingly

        T = parameters['Mean Annual Temperature']
        # convert T to Kelvin: (ask Laura for a better way to do this)
        T += 273.15
        A = parameters['Annual Accumulation Rate (water)']
        p0 = parameters['Initial Snow Density']

        # known constants: (again, ask Laura how to get  units)
        R = 8.314 #units are JK^(-1) mol^(-1)  (gas constant)
        pi = 0.917 #units are Mg m^(-3)
        

        k0 = 11*np.exp(-10160/(R*T))
        k1 = 575*np.exp(-21400/(R*T))

        samples = []

        #depths = core.keys()
        
        # h55 is depth of critical density (changes from stage 1 to stage 2)
        h55 = (np.log(0.55/(pi-0.55))-np.log(p0/(pi-p0)))/(pi*k0) #should be in meters?
        print 'p0 = ', p0, '\n'
        print '\n h55 = ', h55, '\n'

        # where do we change from stage 2 to stage 3?
        # got to do some math to figure this out

        p = 0
        age = 0

        for sample in core:
            # Convert depth to meters
            sample['depth'].units = 'm'
           # print sample['depth']
            h = sample['depth'].unitless_normal()[0]
            
            # first stage of densification
            if h <= h55:
                z0 = np.exp(pi*k0*h+np.log(p0/(pi-p0)))
                p = pi*z0/(1+z0)
                age = np.log((pi-p0)/(pi-p))/(k0*A)

            # TODO: add second stage of densification
            
            sample['Flow Model Density'] = UncertainQuantity(p,'Mg/m^3',0)
            sample['Flow Model Age'] = UncertainQuantity(age, 'years',0)

            #pdb.set_trace()
            #age = 0
            #if z >= h and z < H:
            #    age = ((2*H - h)/c) * (h/z - 1) + ((2*H-h)/(2*c)) * np.log((2*H - h)/h)

            #elif z >= 0  and z < h:
            #    age = ((2*H - h)/(2*c)) * np.log((2*H - h)/(2*z - h))

           # sample['Flow Model Age'] = UncertainQuantity(age, 'years',
           #                    0)
            samples.append(sample)

        # Sort the samples by depth
        samples.sort(key=lambda x: x["depth"])

        # Invert the ages
        for ii in range (0, len(samples)/2):
            end_index = len(samples) - 1 - ii
            if (end_index <= ii):
                break

            temp = samples[ii]["Flow Model Age"]
            samples[ii]["Flow Model Age"] = samples[end_index]['Flow Model Age']
            samples[end_index]['Flow Model Age'] = temp


class DansgaardJohnsen(cscience.components.BaseComponent):

    visible_name = 'Dansgaard-Johnsen ice core flow model'
    inputs = {'required':('depth',)}
    outputs = {'Flow Model Age': ('float', 'kyears', True)}

    def run_component(self, core):
        parameters = self.user_inputs(core, 
                        [('Ice Thickness', ('float', 'meters', False)),
                         ('Kink Height', ('float', 'meters', False)),
                         ('Accumulation Rate', ('float', 'meters/year', False))])

        #strip units for computation ease
        H = parameters['Ice Thickness'].magnitude
        h = parameters['Kink Height'].magnitude
        c = parameters['Accumulation Rate'].magnitude

        samples = []

        for sample in core:
            # Convert depth to meters
            sample['depth'].units = 'm'
            z = sample['depth'].unitless_normal()[0]
            #z = H - depth

            #pdb.set_trace()
            age = 0
            if z >= h and z < H:
                age = ((2*H - h)/c) * (h/z - 1) + ((2*H-h)/(2*c)) * np.log((2*H - h)/h)

            elif z >= 0  and z < h:
                age = ((2*H - h)/(2*c)) * np.log((2*H - h)/(2*z - h))

            sample['Flow Model Age'] = UncertainQuantity(age, 'years', 0)
            samples.append(sample)

        # Sort the samples
        samples.sort(key=lambda x: x["depth"])

        # Invert the ages
        for ii in range (0, len(samples)/2):
            end_index = len(samples) - 1 - ii
            if (end_index <= ii):
                break

            temp = samples[ii]["Flow Model Age"]
            samples[ii]["Flow Model Age"] = samples[end_index]['Flow Model Age']
            samples[end_index]['Flow Model Age'] = temp



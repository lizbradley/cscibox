import cscience.components
import calvin.argue
import numpy as np
from cscience.components import UncertainQuantity

class DansgaardJohnsen(cscience.components.BaseComponent):

    visible_name = 'Dansgaard-Johnsen ice core flow model'
    inputs = {'required':('depth',)}
    outputs = {'Flow Model Age': ('float', 'kyears', True)}

    def run_component(self, core):

        parameters = calvin.argue.find_value('Dansgaard-Johnsen', core)
        H = parameters['Ice Thickness(m)']
        h = parameters['Linear Depth(m)']
        c = parameters['Accumulation Rate(m/yr)']

        samples = []

        for sample in core:
            # Converto depth to meters
            sample['depth'].units = 'm'
            z = sample['depth'].unitless_normal()[0]
            #z = H - depth

            #pdb.set_trace()
            age = 0
            if z >= h and z < H:
                age = ((2*H - h)/c) * (h/z - 1) + ((2*H-h)/(2*c)) * np.log((2*H - h)/h)

            elif z >= 0  and z < h:
                age = ((2*H - h)/(2*c)) * np.log((2*H - h)/(2*z - h))

            sample['Flow Model Age'] = UncertainQuantity(age, 'years',
                               0)
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




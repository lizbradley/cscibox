import cscience.components
import calvin.argue
import numpy as np


class DansgaardJohnsen(cscience.components.BaseComponent):

    visible_name = 'Dansgaard-Johnsen ice core flow model'
    inputs = {'required':('depth',)}
    outputs = {'Model Age': ('float', 'kyears', True), 'Depth': ('float', 'cm', True)}

    def run_component(self, core):

        parameters = calvin.argue.find_value('Dansgaard-Johnsen', core)
        H = parameters['Ice Thickness(m)']
        h = parameters['Linear Depth(m)']
        c = parameters['Accumulation Rate(m/yr)']

        for sample in core:
            # Converto depth to meters
            sample['depth'].units = 'm'
            z = sample['depth'].unitless_normal()[0]

            age = 0
            if z > 0 and z < h:
                sample['Model Age'] = ((2*H-h)/c * (h/z - 1) + (2*H-h)/(2*c) * np.log((2*H - h)/h)) / 1000.0

            elif z < H and z >= h:
                sample['Model Age'] = ((2*H - h)/(2*c) * np.log((2*H - h)/(2*z - h) - 1)) / 1000.0




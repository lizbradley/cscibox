from cscience import components

class Cubic(components.BaseComponent):
    def __call__(self, samples):
        samples['interpolation curve'] = None

components.library['Cubic blah blah blah (user)'] = Cubic


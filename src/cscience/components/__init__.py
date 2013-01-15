
library = {}

class _ComponentType(type):
    """
    Auto-registers any class extending BaseComponent (or another component type)
    in the component library.
    """
    def __new__(cls, name, bases, dct):
        lib_entry = dct.pop('visible_name', None)
        newclass = super(_ComponentType, cls).__new__(cls, name, bases, dct)
        if lib_entry:
            library[lib_entry] = newclass
        return newclass

class BaseComponent(object):
    """Base class for workflow components."""
    
    __metaclass__ = _ComponentType

    def __init__(self):
        self.connections = dict.fromkeys(self.output_ports())
        self.workflow = None
        self.collections = None
        self.computation_plan = None
        
    def prepare(self, paleobase, workflow, experiment):
        self.paleobase = paleobase
        self.workflow = workflow
        self.computation_plan = experiment

    def __call__(self, core):
        """Default implementation of the worker function of a component;
        this function calls run_component and then returns the output port
        and the current set of samples. Useful for the standard case of a
        simple, linear component that does no filtering.
        """
        self.run_component(core)
        return [(self.connections['output'], core)]
        
    def run_component(self, core):
        """By default, actual work is done here so components need not worry
        about input/output specifics."""
        raise NotImplementedError("Components run_component method "
                                  "or override __call__ method")

    def connect(self, component, name='output'):
        self.connections[name] = component.input_port()
        
    def input_port(self):
        return self

    def get_connection(self, name='output'):
        return self.connections[name]

    @classmethod
    def output_ports(cls):
        return ('output',)
    
        
        


library = {}

#TODO: auto-lib components that extend BaseComponent on class decl
class BaseComponent(object):
    """Base class for workflow components."""

    def __init__(self):
        self.connections = {'output':None}
        self.workflow = None
        self.collections = None
        self.computation_plan = None
        
    def prepare(self, collections, workflow, experiment):
        self.collections = collections
        self.workflow = workflow
        self.computation_plan = experiment

    def __call__(self, samples):
        raise NotImplementedError("Components must implement __call__ method")

    def connect(self, component, name='output'):
        self.connections[name] = component.input_port()
        
    def input_port(self):
        return self

    def get_connection(self, name='output'):
        return self.connections[name]

    def output_ports(self):
        keys = self.connections.keys()
        keys.sort()
        return keys


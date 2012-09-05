class Component(object):

    """Base class for workflow components."""

    def __init__(self, collections, workflow):
        self.connections = {}
        self.connections['output'] = None
        self.workflow = workflow

    def __call__(self, samples):
        raise NotImplementedError("Components must implement __call__ method")

    def connect(self, component, name='output'):
        self.connections[name] = component

    def get_connection(self, name='output'):
        return self.connections[name]

    def output_ports(self):
        keys = self.connections.keys()
        keys.sort()
        return keys

    def set_experiment(self, experiment):
        self.experiment = experiment

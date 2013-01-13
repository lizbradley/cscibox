
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
        
        from scipy.interpolate import griddata
        #grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
        #grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
        #grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
        """
        Method that does all the actual work
        """
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


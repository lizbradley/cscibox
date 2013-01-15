import cscience.components
from scipy.interpolate import griddata
       

class Cubic(cscience.components.BaseComponent):
    visible_name = 'Cubic Interpolation (Coming Soon)'
    
    def run_component(self, samples):
        samples['interpolation curve'] = None
        #grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
        #grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
        #grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')


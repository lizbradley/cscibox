# glorified list of points. Can attach additional metadata to
# the list of point =s
class PointSet:
    # create a pointset from a list of plot points
    def __init__( self, plotpoints, vname ):
        self.m_plotpoints = plotpoints[:] # copy
        self.m_plotpoints.sort(key=lambda p: p.x)
        self.m_variable_name = vname

    def __getitem__(self, i):
        return self.m_plotpoints[i]

    def get_variable_name(self):
        return self.m_variable_name

    # returns a ([Num],[Num],[Num],[Num]) of
    # x, y, xorig, yorig
    def unzip_points(self):
        return unzip_plot_points(self.m_plotpoints)

# :: [PlotPoints] -> ([float], [float], [float], [float])
#                      x's     y's       xerr's    yerr's
def unzip_plot_points( points ):
    return (
        [i.x    for i in points],
        [i.y    for i in points],
        [i.xorig for i in points],
        [i.yorig for i in points] )
        


#Embedded file name: /home/jrahm/Projects/Calvin-jrahm/src/cscience/GUI/Util/graph/PointSet.py


class PointSet:

    def __init__(self, plotpoints, vname):
        self.m_plotpoints = plotpoints[:]
        self.m_plotpoints.sort(key=lambda p: p.x)
        self.m_variable_name = vname

    def __getitem__(self, i):
        return self.m_plotpoints[i]

    def get_variable_name(self):
        return self.m_variable_name

    def unzip_points(self):
        return unzip_plot_points(self.m_plotpoints)


def unzip_plot_points(points):
    return ([ i.x for i in points ],
     [ i.y for i in points ],
     [ i.xorig for i in points ],
     [ i.yorig for i in points ])

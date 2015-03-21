class PlotPoint:
    # Potenitally change to have a more robutst
    # statistical distribution than just error bars
    # perhaps maybe?
    def __init__(self, x, y, xorig, yorig):
        self.x = x
        self.y = y
        
        self.xorig = xorig
        self.yorig = yorig

    def __str__(self):
        return "(%s,%s,%s,%s)" % (self.x, self.y, self.xorig, self.yorig)
    def __repr__(self):
        return self.__str__()

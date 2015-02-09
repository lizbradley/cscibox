import wx
import wx.lib.scrolledpanel as scrolled
from cscience.GUI.Util.Graphing import PlotOptions, PlotCanvas

class LineFormat:
    def draw(self, dc, w, h):
        dc.DrawLine( 0, h/2, w, h/2 ) 

    def getMatFormat(self):
        return "-"

class SquareFormat:
    def draw(self, gc, w, h):
        gc.DrawRectangle( w/2-5,h/2-5, 10,10 )

    def getMatFormat(self):
        return "s"

class CircleFormat:
    def draw(self, gc, w, h):
        gc.DrawEllipse( w/2-5,h/2-5, 10,10 )

    def getMatFormat(self):
        return "o"

class StyleButton(wx.combo.BitmapComboBox):
    def __init__(self, color, *args, **kwargs):
        self.m_formats = [SquareFormat(), CircleFormat(), LineFormat()]
        self.m_color = (0,0,0)
        wx.combo.BitmapComboBox.__init__(self, *args, style=wx.CB_READONLY, **kwargs)
        self.SetMinSize( (64,40) )

        self.paint()

    def setColor(self, color):
        print "Set color"
        self.m_color = color;
        self.Clear()

    def paint(self):
        print ("Paint")
        w, h = self.GetSize()
        print ("Size1: " + str(self.GetSize()))
        self.bitmaps = [wx.EmptyBitmap(w,h) for _ in self.m_formats ]

        for i in range(len(self.bitmaps)):
            self.makeBitmap(i)

        for bmp in self.bitmaps:
            self.Append("", bmp, 0)
        self.SetSelection(0)

    def getFormatString(self,n):
        return self.m_formats[n].getMatFormat()


    def makeBitmap(self, n):
        print ("Size: " + str(self.GetSize()))
        _, h = self.GetSize()
        bmp = self.bitmaps[n]
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.Clear()
        dc.SetBrush( wx.Brush(self.m_color) );
        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)

        self.m_formats[n].draw(dc, 32, h)

        dc.SelectObject(wx.NullBitmap)

        self.bitmaps[n] = bmp


class StylePanelSubSection(wx.Panel):
    def __init__(self, def_fmt, def_color, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL);
        self.m_button = StyleButton(def_color, self)
        self.sizer.Add(self.m_button)
        self.SetSizer(self.sizer);

    def set_color(self, color):
        self.Update()

    def get_selected_fmt(self):
        return self.m_button.m_formats[self.m_button.GetSelection()].getMatFormat()
        

class StylePanel(scrolled.ScrolledPanel):
    def __init__(self, names, *args, **kwargs):
        scrolled.ScrolledPanel.__init__(self, *args, **kwargs)
        sizer = wx.GridBagSizer(len(names), 2)
        self.m_lst = []
        self.change_listener = None


        row = 0
        fmt_lst = [CircleFormat(), LineFormat(), SquareFormat()]
        color_lst = [(180, 100, 100), (100, 180, 100), (100, 100, 180), 
                     (180, 180, 100) ]

        for n in names:
            picker = wx.ColourPickerCtrl(self, wx.ID_ANY);
            picker.SetColour(color_lst[row % len(color_lst)])
            checkbox = wx.CheckBox(self, wx.ID_ANY, n)
            tmp = StylePanelSubSection(fmt_lst[row % len(fmt_lst)],
                                       color_lst[row % len(color_lst)], self )
            self.m_lst.append( (n, checkbox, tmp, picker) )

            sizer.Add(checkbox, (row, 0))
            sizer.Add(picker, (row, 2))
            sizer.Add(tmp, (row, 3))

            row += 1

        btn = wx.Button(self, label="OK");
        sizer.Add(btn, (row, 0))
        btn.Bind( wx.EVT_BUTTON, self.on_change )

        sizer.AddGrowableCol( 1 )

        self.SetSizer(sizer)
        self.SetupScrolling()
        self.SetSize((300,500))

    def on_change(self, _):
        if self.change_listener is not None:
            self.change_listener(self.get_variables_and_options())

    def add_change_listener(self, f):
        self.change_listener = f


    def get_variables_and_options(self):
        ret = []

        for (name, box, style_panel, colorpicker) in self.m_lst:
            if box.GetValue():
                opts = PlotOptions()
                opts.color = colorpicker.GetColour().Get()
                opts.fmt = style_panel.get_selected_fmt()
                ret.append( (name, opts) )

        return ret

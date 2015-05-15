import wx
import wx.lib.scrolledpanel as scrolled

import matplotlib
matplotlib.use( 'WXAgg' )
import matplotlib.backends.backend_wxagg as wxagg
import matplotlib.pyplot as plt

from cscience.GUI.Util.graph.options import PlotCanvasOptions, PlotOptions
from cscience.GUI.Util.graph.interpolation import LinearInterpolationStrategy, \
                                                  SciInterpolationStrategy
from cscience.GUI.Util.CalWidgets import CalChoice, CalCheckboxPanel

# Creates a frame that wraps a panel in a scroll panel 
# and also provides a button bar at the bottom
class FrameWrappedPanel(wx.Dialog):
    
    def __init__(self):
        super(FrameWrappedPanel, self).__init__(parent=None)

        self._m_scroll_panel = scrolled.ScrolledPanel(self)
        self._m_button_bar_panel = wx.Panel(parent=self)

        self._m_ok_button = wx.Button(self._m_button_bar_panel, id=wx.ID_OK)
        self._m_cancel_button = wx.Button(self._m_button_bar_panel, id=wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._m_ok_button)
        sizer.Add(self._m_cancel_button)
        self._m_button_bar_panel.SetSizerAndFit(sizer)

        sizer = wx.GridBagSizer()
        sizer.Add(self._m_scroll_panel, (0,0), (1,1), wx.EXPAND)
        sizer.Add(self._m_button_bar_panel, (1,0), (1,1), wx.EXPAND)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        self._m_scroll_panel.SetMaxSize((50, 100))
        self._m_scroll_panel.SetMinSize((0,0))
        self._m_scroll_panel.SetupScrolling()
        self.SetSizerAndFit(sizer)

        self.SetSize((200, 400))

        self._m_ok_listener = None
        self._m_ok_button.Bind(wx.EVT_BUTTON, self.__on_ok)
        #self._m_cancel_button.Bind(wx.EVT_BUTTON, self.__on_cancel)

    def set_ok_listener(self, listener):
        self._m_ok_listener = listener

    def __on_ok(self, evt):
        evt.Skip()
        if self._m_ok_listener is not None:
            self._m_ok_listener()

    def get_panel(self):    
        return self._m_scroll_panel

    def set_panel(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)

        self._m_scroll_panel.Layout()
        self._m_scroll_panel.SetSizerAndFit(sizer)

        self._m_scroll_panel.SetMinSize(panel.GetSize())
        self.Fit()
        self._m_scroll_panel.SetMinSize((-1,-1))

class PlotCanvas(wxagg.FigureCanvasWxAgg):
    def __init__(self, parent, size=None):
        super(PlotCanvas, self).__init__(parent, wx.ID_ANY, plt.Figure(figsize=size))

        self._m_plot = self.figure.add_subplot(1,1,1)
        self._m_pointset = {} # :: Int => (Plotter, [PlotPoint])
        self._m_canvas_options = PlotCanvasOptions()
        self._m_pick_listener = None
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self._m_pointset_table = {} # used to index into when there is a pick event
        self._m_last_pick_line = None

    def get_options(self):
        return self._m_canvas_options

    def set_options(self, new_canvas_options):
        self._m_canvas_options = new_canvas_options
        self._update_graph()
    
    # identitiy :: int - the pointset identity
    # points    :: PointSet - the list of points and their error bars
    # plotter   :: Plotter - the plotter used to plot
    def add_pointset(self, identity, points, plotter):
        # add a pointset to the dictionary of pointsets.
        # This will allow the 
        self._m_pointset[identity] = (points, plotter)

    def clear_pointset(self):
        self._m_pointset = {}

    def on_pick(self, evt):

        if not self._m_last_pick_line is None:
            try:
                self._m_last_pick_line.remove()
            except ValueError:
                pass

        data = evt.artist.get_data()
        xVal, yVal = data[0][evt.ind], data[1][evt.ind]
        lines = evt.artist.axes.plot(xVal, yVal, marker='o', linestyle='',
                                markeredgecolor=[1,0.5,0,0.5],
                                markerfacecolor='none',
                                markeredgewidth=2,
                                markersize=10,
                                label='_nolegend_',
                                gid='highlight')
        

        label = evt.artist.get_label()
        index = evt.ind

        self._m_last_pick_line = lines[0]
        try:
            point = self._m_pointset_table[label][index[0]]
            self._m_pick_listener(point)
        except KeyError:
            print ("[WARN] - invalid key " + label)

    def set_pick_listener(self, l):
        self._m_pick_listener = l
        
    def delete_pointset(self, identity):
        # Python! Why no haz remove!!!
        del self._m_pointset[identity]

    def update_graph(self):
        print ("Updating graph")
        self._update_graph()

    def clear(self):
        self._m_plot.clear()
        self._m_pointset.clear()
        self.draw()

    def reapply_options(self):
        print "_m_canvas_options = ", str(self._m_canvas_options)
        self._m_canvas_options.plot_with(self._m_pointset, self._m_plot)

    def export_to_file(self, filename):
        self.figure.savefig(filename)

    def _update_graph(self):
        self._m_plot.clear()
        self._m_pointset_table = {}
        print "Reapply options"

        # for now, plot everything on the same axis
        for (points, plotter) in self._m_pointset.values():
            self._m_pointset_table[points.get_variable_name()] = points
            plotter.plot_with(points, self._m_plot)

        self.reapply_options()

        self.draw()


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

class NoneFormat:
    def draw(self, _gc, _w, _h):
        return

    def getMatFormat(self):
        return None # indicates no pointst

class StyleButton(wx.combo.BitmapComboBox):
    def __init__(self, color, *args, **kwargs):
        self.m_formats = [SquareFormat(), CircleFormat(), NoneFormat()]
        self.m_color = (0,0,0)
        wx.combo.BitmapComboBox.__init__(self, *args, style=wx.CB_READONLY, **kwargs)
        self.SetMinSize( (64,35) )

        self.paint()

    def setColor(self, color):
        self.m_color = color;
        self.Clear()

    def paint(self):
        w, h = self.GetSize()
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
        self.interp = None
        self.m_button.Bind(wx.EVT_COMBOBOX, self.on_combo)

    def set_interp(self, interp):
        self.interp = interp

    def set_color(self, color):
        self.Update()

    def on_combo(self, x):
        self.GetParent().Update()

    def _get_selected_fmt(self):
        return self.m_button.m_formats[self.m_button.GetSelection()]

    def get_selected_fmt(self):
        return self._get_selected_fmt().getMatFormat()

    def get_interp_strategy(self):
        return self.interp.get_selected()
        
class StyleFrame(FrameWrappedPanel):
    def __init__(self):
        super(StyleFrame, self).__init__()
        self._m_panel = StylePanel(self)

    def get_panel(self):
        return self._m_panel

class TestTransientPopup(wx.PopupTransientWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style):
        wx.PopupTransientWindow.__init__(self, parent, style)
        self.Layout()

    def set_panel(self, panel):
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)
        
        self.SetSizerAndFit(sizer)


class StylePanel(wx.Panel):
    def __init__(self, names, computation_plans, *args, **kwargs):
        super(StylePanel, self).__init__(*args, **kwargs)
        sizer = wx.GridBagSizer(len(names), 2)
        self.m_lst = []
        self.change_listener = None
        self._m_computation_plans = computation_plans

        row = 1
        fmt_lst = [CircleFormat(), SquareFormat()]
        color_lst = [(180, 100, 100), (100, 180, 100), (100, 100, 180), 
                 (180, 180, 100) ]

        sizer.Add(wx.StaticText(self, -1, "Enabled"), (0, 0))
        sizer.Add(wx.StaticText(self, -1, "Color"), (0, 2))
        sizer.Add(wx.StaticText(self, -1, "Style"), (0, 3))
        sizer.Add(wx.StaticText(self, -1, "Interpolation"), (0, 4))

        for n in names:
            picker = wx.ColourPickerCtrl(self, wx.ID_ANY);
            picker.SetColour(color_lst[row % len(color_lst)])
            checkbox = wx.CheckBox(self, wx.ID_ANY, n)
            tmp = StylePanelSubSection(fmt_lst[row % len(fmt_lst)],
                                       color_lst[row % len(color_lst)], self )

            interp = CalChoice(self, [
                  ("Linear", LinearInterpolationStrategy())
                , ("Cubic", SciInterpolationStrategy('cubic'))
                , ("Quadratic", SciInterpolationStrategy('quadratic'))
                , ("No Line", None) # None indicates no line.
                ])
            tmp.set_interp(interp)

            (cplan_check, fn) = self.transient_bind_closure()
            self.m_lst.append( (n, checkbox, tmp, picker, cplan_check) )

            sizer.Add(checkbox, (row, 0))
            sizer.Add(picker, (row, 2))
            sizer.Add(tmp, (row, 3))
            sizer.Add(interp, (row, 4))

            computation_plan_button = wx.Button(self, wx.ID_ANY, "Computation Plan")

            self.Bind(wx.EVT_BUTTON, fn, computation_plan_button)
            sizer.Add(computation_plan_button, (row, 5))

            row += 1

        # btn = wx.Button(self, label="OK");
        # sizer.Add(btn, (row, 0))
        # btn.Bind( wx.EVT_BUTTON, self.on_change )

        sizer.AddGrowableCol( 1 )

        self.SetSizer(sizer)
        self.SetSize((300,500))

    def on_change(self, _):
        if self.change_listener is not None:
            self.change_listener(self.get_variables_and_options())

    def add_change_listener(self, f):
        self.change_listener = f
    
    def transient_bind_closure(self):
        win = TestTransientPopup(self, wx.SIMPLE_BORDER)
        panel = CalCheckboxPanel( zip(self._m_computation_plans, self._m_computation_plans), win, style=wx.SUNKEN_BORDER)
        win.set_panel(panel)
        
        def return_function(evt):
            btn = evt.GetEventObject()
            pos = btn.ClientToScreen((0,0))
            sz = btn.GetSize()
            win.Position(pos, (0, sz[1]))
            win.Popup()

        return (panel, return_function)

    def OnShowPopupTransient(self, evt):
        win = TestTransientPopup(self, wx.SIMPLE_BORDER, self._m_computation_plans)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen( (0,0) )
        sz =  btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()

    def get_variables_and_options(self):
        ret = []

        for (name, box, style_panel, colorpicker, check_panel) in self.m_lst:
            for cplan in check_panel.get_selected():
                
                if box.GetValue():
                    opts = PlotOptions()
                    opts.color = colorpicker.GetColour()
                    opts.fmt = style_panel.get_selected_fmt()
                    opts.interpolation_strategy = style_panel.get_interp_strategy()
                    opts.computation_plan = cplan
                    ret.append( (name, opts) )

        return ret

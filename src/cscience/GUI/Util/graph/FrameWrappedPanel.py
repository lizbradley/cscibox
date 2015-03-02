import wx
import wx.lib.scrolledpanel as scrolled

# Creates a frame that wraps a panel in a scroll panel 
# and also provides a button bar at the bottom
class FrameWrappedPanel(wx.Frame):
    
    def __init__(self):
        super(FrameWrappedPanel, self).__init__(parent=None)

        self._m_outer_panel = wx.Panel(parent=self)
        self._m_scroll_panel = scrolled.ScrolledPanel(self._m_outer_panel)
        self._m_button_bar_panel = wx.Panel(parent=self._m_outer_panel)



        self._m_ok_button = wx.Button(self._m_button_bar_panel, label="OK")
        self._m_cancel_button = wx.Button(self._m_button_bar_panel, label="OK")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._m_ok_button)
        sizer.Add(self._m_cancel_button)
        self._m_button_bar_panel.SetSizerAndFit(sizer)

        sizer = wx.GridBagSizer()
        sizer.Add(self._m_scroll_panel, (0,0), (1,1), wx.EXPAND)
        sizer.Add(self._m_button_bar_panel, (1,0), (1,1), wx.EXPAND)
        sizer.AddGrowableRow(0)
        self._m_scroll_panel.SetupScrolling()
        self._m_outer_panel.SetSizerAndFit(sizer)

    def get_panel(self):    
        return self._m_scroll_panel

    def set_panel(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)

        self._m_scroll_panel.SetSizerAndFit(sizer)

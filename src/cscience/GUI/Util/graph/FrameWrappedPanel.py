import wx
import wx.lib.scrolledpanel as scrolled

# Creates a frame that wraps a panel in a scroll panel 
# and also provides a button bar at the bottom
class FrameWrappedPanel(wx.Frame):
    
    def __init__(self):
        super(FrameWrappedPanel, self).__init__(parent=None)

        self._m_scroll_panel = scrolled.ScrolledPanel(self)
        self._m_button_bar_panel = wx.Panel(parent=self)

        self._m_ok_button = wx.Button(self._m_button_bar_panel, label="OK")
        self._m_cancel_button = wx.Button(self._m_button_bar_panel, label="Cancel")
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
        self._m_cancel_button.Bind(wx.EVT_BUTTON, self.__on_cancel)

    def set_ok_listener(self, listener):
        self._m_ok_listener = listener

    def __on_ok(self, _):
        self.Hide()
        if self._m_ok_listener is not None:
            self._m_ok_listener()

    def __on_cancel(self, _):
        self.Hide()

    def get_panel(self):    
        return self._m_scroll_panel

    def set_panel(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)

        self._m_scroll_panel.SetSizerAndFit(sizer)

import wx

from wx.lib.agw import aui
from wx.lib.agw import foldpanelbar as fpb

from cscience.GUI.Util.CalWidgets import CalCollapsiblePane, \
                                         CalCheckboxPanel, \
                                         CalRadioButtonGroup, \
                                         CalListBox

class OptionsPane(wx.Panel): # {
    def __build_display_panel(self):

        # Display fold panel
        box = wx.StaticBox(self, wx.ID_ANY, "Display")
        widget = CalCheckboxPanel(
                             [ ("Show Axes Labels", 0)
                             , ("Show Legend",      1)
                             , ("Show Grid",        2)
                             , ("Graphs Stacked",   3)
                             , ("Invert X Axis",    4)
                             , ("Invert Y Axis",    5)
                             ], box)
        self.sizer.Add(box, (0,0))
        return widget

    def __build_cplan_panel(self, selected):
        box = wx.StaticBox(self, wx.ID_ANY, "Computation Plans")
        cplans = zip(selected, range(len(selected)))
        widget = CalListBox(cplans, box)
        self.sizer.Add(box, (1,0))
        return widget


        
    # OptionsPane()
    def __init__(self, parent, selected_cplans):
        super(OptionsPane,self).__init__(parent)

        self.sizer = wx.GridBagSizer(5, 5)
        self.display_panel = self.__build_display_panel()
        self.cplan_panel = self.__build_cplan_panel(selected_cplans)
        self.SetSizerAndFit(self.sizer)


        # item = fold_panel.AddFoldPanel("Computation Plans", collapsed=False, cbstyle=cs)
        # cplans = zip(selected_cplans, range(len(selected_cplans)))
        # widget = CalListBox(cplans, item)
        # fold_panel.AddFoldPanelWindow(item, widget)
# }

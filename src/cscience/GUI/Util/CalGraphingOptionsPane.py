import wx

from wx.lib.agw import aui
from wx.lib.agw import foldpanelbar as fpb

from cscience.GUI.Util.CalWidgets import CalCollapsiblePane, \
                                         CalCheckboxPanel, \
                                         CalRadioButtonGroup, \
                                         CalListBox

class OptionsPane(CalCollapsiblePane): # {
    def __build_display_panel(self, fold_panel, cs):

        # Display fold panel
        item = fold_panel.AddFoldPanel("Display", collapsed=False, cbstyle=cs)
        widget = CalCheckboxPanel(
                             [ ("Show Axes Labels", 0)
                             , ("Show Legend",      1)
                             , ("Show Grid",        2)
                             , ("Graphs Stacked",   3)
                             , ("Invert X Axis",    4)
                             , ("Invert Y Axis",    5)
                             ], item)
        fold_panel.AddFoldPanelWindow(item, widget)
        return widget

    def __build_error_panel(self, fold_panel):
        # Error fold panel
        item = fold_panel.AddFoldPanel("Error", collapsed=False)
        widget = CalRadioButtonGroup(
                    [  ('None',       False)
                     , ('Error Bars', True)
                     ], item)
        fold_panel.AddFoldPanelWindow(item, widget)
        return widget

    def create_plot_mutators(self):
        display_selections = self.display_panel.get_selected()
        error_bars_enabled = self.error_panel.get_selection()

        show_axes_labels = 0 in display_selections
        show_legend = 1 in display_selections
        show_grid = 2 in display_selections

        def f_show_legend(plot):
            plot.plotting_options.show_legend = show_legend
        def f_show_grid(plot):
            plot.plotting_options.show_grid = show_grid
        def f_enable_error_bars(plot):
            plot.errorbar_options.enabled = error_bars_enabled
        def f_show_labels(plot):
            plot.label_options.x_label_visible = show_axes_labels
            plot.label_options.y_label_visible = show_axes_labels
            

        return [ f_show_legend,
                 f_show_grid,
                 f_enable_error_bars,
                 f_show_labels ]
        
    # def __build_interpolation_panel(self, 
        
        
    # OptionsPane()
    def __init__(self, parent, selected_cplans):
        CalCollapsiblePane.__init__(self, parent)
        fold_panel = fpb.FoldPanelBar(self.GetPane(), wx.ID_ANY, size=(150, -1),
                                      agwStyle=fpb.FPB_VERTICAL, pos=(-1, -1))
        cs = fpb.CaptionBarStyle()
        base_color = aui.aui_utilities.GetBaseColour()
        cs.SetFirstColour(aui.aui_utilities.StepColour(base_color, 180))
        cs.SetSecondColour(aui.aui_utilities.StepColour(base_color, 85))

        self.error_panel = self.__build_error_panel(fold_panel)
        self.display_panel = self.__build_display_panel(fold_panel, cs)


        item = fold_panel.AddFoldPanel("Interpolation", collapsed=False, cbstyle=cs)
        widget = CalRadioButtonGroup([ ("None",   0)
                                     , ("Linear", 1)
                                     , ("Cubic",  2)
                                     ], item)
        fold_panel.AddFoldPanelWindow(item, widget)

        item = fold_panel.AddFoldPanel("Computation Plans", collapsed=False, cbstyle=cs)
        cplans = zip(selected_cplans, range(len(selected_cplans)))
        widget = CalListBox(cplans, item)
        fold_panel.AddFoldPanelWindow(item, widget)

        sizer = wx.GridSizer(1, 1)
        sizer.Add(fold_panel, 1, wx.EXPAND)
        self.GetPane().SetSizerAndFit(sizer)
# }

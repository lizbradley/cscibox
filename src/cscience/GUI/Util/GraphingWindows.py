"""
Graphing.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import wx

from wx.lib.agw import aui
from wx.lib.agw import foldpanelbar as fpb

from cscience import datastore
from cscience.GUI import icons

from cscience.GUI.Util.Graphing import Plotter, PlotPoint, PlotCanvas

from cscience.GUI.Util.CalWidgets import CalCollapsiblePane, \
                                         CalCheckboxPanel, \
                                         CalRadioButtonGroup, \
                                         CalChoice, \
                                         CalListBox

class PlotWindow(wx.Frame):

    ''' Class which is a toolbar specific to the
    PlotWindow '''
    class Toolbar(aui.AuiToolBar): # {
        def __init__(self, parent, indattrs):
            aui.AuiToolBar.__init__(self, parent, wx.ID_ANY,
                                      agwStyle=aui.AUI_TB_HORZ_TEXT)
            self.icons = self.setup_art()
            
            # Checkbox's to tell which axis should be on the
            # bottom. {
            text = "Independent Axis:"
            self.AddLabel(wx.ID_ANY, text, width=self.GetTextExtent(text)[0])
        
            l_id = wx.NewId()
            self.AddRadioTool(l_id, '',
                              self.icons['y_axis'], 
                              self.icons['y_axis'])
    
            l_id = wx.NewId()
            self.AddRadioTool(l_id, '',
                              self.icons['x_axis'], 
                              self.icons['x_axis'])
            # }

            # The different choices for the data to plot {
            choice_arr = [(i,None) for i in indattrs]
            choice_dict = dict(choice_arr)
            invar_choice = CalChoice(self, choice_dict) 
            self.AddControl(invar_choice)

            choice_dict = dict(choice_arr + [('<Multiple>','')])
            depvar_choice = CalChoice(self, choice_dict) 
            self.AddControl(depvar_choice)
            # }

            self.AddStretchSpacer()
            self.AddSeparator()

            options_button_id = wx.NewId()
 
            self.AddSimpleTool(options_button_id, "", self.icons['graphing_options'])

            self.Realize()
            self.options_pressed_listeners = []
            self.Bind(wx.EVT_TOOL, self.__on_options_pressed, id=options_button_id)

        def on_invar_changed_do( self, func ):
            pass

        def on_options_pressed_do( self, func ):
            # do something when the options button is pressed 
            self.options_pressed_listeners.append( func )

        def __on_options_pressed(self, _):
            for f in self.options_pressed_listeners: f()

        def setup_art(self):
            # Setup the dictionary of artwork for easier and
            # more terse access to the database of icons
            art = [
                  ("radio_on",icons.ART_RADIO_ON)
                , ("radio_off", icons.ART_RADIO_OFF)
                , ("graphing_options", icons.ART_GRAPHING_OPTIONS)
                , ("x_axis", icons.ART_X_AXIS)
                , ("y_axis", icons.ART_Y_AXIS)
                ]
    
            art_dic = {}
            for (name, loc) in art:
                art_dic[name] = wx.ArtProvider.GetBitmap(
                    loc, wx.ART_TOOLBAR, (16, 16))
            return art_dic
    # }

    class OptionsPane(CalCollapsiblePane): # {
        def __build_display_panel(self, fold_panel, cs):

            # Display fold panel
            item = fold_panel.AddFoldPanel("Display", collapsed=False, cbstyle=cs)
            widget = CalCheckboxPanel(
                                [  ("Show Axes Labels", 0)
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
    
    def __init__(self, parent, samples):
        start_pos = parent.GetPosition()
        start_pos.x += 50
        start_pos.y += 100
        # initialize the window as a frame
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'],
                                         pos=start_pos)

        # choices in the first combo box
        independent_choices = [
            i.name for i in datastore.sample_attributes
                   if i.is_numeric() and i in parent.view ]

        # layout for the window
        sizer = wx.GridBagSizer()

        _m_options_pane = self.build_options_pane(self, samples)

        # Create the toolbar and hook it up so that when the options
        # button is pressed, the options pane is toggled
        _m_toolbar = self.build_toolbar(self, independent_choices,
                lambda: _m_options_pane.Collapse( not _m_options_pane.IsCollapsed() )
            )

        sizer.Add(_m_toolbar, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND)

        self._m_plot_canvas = self.build_plot(self)
        sizer.Add(self._m_plot_canvas, wx.GBPosition(1, 0),
                    wx.GBSpan(1, 1), wx.EXPAND)
        # This is just for testing {
        self._m_plot_canvas.add_pointset(0, [PlotPoint(i,i**2,0,0) for i in range(0,10)], Plotter()) 
        self._m_plot_canvas.update_graph()
        # }

        sizer.Add(_m_options_pane,
                    wx.GBPosition(0, 1), wx.GBSpan(2, 1), wx.EXPAND)

        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableRow(1, 0)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def build_options_pane(self, parent, samples):
        selected = [sample['computation plan'] 
                        for sample in samples]
        ret = PlotWindow.OptionsPane(self, list(set(selected))) ;
        ret.Expand()
        return ret
    
    def build_plot(self, parent):
        ret = PlotCanvas(parent)
        return ret;

    def build_toolbar(self, parent, independent_choice, whattodo):
        # The toolbar for the window
        ret = PlotWindow.Toolbar(parent, independent_choice)
        ret.on_options_pressed_do(whattodo)
        return ret
            
        



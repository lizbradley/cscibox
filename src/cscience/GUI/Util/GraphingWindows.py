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
from wx.lib.agw import pycollapsiblepane as pcp

from cscience import datastore
from cscience.GUI import icons, events
from cscience.GUI.Util import PlotOptions, PlotCanvas

class PlotWindow(wx.Frame):
    
    option_elements = {
                  'no_error' : {'text' : 'None', 
                                'options_id' : PlotOptions.ERROR_NONE},
                  'bar_error' : {'text' : 'Error Bars', 
                                'options_id' : PlotOptions.ERROR_BARS},
                  'violin_error' : {'text' : 'Violin Plot', 
                                'options_id' : PlotOptions.ERROR_VIOLIN},
                  'toggle_axes_labels' : {'text' : 'Show Axes Labels', 
                                'options_id' : 'show_axes_labels'},
                  'toggle_legend' : {'text' : 'Show Legend', 
                                'options_id' : 'show_legend'},
                  'toggle_grid' : {'text' : 'Show Grid', 'options_id' : 'show_grid'},
                  'stacked' : {'text' : 'Graphs Stacked', 'options_id' : 'stacked'},
                  'no_interp' : {'text' : 'None', 'options_id' : PlotOptions.INTERP_NONE},
                  'linear_interp' : {'text' : 'Linear', 'options_id' : PlotOptions.INTERP_LINEAR},
                  'cubic_interp' : {'text' : 'Cubic', 'options_id' : PlotOptions.INTERP_CUBIC},
                  }
    
    error_element_names = ('no_error', 'bar_error', 'violin_error')
    display_element_names = ('toggle_axes_labels', 'toggle_legend',
                        'toggle_grid', 'stacked')
    interp_element_names = ('no_interp', 'linear_interp', 'cubic_interp')
    
    def __init__(self, parent, samples):
        start_position = parent.GetPosition()
        start_position.x += 50
        start_position.y += 100
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'],
                                         pos=start_position)
        self.numericatts = [att.name for att in datastore.sample_attributes if 
                                    (att.type_ in ('integer', 'float') and \
                                     att in parent.view)]
        self.var_choice_atts = [att.name for att in datastore.sample_attributes if 
                                    (att.type_ in ('integer', 'float') and \
                                    att in parent.view)]
        self.var_choice_atts.append("<Multiple>")
        self.selected_cplans = list(set([sample['computation plan'] for sample in samples]))
        self.parent = parent
        
        sizer = wx.GridBagSizer()
        
        self.toolbar = self.create_toolbar(self)
        sizer.Add(self.toolbar,wx.GBPosition(0,0),wx.GBSpan(1,1),wx.EXPAND)
        
        self.plot_canvas = PlotCanvas(self, samples, self.get_options())
        sizer.Add(self.plot_canvas,wx.GBPosition(1,0),wx.GBSpan(1,1),wx.EXPAND)
        
#         self.options_pane = CalOptionsPane(self)
        self.options_pane = self.create_options_pane()
        sizer.Add(self.options_pane, wx.GBPosition(0,1),wx.GBSpan(2,1), wx.EXPAND)
        
        sizer.AddGrowableCol(0,1)
        sizer.AddGrowableCol(1,0)
        sizer.AddGrowableRow(0,0)
        sizer.AddGrowableRow(1,1)
        
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    #TODO add a little bit more vertical space after the last item in a panel
    #TODO figure out why it doesn't start at the very top.
    def create_options_pane(self):
        
        cp = CalCollapsiblePane(self)
        
        #For some reason, letting the window manager set the width doesn't work.
        #So we set the width manually with size=(150,-1)
        bar = fpb.FoldPanelBar(cp.GetPane(), wx.ID_ANY, size=(150, -1),
                               agwStyle=fpb.FPB_VERTICAL, pos=(-1,-1))
        
        cs = fpb.CaptionBarStyle()
        base_colour = aui.aui_utilities.GetBaseColour()
        cs.SetFirstColour(aui.aui_utilities.StepColour(base_colour, 180))
        cs.SetSecondColour(aui.aui_utilities.StepColour(base_colour, 85))
#         cs.SetCaptionStyle(fpb.CAPTIONBAR_SINGLE)
#         cs.SetFirstColour(wx.WHITE)
        
        item = bar.AddFoldPanel("Error", collapsed=False, cbstyle=cs)
        for name in self.error_element_names:
            element = self.option_elements[name]
            element['control'] = wx.RadioButton(item, wx.ID_ANY, 
                                                element['text'])
            element['control'].SetValue(PlotOptions.defaults['error_display'] == element['options_id'])
            element['control'].Bind(wx.EVT_RADIOBUTTON, self.OnOptionsChanged)
            bar.AddFoldPanelWindow(item, element['control'], fpb.FPB_ALIGN_LEFT,
                                    leftSpacing=10)
        
        item = bar.AddFoldPanel("Display", collapsed=False, cbstyle=cs)
        for name in self.display_element_names:
            element = self.option_elements[name]
            element['control'] = wx.CheckBox(item, wx.ID_ANY, 
                                                element['text'])
            element['control'].SetValue(PlotOptions.defaults[element['options_id']])
            element['control'].Bind(wx.EVT_CHECKBOX, self.OnOptionsChanged)
            bar.AddFoldPanelWindow(item, element['control'], fpb.FPB_ALIGN_LEFT,
                                    leftSpacing=10)
            
        item = bar.AddFoldPanel("Interpolation", collapsed=False, cbstyle=cs)
        for name in self.interp_element_names:
            element = self.option_elements[name]
            element['control'] = wx.RadioButton(item, wx.ID_ANY,
                                                element['text'])
            element['control'].SetValue(PlotOptions.defaults['interpolation'] == element['options_id'])
            element['control'].Bind(wx.EVT_RADIOBUTTON, self.OnOptionsChanged)
            bar.AddFoldPanelWindow(item, element['control'], fpb.FPB_ALIGN_LEFT,
                                    leftSpacing=10)
            
        item = bar.AddFoldPanel("Computation Plans", collapsed=False, cbstyle=cs)
        self.cplanListBox = wx.ListBox(item, wx.ID_ANY, choices=self.selected_cplans, style=wx.LB_MULTIPLE | wx.LB_NEEDED_SB)
        for i in range(len(self.selected_cplans)):
            self.cplanListBox.Select(i)
        self.cplanListBox.Bind(wx.EVT_LISTBOX, self.OnCplanSelectionsChanged)
        bar.AddFoldPanelWindow(item, self.cplanListBox, fpb.FPB_ALIGN_LEFT, leftSpacing=10)
        
        
        sizer = wx.GridSizer(1,1)
        sizer.Add(bar,1,wx.EXPAND)
        cp.GetPane().SetSizer(sizer)
        
        return cp

    def create_toolbar(self, parent):
        
        radio_on_bmp = wx.ArtProvider.GetBitmap(icons.ART_RADIO_ON,wx.ART_TOOLBAR,(16,16))
        radio_off_bmp = wx.ArtProvider.GetBitmap(icons.ART_RADIO_OFF,wx.ART_TOOLBAR,(16,16))
        cog_bmp = wx.ArtProvider.GetBitmap(icons.ART_GRAPHING_OPTIONS,wx.ART_TOOLBAR,(16,16))
        
        tb = aui.AuiToolBar(parent, wx.ID_ANY,
                                      agwStyle=aui.AUI_TB_HORZ_TEXT)

        tb.AddLabel(wx.ID_ANY,"Invariant Axis:",width=tb.GetTextExtent("InvariantAxis:")[0])
        
        self.x_radio_id = wx.NewId()
        tb.AddRadioTool(self.x_radio_id, '',
                wx.ArtProvider.GetBitmap(icons.ART_X_AXIS, wx.ART_TOOLBAR, (16, 16)),
                wx.ArtProvider.GetBitmap(icons.ART_X_AXIS, wx.ART_TOOLBAR, (16, 16)))
        tb.ToggleTool(self.x_radio_id,True)
        self.y_radio_id = wx.NewId()
        tb.AddRadioTool(self.y_radio_id, '',
                wx.ArtProvider.GetBitmap(icons.ART_Y_AXIS, wx.ART_TOOLBAR, (16, 16)),
                wx.ArtProvider.GetBitmap(icons.ART_Y_AXIS, wx.ART_TOOLBAR, (16, 16)))

        tb.AddSeparator()

        self.invar_choice_id = wx.NewId()
        self.invar_choice = wx.Choice(tb, self.invar_choice_id, 
                                      choices=self.numericatts)
        self.invar_choice.SetStringSelection(PlotOptions.defaults['invaratt'])
        tb.AddControl(self.invar_choice)
        
        self.var_choice_id = wx.NewId()
        self.var_choice = wx.Choice(tb, self.var_choice_id, 
                                choices=self.var_choice_atts)
        self.var_choice.SetStringSelection(PlotOptions.defaults['varatts'][0])
        self.var_selection = [ self.var_choice.GetStringSelection() ] 
        self.last_var_selection = self.var_selection
        tb.AddControl(self.var_choice)
        
        tb.AddStretchSpacer()
        
        self.options_button_id = wx.NewId()
        tb.AddSimpleTool(self.options_button_id, "", cog_bmp)
        
        self.Bind(wx.EVT_TOOL, self.OnOptionsChanged, id=self.x_radio_id)
        self.Bind(wx.EVT_TOOL, self.OnOptionsChanged, id=self.y_radio_id)
        self.Bind(wx.EVT_CHOICE, self.OnOptionsChanged, 
                  id=self.invar_choice_id)
        self.Bind(wx.EVT_CHOICE, self.OnVariantChanged, id=self.var_choice_id)
        self.Bind(wx.EVT_TOOL, self.OnOptionsPressed, id=self.options_button_id)
                
        tb.Realize()
        return tb
        
    def OnOptionsPressed(self, event):
        if self.options_pane.IsExpanded():
            self.options_pane.Collapse()
        else:
            self.options_pane.Expand()
        
    def OnOptionsChanged(self, event):
        # TODO: Implement it!
        if self.option_elements['violin_error']['control'].GetValue():
            wx.MessageBox('Option not yet implemented.','Error', 
                          wx.ICON_ERROR)
            self.option_elements['no_error']['control'].SetValue(True)
        
        self.plot_canvas.update_graph(self.get_options())
        
    def OnCplanSelectionsChanged(self, event):
        strings = self.cplanListBox.GetStrings()
        self.selected_cplans = [strings[i] for i in self.cplanListBox.GetSelections()]
        self.OnOptionsChanged(event)
        
    def OnVariantChanged(self, event):
        if event.GetId() is not self.var_choice_id:
            print("Error: unexpected event source.")
            return
        
        if self.var_choice.GetStringSelection() != "<Multiple>":
            self.var_selection = [self.var_choice.GetStringSelection()]
        else:
            dlg = wx.MultiChoiceDialog( self, 
                    "Select multiple attributes to plot on the variant axis.",
                    "Multiple Variant Selection", self.numericatts)
            if (dlg.ShowModal() == wx.ID_OK and len(dlg.GetSelections()) > 0):
                self.var_selection = [self.numericatts[i] 
                                      for i in dlg.GetSelections()]
            else:
                self.var_selection = self.last_var_selection
            dlg.Destroy()
            if len(self.var_selection) is 1:
                self.var_choice.SetStringSelection(self.var_selection[0])
        self.last_var_selection = self.var_selection
        self.OnOptionsChanged(event)
        
    def get_options(self):
        options = {}
        options['invaratt'] = self.invar_choice.GetStringSelection()
        options['varatts'] = self.var_selection
        options['invaraxis'] = 'x' if self.toolbar.GetToolToggled(self.x_radio_id) else 'y'
        options['selected_cplans'] = self.selected_cplans
                                    
        for name in self.error_element_names:
            element = self.option_elements[name]
            #If we haven't actually built the options pane yet, then 'control'
            #won't be in element, and we should just start with the defaults.
            try:
                control = element['control']
            except KeyError:
                break
            else:
                if control:
                    if control.GetValue():
                        options['error_display'] = element['options_id']
                        break
        
        for name in self.display_element_names:
            element = self.option_elements[name]
            #If we haven't actually built the options pane yet, then 'control'
            #won't be in element, and we should just start with the defaults.
            try:
                control = element['control']
            except KeyError:
                break
            else:
                if element['control']:
                    options[element['options_id']] = element['control'].GetValue()

        for name in self.interp_element_names:
            element = self.option_elements[name]
            #If we haven't actually built the options pane yet, then 'control'
            #won't be in element, and we should just start with the defaults.
            try:
                control = element['control']
            except KeyError:
                break
            else:
                if control:
                    if control.GetValue():
                        options['interpolation'] = element['options_id']
                        break

        return PlotOptions(**options)
    
    
"""We want the pane to be invisible when collapsed, so we have to make some 
minor modifications to PyCollapsiblePane
I'm stealing and throwing out a lot of what this class does. Might be good to
look in to exactly what of it we're using and maybe just write our own class if
it would be smaller than the below.
"""
class CalCollapsiblePane(pcp.PyCollapsiblePane):
    
    #Copied code below from wx source so I could make a few modifications.
    #Fixing the bug of the small extra space above the bar. Essentially, I've
    #taken over the AGW flag CP_GTK_EXPANDER to mean no expander at all.
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, agwStyle=wx.CP_DEFAULT_STYLE | 
                 wx.CP_GTK_EXPANDER, validator=wx.DefaultValidator, 
                 name="PyCollapsiblePane"):
        """
        Default class constructor.

        :param `parent`: the L{PyCollapsiblePane} parent. Must not be ``None``;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `label`: The initial label shown in the button which allows the
         user to expand or collapse the pane window.
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `style`: the underlying `wx.PyPanel` window style;
        :param `agwStyle`: the AGW-specifi window style. This can be a combination of the
         following bits:

         ==================== =========== ==================================================
         Window Styles        Hex Value   Description
         ==================== =========== ==================================================
         ``CP_NO_TLW_RESIZE``         0x2 By default L{PyCollapsiblePane} resizes the top level window containing it when its own size changes. This allows to easily implement dialogs containing an optionally shown part, for example, and so is the default behaviour but can be inconvenient in some specific cases -- use this flag to disable this automatic parent resizing then.
         ``CP_GTK_EXPANDER``          0x4 Uses a GTK expander instead of a button.
         ``CP_USE_STATICBOX``         0x8 Uses a `wx.StaticBox` around L{PyCollapsiblePane}.
         ``CP_LINE_ABOVE``           0x10 Draws a line above L{PyCollapsiblePane}.
         ==================== =========== ==================================================

        :param `validator`: the validator associated to the L{PyCollapsiblePane};
        :param `name`: the widget name.
        
        """
                
        wx.PyPanel.__init__(self, parent, id, pos, size, style, name)
        
        self._pButton = self._pStaticLine = self._pPane = self._sz = None            
        self._strLabel = label
        self._bCollapsed = True
        self._agwStyle = agwStyle

        self._pPane = wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        self._pPane.Hide()

        self._pButton = wx.Button(self)
        self._pButton.Hide()
        self._sz = wx.BoxSizer(wx.HORIZONTAL)
        self.SetExpanderDimensions(0, 0)
            
        self.Bind(wx.EVT_SIZE, self.OnSize)
        if self.IsExpanded():
            self.expanded_width = self.GetSize().width
    
    """Overriding PyCollapsiblePane's DoGetBestSize()"""
    def DoGetBestSize(self):
        if self.IsExpanded():
            return super(CalCollapsiblePane, self).DoGetBestSize()
        else:
            return wx.Size(0,0)
        
    #Below copied from wxPython source exactly, then modified to fix the bug where
    #collapsing the options pane resized the window
    def OnStateChange(self, sz):
        """
        Handles the status changes (collapsing/expanding).

        :param `sz`: an instance of `wx.Size`.
        """
        # minimal size has priority over the best size so set here our min size
        self.SetMinSize(sz)
        self.SetSize(sz)
        if self.IsExpanded():
            self.expanded_width = self.GetSize().width

        if self.HasAGWFlag(wx.CP_NO_TLW_RESIZE):
            # the user asked to explicitely handle the resizing itself...
            return
        
        # NB: the following block of code has been accurately designed to
        #     as much flicker-free as possible be careful when modifying it!

        top = wx.GetTopLevelParent(self)
        if top:
            # NB: don't Layout() the 'top' window as its size has not been correctly
            #     updated yet and we don't want to do an initial Layout() with the old
            #     size immediately followed by a SetClientSize/Fit call for the new
            #     size that would provoke flickering!

            # we shouldn't attempt to resize a maximized window, whatever happens
            if not top.IsMaximized():
                
                cur_size = top.GetSize()
                if self.IsCollapsed(): # expanded -> collapsed transition
                   cur_size.width -= self.expanded_width
                else: #collapsed -> expanded transition
                    cur_size.width += self.GetSize().width
                top.SetSize(cur_size)

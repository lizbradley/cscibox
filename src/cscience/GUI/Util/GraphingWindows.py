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
from cscience.GUI.Util.CalWidgets import CalChoice
            

class PlotWindow(wx.Frame):

    class Toolbar(aui.AuiToolBar): # {
        def __init__(self, parent, indattrs):
            aui.AuiToolBar.__init__(self, parent, wx.ID_ANY,
                                      agwStyle=aui.AUI_TB_HORZ_TEXT)
            self.icons = self.setup_art()
            
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

            choice_arr = [(i,None) for i in indattrs]
            choice_dict = dict(choice_arr)
            invar_choice = CalChoice(self, choice_dict) 
            self.AddControl(invar_choice)

            choice_dict = dict(choice_arr + [('<Multiple>','')])
            depvar_choice = CalChoice(self, choice_dict) 
            self.AddControl(depvar_choice)

            self.AddSeparator()
            self.Realize()

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
    
    def __init__( self, parent, samples ):
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

        sizer = wx.GridBagSizer()
        sizer.Add(self.build_toolbar(self, independent_choices ),
                    wx.GBPosition(0,0), wx.GBSpan(1,1), wx.EXPAND)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def build_toolbar(self, parent, independent_choice ):
        return PlotWindow.Toolbar(parent, independent_choice)
            
        


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

    def DoGetBestSize(self):
        """Overriding PyCollapsiblePane's DoGetBestSize()"""
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

"""
grid.py

* Copyright (c) 2012-2015, University of Colorado.
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
from wx.lib.agw import ribbon

class RibbonPanelSizer(ribbon.RibbonPanel):
    """
    Semitrivial patch of RibbonPanel to allow it to use sizers, at least in some
    cases, fairly easily.
    """
    
    def Layout(self):

        if self.IsMinimised():
            # Children are all invisible when minimised
            return True
        elif self.Sizer:
            self.Sizer.Layout()
            dc = wx.ClientDC(self)
            size, position = self._art.GetPanelClientSize(dc, self, wx.Size(*self.GetSize()), wx.Point())
            self.Sizer.SetDimension(position.x, position.y, size.GetWidth(), size.GetHeight())
            # Delegate to sizer whenever there is one.
            return True
        else:
            return super(RibbonPanelSizer, self).Layout()
        
        
    def ShowExpanded(self):
        #(Copied from original RibbonPanel to insert changes in the middle)...
        """
        Show the panel externally expanded.

        When a panel is minimised, it can be shown full-size in a pop-out window, which
        is referred to as being (externally) expanded.

        :returns: ``True`` if the panel was expanded, ``False`` if it was not (possibly
         due to it not being minimised, or already being expanded).

        :note: When a panel is expanded, there exist two panels - the original panel
         (which is referred to as the dummy panel) and the expanded panel. The original
         is termed a dummy as it sits in the ribbon bar doing nothing, while the expanded
         panel holds the panel children.
         
        :see: L{HideExpanded}, L{GetExpandedPanel}
        """

        if not self.IsMinimised():        
            return False
        
        if self._expanded_dummy != None or self._expanded_panel != None:        
            return False

        size = self.GetBestSize()
        pos = self.GetExpandedPosition(wx.RectPS(self.GetScreenPosition(), 
                    self.GetSize()), size, self._preferred_expand_direction).GetTopLeft()

        # Need a top-level frame to contain the expanded panel
        container = wx.Frame(None, wx.ID_ANY, self.GetLabel(), pos, size, 
                             wx.FRAME_NO_TASKBAR | wx.BORDER_NONE)

        self._expanded_panel = ribbon.RibbonPanelSizer(container, wx.ID_ANY, 
                    self.GetLabel(), self._minimised_icon, wx.Point(0, 0), 
                    size, self._flags)
        self._expanded_panel.SetArtProvider(self._art)
        self._expanded_panel._expanded_dummy = self

        # Move all children to the new panel.
        # Conceptually it might be simpler to re-parent self entire panel to the
        # container and create a new panel to sit in its place while expanded.
        # This approach has a problem though - when the panel is reinserted into
        # its original parent, it'll be at a different position in the child list
        # and thus assume a new position.
        # NB: Children iterators not used as behaviour is not well defined
        # when iterating over a container which is being emptied
        
        for child in self.GetChildren(): 
            child.Reparent(self._expanded_panel)
            child.Show()
        
        self._expanded_panel.SetSizer(self.Sizer)
        self._expanded_panel.Realize()
        self.Refresh()
        container.Show()
        self._expanded_panel.SetFocus()

        return True
        
    def HideExpanded(self):
        #Copied for mid-method insert
        """
        Hide the panel's external expansion.

        :returns: ``True`` if the panel was un-expanded, ``False`` if it was not
         (normally due to it not being expanded in the first place).
         
        :see: L{HideExpanded}, L{GetExpandedPanel}
        """

        if self._expanded_dummy == None:        
            if self._expanded_panel:            
                return self._expanded_panel.HideExpanded()
            else:            
                return False
            
        # Move children back to original panel
        # NB: Children iterators not used as behaviour is not well defined
        # when iterating over a container which is being emptied
        for child in self.GetChildren():
            child.Reparent(self._expanded_dummy)
            child.Hide()

        self._expanded_dummy._expanded_panel = None
        self._expanded_dummy.SetSizer(self.Sizer)
        self._expanded_dummy.Realize()
        self._expanded_dummy.Refresh()
        parent = self.GetParent()
        self.Destroy()
        parent.Destroy()

        return True
    
    def GetMinNotMinimisedSize(self):
        if self.Sizer:
            dc = wx.ClientDC(self)
            return self._art.GetPanelSize(dc, self, 
                                        wx.Size(*self.Sizer.GetMinSize()), None)
        return super(RibbonPanelSizer, self).GetMinNotMinimisedSize()
    
    def DoGetBestSize(self):
        if self.Sizer:
            return self.GetMinNotMinimisedSize()
        return super(RibbonPanelSizer, self).DoGetBestSize()
    
    def DoGetNextLargerSize(self, direction, relative_to):
        if self.Sizer:
            return relative_to
        return super(RibbonPanelSizer, self).DoGetNextLargerSize(direction, relative_to)
    
    
    
    
    
    
    
    
    
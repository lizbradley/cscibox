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
import wx.grid
import wx.lib.fancytext
import wx.lib.mixins.gridlabelrenderer as glr
from cscience.GUI import events

class UpdatingTable(wx.grid.PyGridTableBase):
    def __init__(self, grid, *args, **kwargs):
        super(UpdatingTable, self).__init__(*args, **kwargs)
        self.grid = grid
        self.grid.SetTable(self)
    def reset_view(self):
        """Trim/extend the control's rows and update all values"""
        self.grid.BeginBatch()
        for current, new, delmsg, addmsg in (
             (self.grid.GetNumberRows(), self.GetNumberRows(), 
              wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 
              wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
             (self.grid.GetNumberCols(), self.GetNumberCols(), 
              wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, 
              wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED)):
                if new < current:
                    self.grid.ProcessTableMessage(wx.grid.GridTableMessage(
                                    self, delmsg, new, current-new))
                elif new > current:
                    self.grid.ProcessTableMessage(wx.grid.GridTableMessage(
                                    self, addmsg, new-current))
        
        self.grid.ProcessTableMessage(wx.grid.GridTableMessage(
                                self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES))    
       
        self.grid.EndBatch()
        self.grid.AutoSize()
        
        #if the grid is now larger than the enclosing window can show, let's
        # show it for better happiness!
        frame = self.grid.GetParent()
        bw, bh = frame.GetBestSize()
        w, h = frame.GetSize()
        frame.SetSize((max(bw, w), max(bh, h)))
        frame.Layout()        
        
    def IsEmptyCell(self, row, col):
        """Return True if the cell is empty"""
        return False

    def GetTypeName(self, row, col):
        """Return the name of the data type of the value in the cell"""
        return 'string'

class LabelSizedGrid(wx.grid.Grid, glr.GridWithLabelRenderersMixin):
    
    def __init__(self, *args, **kwargs):
        self._selected_rows = set()
        super(LabelSizedGrid, self).__init__(*args, **kwargs)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.SetDefaultRenderer(FancyTextRenderer())
        self.RegisterDataType('string', wx.grid.GridCellStringRenderer(),
                              wx.grid.GridCellAutoWrapStringEditor())
        self.RegisterDataType('boolean', wx.grid.GridCellBoolRenderer(),
                              wx.grid.GridCellBoolEditor())
        
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self)
    
    def AutoSize(self):
        # set row and column label cells to fit cell contents.
        width = max([self.GetTextExtent(self.GetRowLabelValue(i))[0] for i in 
                     range(self.GetNumberRows())])
        width = (width or 30) + 20
        self.SetRowLabelSize(width)
        
        #column names are permitted to be multi-line, which GetTextExtent does
        #not account for. So, we need to count both max extent and max no. of
        #lines for proper sizing
        clabels = [self.GetColLabelValue(i) for i in range(self.GetNumberCols())]
        height = max([self.GetTextExtent(lab)[1] for lab in clabels])
        lines = max([lab.count('\n') + 1 for lab in clabels])
        totalh = (height * lines or 30) +20
        self.SetColLabelSize(totalh)
        
        super(LabelSizedGrid, self).AutoSize()
        
        for col in range(0,self.GetNumberCols()):
            self.SetColLabelRenderer(col,CalColLabelRenderer())
        
        # The scroll bars aren't resized automatically (at least on windows)
        self.AdjustScrollbars()
        self.ForceRefresh()
        
    def OnRangeSelect(self, event):
        """
        For reasons unknown, the built-in grid methods for getting selected cells
        or rows simply don't seem to work (maybe due to selection mode issues?)
        
        Therefore, we keep a set of selected rows around for this extension for
        great justice.
        """
        new_rows = range(event.GetTopLeftCoords()[0], 
                         event.GetBottomRightCoords()[0]+1)
        if event.Selecting():
            self._selected_rows.update(new_rows)
        else:
            self._selected_rows.difference_update(new_rows)
        event.Skip()
        
    @property
    def SelectedRows(self):
        return sorted(list(self._selected_rows))
    

class CalColLabelRenderer(glr.GridLabelRenderer):
    
    
    def Draw(self,grid, dc, rect, col):
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        rect.left-=1
        self.DrawBorder(grid,dc,rect)
        self.DrawText(grid,dc,rect,text,hAlign,vAlign)
        if(grid.GetSortingColumn() == col):
            tri_width = 8
            tri_height = 5
            left = rect.left + abs(rect.left-rect.right)/2-tri_width/2
            top = rect.bottom - 2 - tri_height

            dc.SetBrush(wx.Brush(wx.BLACK))
            if grid.IsSortOrderAscending():
                dc.DrawPolygon([(left,top), (left + tri_width,top), (left + tri_width/2, top + tri_height)])
            else:
                dc.DrawPolygon([(left + tri_width/2, top), (left + tri_width, top + tri_height), (left, top + tri_height)])
        
#TODO: what does this actually accomplish?
class FancyTextRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self):
        wx.grid.PyGridCellRenderer.__init__(self)
        
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = attr.GetBackgroundColour()
            fg = attr.GetTextColour()
        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)
        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        wx.lib.fancytext.RenderToDC(text, dc, rect.x + 2, rect.y + 2)
        dc.DestroyClippingRegion()
        
    def GetBestSize(self, grid, attr, dc, row, col):
            """Customisation Point: Determine the appropriate (best) size for 
            the control, return as wxSize

            Note: You _must_ return a wxSize object.  Returning a two-value-tuple
            won't raise an error, but the value won't be respected by wxPython.
            """
            x, y = wx.lib.fancytext.GetExtent(grid.GetCellValue(row, col), dc)
            # note that the two-tuple returned by GetTextExtent won't work,
            # need to give a wxSize object back!
            return wx.Size(x, y)

    def Clone(self):
        return FancyTextRenderer()
        

        
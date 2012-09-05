#!/usr/bin/env python

"""WorkflowEditorTest.py is a starting point for a workflow editor for ACE."""

import wx

class WorkflowComponent():
    
    def __init__(self, x, y):
        self.rect = wx.Rect(x, y, 200, 75)
        self.selectionRect = wx.Rect(x-2, y-2, 204, 79)
        self.selected = False
        self.name     = "Workflow Component"
        
    def Contains(self, pt):
        return self.rect.Contains(pt)
        
    def Draw(self, dc):
        dc.SetPen(wx.Pen("Black", 2, wx.SOLID))
        dc.SetBrush(wx.Brush("White", wx.SOLID))
        dc.DrawRectangleRect(self.rect)
        self.DrawName(dc)
        if self.selected:
            dc.SetPen(wx.Pen("Red", 2, wx.SOLID))
            dc.SetBrush(wx.Brush("White", wx.TRANSPARENT))
            dc.DrawRectangleRect(self.selectionRect)
            
    def DrawName(self, dc):
        top  = self.rect.y + 37
        left = self.rect.x + 100

        extent = dc.GetTextExtent(self.name)
        
        width  = extent[0]
        height = extent[1]
        
        left = left - width / 2
        top  = top - height / 2
        
        dc.DrawText(self.name, left, top)
        
    def SetSelected(self, value):
        self.selected = value

class WorkflowWindow(wx.Window):

    def __init__(self, parent):
        wx.Window.__init__(self, parent, id=-1)
        self.SetBackgroundColour("White")
        
        self.rects = []
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.reInitBuffer = True
        self.selected     = None
        
    def InitBuffer(self):
        size = self.GetClientSize()
        print "size: (%d, %d)" % (size.width, size.height)
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawRects(dc)
        self.reInitBuffer = False

    def DrawRects(self, dc):
        for rect in self.rects:
            rect.Draw(dc)

    def OnLeftDown(self, event):

        hitRect = None
        pos = event.GetPositionTuple()

        # loop through list of rectangles backwards to find the
        # top most rectangle selected by the user and select it

        index = len(self.rects) - 1
        while index > -1:
            rect = self.rects[index]
            if rect.Contains(pos):
                rect.SetSelected(True)
                hitRect = rect
                break
            index = index - 1

        # loop through list of rectangles and deselct all
        # rectangles except hitRect
                
        for rect in self.rects:
            if not rect == hitRect:
                rect.SetSelected(False)
        
        # update class to point at hitRect (which may be set to None)
        
        self.selected = hitRect
        if self.selected:
            self.rects.remove(self.selected)
            self.rects.append(self.selected)

        # save position in case of drag event
        self.pos = wx.Point(*event.GetPositionTuple())

        self.CaptureMouse()
        
    def OnLeftUp(self, event):
        
        if self.HasCapture():
            if not self.selected:
                rect = WorkflowComponent(*event.GetPositionTuple())
                rect.SetSelected(True)
                self.rects.append(rect)
                self.selected = rect
            
            self.reInitBuffer = True
            self.ReleaseMouse()
        
    def OnMotion(self, event):
        if event.Dragging() and event.LeftIsDown() and self.selected:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            self.DrawMotion(dc, event)
        event.Skip()
        
    def DrawMotion(self, dc, event):
        newPos = wx.Point(*event.GetPositionTuple())
        diffPos = newPos - self.pos

        #print "New Position: " + str(newPos)
        #print "Previous Position: " + str(self.pos)
        #print "Difference: " + str(diffPos)
        
        self.selected.rect.x += diffPos.x
        self.selected.rect.y += diffPos.y

        self.selected.selectionRect.x += diffPos.x
        self.selected.selectionRect.y += diffPos.y
        
        self.pos = newPos
        
        dc.Clear()
        self.DrawRects(dc)
        
    def OnSize(self, event):
        self.reInitBuffer = True

    def OnIdle(self, event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
    
    def OnPaint(self, event):
        if not hasattr(self, "buffer"):
            self.InitBuffer()
        dc = wx.BufferedPaintDC(self, self.buffer)

class WorkflowFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title="Workflow Editor", size=(800,600), pos=(0,0))
        self.window = WorkflowWindow(self)
    
class App(wx.App):
    
    def OnInit(self):
        self.frame = WorkflowFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

if __name__ == '__main__':
    app = App(redirect=False)
    app.MainLoop()

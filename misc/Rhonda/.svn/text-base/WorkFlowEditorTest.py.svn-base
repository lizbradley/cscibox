#!/usr/bin/env python

"""WorkflowEditorTest.py is a starting point for a workflow editor for ACE."""

import wx

class WorkflowComponent():
    
    def __init__(self, x, y, name):
        self.rect = wx.Rect(x, y, 90, 40)
        self.selectionRect = wx.Rect(x-2, y-2, 94, 44)
        self.selected = False
        self.name     = name
        
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
        top  = self.rect.y + 17
        left = self.rect.x + 40

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
        print "WorkflowWindow init"
        #vbox = wx.BoxSizer(wx.VERTICAL)

        #self.SetSizer(vbox)
           
        self.rects = []
        w = 700
        h = 500
        for i in range(1,11):
            name = "test" + str(i)
            rect = WorkflowComponent(w, h, name)
            rect.SetSelected(False)
            self.rects.append(rect)
            h = h - 50
        self.selected = rect
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
                
        self.reInitBuffer = True
        self.selected     = None

    def InitBuffer(self):
        print "WorkflowWindow initBuffer"
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawRects(dc)
        self.DrawLine(dc)
        self.reInitBuffer = False

    def DrawLine(self, dcLine):
        # Draw line separating workflow buttons from workflow area
        Lines = []
        x,y = 650,10 
        x2,y2 = 650,530 
        Lines.append((x,y,x2,y2))

        dcLine.BeginDrawing()
        for line in Lines:
            pen = wx.Pen("Red", 5, wx.SOLID)
            pen.SetCap(wx.CAP_ROUND)
            dcLine.SetPen(pen)
            dcLine.DrawLine(line[0],line[1],line[2],line[3])
        dcLine.EndDrawing()

    def DrawRects(self, dc):
        print "WorkflowWindow drawRects"
        for rect in self.rects:
            rect.Draw(dc)

 #   def OnExit(self, event):
 #       self.Close()

    def OnLeftDown(self, event):
        print "WorkflowWindow OnLeftDown"
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
        print "WorkflowWindow OnLeftUp"
        if self.HasCapture():
#            if not self.selected:
#                rect = WorkflowComponent(*event.GetPositionTuple())
#                rect.SetSelected(True)
#                self.rects.append(rect)
#                self.selected = rect
            
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

        self.selected.rect.x += diffPos.x
        self.selected.rect.y += diffPos.y

        self.selected.selectionRect.x += diffPos.x
        self.selected.selectionRect.y += diffPos.y
        
        self.pos = newPos
        
        dc.Clear()
        self.DrawLine(dc)
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
        print "workflow frame"
        wx.Frame.__init__(self, parent=None, id=-1, title="Workflow Editor", size=(800,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.window = WorkflowWindow(self) 
        self.createToolBar()
        
        
    def createToolBar(self):
        toolbar = self.CreateToolBar(wx.TB_VERTICAL)
        for each in self.toolbarData():
            self.createSimpleTool(toolbar, *each)
            
        toolbar.Realize()
        
    def createSimpleTool(self, toolbar, label, filename, help, handler, index):
        if not label:
            toolbar.AddSeparator()
            return
        bmp = wx.Image(filename, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        tool = toolbar.AddSimpleTool(index, bmp, label, help)
        self.Bind(wx.EVT_MENU, handler, tool)

    def toolbarData(self):
        return (("Exit", "toolbar/exit.bmp", "Exit", self.OnExit, 1),
                ("","","","",""),
                ("Person", "toolbar/person.bmp", "person", self.OnNewComponent, 2), 
                ("Red", "toolbar/red.bmp", "Red", self.OnNewComponent, 3), 
                ("Person2", "toolbar/person.bmp", "person2", self.OnNewComponent, 4), 
                ("Red2", "toolbar/red.bmp", "Red2", self.OnNewComponent, 5), 
                ("Person3", "toolbar/person.bmp", "person3", self.OnNewComponent, 6), 
                ("Red3", "toolbar/red.bmp", "Red3", self.OnNewComponent, 7), 
                ("Person4", "toolbar/person.bmp", "person4", self.OnNewComponent, 8), 
                ("Red4", "toolbar/red.bmp", "Red4", self.OnNewComponent, 9), 
                ("Person5", "toolbar/person.bmp", "person5", self.OnNewComponent, 10), 
                ("Red5", "toolbar/red.bmp", "Red5", self.OnNewComponent, 11), 
                ("Person6", "toolbar/person.bmp", "person6", self.OnNewComponent, 12), 
                ("Red6", "toolbar/red.bmp", "Red6", self.OnNewComponent, 13), 
                ("Person7", "toolbar/person.bmp", "person7", self.OnNewComponent, 14), 
                ("Red7", "toolbar/red.bmp", "Red7", self.OnNewComponent, 15), 
                ("Person8", "toolbar/person.bmp", "person8", self.OnNewComponent, 16), 
                ("Red8", "toolbar/red.bmp", "Red8", self.OnNewComponent, 17), 
                ("Person9", "toolbar/person.bmp", "person", self.OnNewComponent, 2), 
                ("Red9", "toolbar/red.bmp", "Red", self.OnNewComponent, 3), 
                ("Person10", "toolbar/person.bmp", "person", self.OnNewComponent, 2), 
                ("Red10", "toolbar/red.bmp", "Red", self.OnNewComponent, 3), 
                ("Person11", "toolbar/person.bmp", "person", self.OnNewComponent, 2), 
                ("Red11", "toolbar/red.bmp", "Red", self.OnNewComponent, 3))

    def OnExit(self, event):
        self.Close()

    def OnNewComponent(self, event):
       toolbar = self.GetToolBar()
       itemId = event.GetId()
       print str(itemId)
       item = toolbar.FindById(itemId)
       print str(item)
       name = item.GetShortHelp()

       rect = WorkflowComponent(200, 200, name)
       rect.SetSelected(True)
       self.window.rects.append(rect)
       self.window.reInitBuffer = True
    
class App(wx.App):
    print "App Loop"
    def OnInit(self):
        print "On Init: "
        self.frame = WorkflowFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

if __name__ == '__main__':
    print "In Main: "
    app = App(redirect=False)
    app.MainLoop()

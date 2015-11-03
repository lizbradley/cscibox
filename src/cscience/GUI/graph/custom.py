#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import sys
import wx
import wx.calendar
import wx.combo
from datetime import date as dt

class ColorButton(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent)
        self.color = (0,0,0)
        self.color_data = wx.ColourData()
        self.mk_bitmap()

    def SetColor(self, color):
        self.color = color
        self.color_data.SetColour(self.color)
        self.mk_bitmap()

    def GetColor(self):
        return self.color

    def ShowModal(self, parent):
        dialog = wx.ColourDialog(parent, self.color_data)
        dialog.ShowModal()
        self.color_data = dialog.GetColourData()
        self.color = self.color_data.GetColour()
        self.SetColor(self.color)

    def mk_bitmap(self):  # copied directly from demo
        bmp = wx.EmptyBitmap(50, 15)
        dc = wx.MemoryDC(bmp)

        # clear to a specific background colour
        dc.SetBrush(wx.Brush(self.color, wx.SOLID))
        dc.DrawRectangle(0,0, 50,15)

        del dc

        # and tell the ComboCtrl to use it
        self.SetBitmap(bmp)
        self.GetParent().Refresh()

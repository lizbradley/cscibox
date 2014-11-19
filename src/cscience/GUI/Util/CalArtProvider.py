"""
CalArtProvider.py

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
import os
import sys


from cscience.GUI import icons

#TODO: For release (or once we have the icons finalized), convert this ArtProvider to use Img2PyArtProvider and embedded images.

class CalArtProvider(wx.ArtProvider):

    iconfiles = {icons.ART_CALC: 'calculator_black.png',
                 icons.ART_VIEW_ATTRIBUTES: 'table_select_column.png',
                 icons.ART_FILTER: 'table_select_row.png',
                 icons.ART_ANALYZE_AGE: 'timeline_marker.png',
                 icons.ART_SORT_ASCENDING: 'sort_ascending.png',
                 icons.ART_SORT_DESCENDING: 'sort_descending.png',
                 icons.ART_GRAPHING_OPTIONS: 'cog.png',
                 icons.ART_RADIO_ON: 'bullet_black.png',
                 icons.ART_RADIO_OFF: 'bullet_white.png',
                 #TODO: Make slightly less awkward x and y icons.
                 icons.ART_X_AXIS: 'key_x.png',
                 icons.ART_Y_AXIS: 'key_y.png'
                }

    def __init__(self):
        super(CalArtProvider, self).__init__()

    def GetBitmapFromFile(self,filepath):
        try:
            img = wx.Image(filepath,type=wx.BITMAP_TYPE_PNG)
            bmp = wx.BitmapFromImage(img)
        except Exception:
            print("bmp file for icon not found.")
            bmp = wx.NullBitmap
        return bmp

    def CreateBitmap(self, artid, client, size):
        path = ""
        if getattr(sys, 'frozen', False):
            # we are running in a |PyInstaller| bundle
            path = sys._MEIPASS
        else:
            path = os.path.join(os.getcwd(), os.pardir)

        path = os.path.join(path, "resources", "fatcow-hosting-icons-3000")

        if size == 32:
            path = os.path.join(path,"32x32")
        else:
            path = os.path.join(path,"16x16")

        if artid in self.iconfiles:
            return self.GetBitmapFromFile(os.path.join(path, self.iconfiles[artid]))
        else:
            return wx.NullBitmap



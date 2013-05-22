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

class CalArtProvider(wx.ArtProvider):
    
    ART_CALC = "ID_FOR_CALCULATOR_ICON"
    ART_VIEW_ATTRIBUTES = "ID_FOR_VIEW_ATTRIBUTES_ICON"
    ART_FILTER = "ID_FOR_FILTER_ICON"
    ART_ANALYZE_AGE = "ID_FOR_ANALYZE_AGES_ICON"
    ART_SORT_ASCENDING = "ID_FOR_SORT_ASCENDING_ICON"
    ART_SORT_DESCENDING = "ID_FOR_SORT_DESCENDING_ICON"
    
    def __init__(self):
        wx.ArtProvider.__init__(self)
        
    def GetBitmapFromFile(self,filepath):
        try:
            img = wx.Image(filepath,type=wx.BITMAP_TYPE_PNG)
            bmp = wx.BitmapFromImage(img)
        except:
            print("bmp file for icon not found.")
            bmp = wx.NullBitmap
        return bmp
        
    def CreateBitmap(self, artid, client, size):
        path = os.path.join(os.getcwd(),os.pardir,"resources", "fatcow-hosting-icons-3000")
        if(size is 32):
            path = os.path.join(path,"32x32")
        else:
            path = os.path.join(path,"16x16")

        bmp = wx.NullBitmap
        
        if(artid == self.ART_CALC):
            filename = "calculator_black.png"
            print("ID_check if statement was true. Our path is: " + os.path.join(path,filename))
        elif(artid == self.ART_VIEW_ATTRIBUTES ):
            filename = "soil_layers.png"
        elif(artid == self.ART_FILTER):
            filename = "table_tab_search.png"
        elif(artid == self.ART_ANALYZE_AGE):
            filename = "timeline_marker.png"
        elif(artid == self.ART_SORT_ASCENDING):
            filename = "sort_ascending.png"
        elif(artid == self.ART_SORT_DESCENDING):
            filename = "sort_descending.png"
        else:
            return bmp
        
        bmp = self.GetBitmapFromFile(os.path.join(path,filename))

        return bmp

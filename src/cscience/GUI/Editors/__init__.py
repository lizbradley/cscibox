"""
__init__.py

* Copyright (c) 2006-2015, University of Colorado.
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
import pickle

#TODO: use wx.PersistenceManager &c instead of rolling our own!
class MemoryFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MemoryFrame, self).__init__(*args, **kwargs)
        
        self.Bind(wx.EVT_MOVE, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        
    def SetSizer(self, sizer):
        super(MemoryFrame, self).SetSizer(sizer)
        self.Layout()
        self.SetSize(self.GetBestSize())
        self.SetMinSize(self.GetSize())
        
        config = wx.Config.Get()
        loc = config.Read(self.loc_config)
        if loc:
            self.SetPosition(pickle.loads(loc))
        size = config.Read(self.size_config)
        if size:
            self.SetSize(pickle.loads(size))
            
    @property
    def loc_config(self):
        return '/'.join(('windows', self.framename, 'location'))
    @property
    def size_config(self):
        return '/'.join(('windows', self.framename, 'size'))
    
    def on_move(self, event):
        wx.Config.Get().Write(self.loc_config, 
                              pickle.dumps(tuple(event.GetPosition())))
    def on_resize(self, event):
        wx.Config.Get().Write(self.size_config, 
                              pickle.dumps(tuple(event.GetSize())))
        self.Layout()

import CoreBrowser
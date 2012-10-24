#!/usr/bin/env pythonw
"""
ACE.py

ACE is an Age Calculation Environment that supports the dating of samples
using cosmogenic nuclide dating techniques. ACE is also a design environment
that supports the creation and evaluation of new algorithms for cosmogenic
dating.

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

import sys
import traceback
import wx

from cscience import datastore
from cscience.GUI import Editors

class BrowserApp(wx.App):
    
    def on_repo_error(self, exc):
        config = wx.Config.Get()
        config.DeleteEntry("repodir", False)
        config.Flush()
        
        # need to CallAfter or something to handle the splash screen, here
        wx.MessageBox(' '.join((exc.message, 
                                'Re-run CScience to select a new repository.')),
                      'Repository Error')
        wx.SafeYield(None, True)
        #Need to flush?
    
    def on_error(self, exctype, value, traceback):
        if exctype == datastore.RepositoryException:
            self.on_repo_error(value)
        else:
            #TODO: handle with more elegance.
            print exctype, value
            print traceback.format_exc()  
        self.Exit()

    def OnInit(self):
        self.SetAppName('CScience')
        self.SetVendorName('colorado.edu')
        config = wx.Config('CScience', 'colorado.edu')
        wx.Config.Set(config)
        sys.excepthook = self.on_error
        
        #bmp = wx.Image("images/ace_logo.png").ConvertToBitmap()
        #wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, 500, None, -1)
        #wx.SafeYield(None, True)
        
        frame = Editors.SampleBrowser.SampleBrowser()
        self.SetTopWindow(frame)
        frame.Show()
        
        repodir = config.Read('repodir')
        wx.CallAfter(frame.open_repository, repodir)
        return True
        
    def OnExit(self):
        config = wx.Config.Get()
        if datastore.data_source:
            config.Write('repodir', datastore.data_source)
        else:
            config.DeleteEntry('repodir')
        config.Flush()

if __name__ == '__main__':
    app = BrowserApp(redirect=False)
    app.MainLoop()

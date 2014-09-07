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
import logging

from wx.lib.agw import persist
from wx.lib.art import img2pyartprov

from cscience import datastore
from cscience.GUI import Editors, icons
from cscience.GUI.Util import CalArtProvider

class BrowserApp(wx.App):

    def OnInit(self):
        # Colin wuz here
        #bmp = wx.Image("images/ace_logo.png").ConvertToBitmap()
        #wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, 500, None, -1)
        #wx.SafeYield(None, True)
        #set correct icon handlers.
        #TODO: is this really the right place to do this in?
        wx.ArtProvider.Push(CalArtProvider())
        wx.ArtProvider.Push(img2pyartprov.Img2PyArtProvider(icons, artIdPrefix='ART_'))


        frame = Editors.CoreBrowser.CoreBrowser()
        self.SetTopWindow(frame)

        #This disgusting hack is required by a bug in wxpython 3.0.0 that causes
        #message boxes & dialogs to return too soon if they are called before
        #app.MainLoop has actually been run. Potential fix in later version of
        #wxpython that we should look into...
        #see http://trac.wxwidgets.org/ticket/16253 for details
        wx.CallLater(10, persist.PersistenceManager.Get().Restore, frame)
        return True


def setupAppLogger():
    # Create the application-wide logger (root)
    logger = logging.getLogger()

    # Set this to logging.WARN or logging.ERROR for production
    logger.setLevel(logging.DEBUG)

    # create file handler which logs warning messages and up
    fh = logging.FileHandler('cscience.log')
    fh.setLevel(logging.WARN)

    # create console handler for all log messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


if __name__ == '__main__':


    # if getattr(sys, 'frozen', False):
    #     # we are running in a |PyInstaller| bundle
    #     datastore_singleton = datastore.Datastore()
    #     sys.modules['cscience.datastore'] = datastore_singleton

    #setupAppLogger()
    app = BrowserApp()
    app.MainLoop()


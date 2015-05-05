"""
__init__.py

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
from cscience.GUI.Util import grid
from cscience.GUI.Util import graph
from cscience.GUI.Util.GraphingWindows import PlotWindow
from cscience.GUI.Util.CalArtProvider import CalArtProvider

import wx

class FunctionValidator(wx.PyValidator):
    def __init__(self, valid_func, *args, **kwargs):
        self.valid_func = valid_func
        super(FunctionValidator, self).__init__(*args, **kwargs)
    
    def Clone(self):
        return FunctionValidator(self.valid_func)
    
    def Validate(self, win):
        """ Validate the contents of the given control -- simply calls the 
        constructor-passed function
        """
        return self.valid_func(self, win)
    
    def TransferToWindow(self):
        return True # Prevent wxDialog from complaining.
    def TransferFromWindow(self):
        return True # Prevent wxDialog from complaining.

"""
AboutBox.py

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
import wx.html
import wx.lib.hyperlink

class AboutBox(wx.Dialog):
    text = '''
<html>
    <body bgcolor="white">
        <center>
            <h1>ACE: Age Calculation Environment</h1>
            <h2>Version 1.0</h2>
            <h3>http://ace.hwr.arizona.edu</h3>
            <table>
                <tr>
                    <th colspan="2">Contributors</td>
                </tr>
                <tr>
                    <td>Kenneth M. Anderson</td>
                    <td>Laura Rassbach</td>
                </tr>
                <tr>
                    <td>Elizabeth Bradley</td>
                    <td>Evan Sheehan</td>
                </tr>
                <tr>
                    <td>William Van Lepthien</td>
                    <td>Marek Zreda</td>
                </tr>
                <tr>
                    <td align="center" colspan="2">Chris Zweck</td>
                </td>
            </table>
            <p>This software is based upon work sponsored by the NSF under Grant Number ATM-0325812 and Grant Number ATM-0325929.</p>
            <p>Copyright &copy; 2007-2009 University of Colorado. All rights reserved.</p>
        </center>
    </body>
</html>'''
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About ACE', size=(600, 400) )

        html = wx.html.HtmlWindow(self)
        html.SetPage(self.text)
        
        link = wx.lib.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, "ACE Website", URL="http://ace.hwr.arizona.edu")
        button = wx.Button(self, wx.ID_OK, "Ok")
        

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(link, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()


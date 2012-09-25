"""
RepositoryManager.py

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


import os.path

import wx

import matplotlib
matplotlib.use('WxAgg')

from ACE.framework import Attributes, Collections, Experiments, Factors, \
    Filters, Groups, Samples, Templates, Views, Workflows

from ACE.GUI.Editors.SampleBrowser import SampleBrowser

class RepositoryManager(object):
    
    MODELS = ["Attributes", "Collections", "Experiments", "Factors", "Filters", 
              "Groups", "Samples", "Templates", "Views", "Workflows"]
    
    def __init__(self):
        self.open = False
        self.modified = False
        self.windows = []
        self.repo = None
        self.config = wx.Config("ACE", "colorado.edu")
        self.models = {}
        self.InitModels()
        
    def HandleAppStart(self, app):
        self.frame = SampleBrowser(self)
        app.SetTopWindow(self.frame)
        self.frame.Show()
        wx.CallAfter(self.FirstAction)
        return True
        
    def FirstAction(self):
        self.repo = self.config.Read("repodir", "")
        if self.repo == "":
            self.repo = None
        if self.repo is None:
            dialog = wx.DirDialog(None, "Choose a Repository", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
            result = dialog.ShowModal()
            path = dialog.GetPath()
            dialog.Destroy()
            if result == wx.ID_OK:
                self.repo = path
            else:
                wx.CallAfter(self.frame.OnQuit, None)
                return

        if not os.path.exists(self.repo):
            wx.FutureCall(1000, self.ReportRepoMissing)
            return

        result = self.frame.OnOpen(None)
        if not result:
            wx.FutureCall(1000, self.ReportLoadError)
        
    def ReportRepoMissing(self):
        wx.MessageBox('Previously saved repository no longer exists. Re-run ACE to select new repository.', "Repository Error")
        wx.SafeYield(None, True)
        self.repo = None
        self.config.DeleteEntry("repodir", False)
        self.config.Flush(True)
        wx.CallAfter(self.frame.OnQuit, None)

    def ReportLoadError(self):
        wx.MessageBox('Error while loading selected repository. Re-run ACE to select new repository.', "Repository Load Error")
        wx.SafeYield(None, True)
        self.repo = None
        self.config.DeleteEntry("repodir", False)
        self.config.Flush(True)
        wx.CallAfter(self.frame.OnQuit, None)

    def HandleAppQuit(self):
        if self.repo is not None:
            self.config.Write("repodir", self.repo)
        else:
            if self.config.Exists("repodir"):
                self.config.DeleteEntry("repodir", False)
        self.handleClose()
        
    def handleOpen(self):
        
        # load repository into models
        try:
            self.InitModels()
            self.LoadModels()
        except Exception as e:
            print e
            return False

        # self.InitModels()
        # self.LoadModels()
        
        # check to see if "All" view is out-of-date... if so update it
        legalAtts = self.GetModel("Attributes")
        views = self.GetModel("Views")
        view = views.get("All")
        if len(view.atts()) != len(legalAtts.names()):
            for att in legalAtts.names():
                view.add(att)
            self.RepositoryModified()
        
        # set status
        self.modified = False
        return True
        
    def handleSwitch(self):
        # check to see if repository is modified
        if self.modified:
            dialog = wx.MessageDialog(None, 'You have modified this repository. Would you like to save your changes?', "Unsaved Changes", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_YES:
                self.handleSave()
        
        # retrieve repository directory
        dialog = wx.DirDialog(None, "Choose a Repository", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        path = dialog.GetPath()
        dialog.Destroy()
        if result == wx.ID_OK:
            self.frame.OnClose(None)
            self.repo = path
            result = self.frame.OnOpen(None)
            if not result:
                wx.CallAfter(self.ReportLoadError)

    def handleSave(self):
        # check to see if repository is modified
        if self.modified:
            self.SaveModels()
            self.RepositorySaved()

    def handleClose(self):        
        # check to see if repository is modified
        if self.modified:
            dialog = wx.MessageDialog(None, 'You have modified this repository. Would you like to save your changes?', "Unsaved Changes", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dialog.ShowModal() == wx.ID_YES:
                self.handleSave()
            else:
                # if user decides not to save changes during application shutdown
                # then pretend that repository is not modified.
                # This prevents ACE from asking the user if they want to save
                # changes twice, since sometimes handleClose is called twice
                # during shutdown.
                self.modified = False

        # close all windows except for main window
        for window in self.windows[:]:
            try:
                if window.IsShown():
                    window.Close()
            except:
                # sometimes we have references to windows that have already closed
                pass

        # clear models
        self.ClearModels()
            
    def RepositoryModified(self):
        self.modified = True
        menuBar = self.frame.GetMenuBar()
        fileMenu = menuBar.GetMenu(menuBar.FindMenu("File"))
        fileMenu.Enable(wx.ID_SAVE, True)
        
    def RepositorySaved(self):
        self.modified = False
        try:
            menuBar = self.frame.GetMenuBar()
            fileMenu = menuBar.GetMenu(menuBar.FindMenu("File"))
            fileMenu.Enable(wx.ID_SAVE, False)
        except:
            pass

    def AddWindow(self, window):
        self.windows.append(window)
        
    def RemoveWindow(self, window):
        self.windows.remove(window)
        
    def GetModel(self, name):
        return self.models[name]
        
    def GetConfig(self):
        return self.config

    def SaveModels(self):
        for name in RepositoryManager.MODELS:
            model = self.models[name]
            model.save(self.repo)
        
    def LoadModels(self):
        for name in RepositoryManager.MODELS:
            model = self.models[name]
            try:
                model.load(self.repo)
            except:
                model.load(self.repo, self)
        
    def InitModels(self):
        for name in RepositoryManager.MODELS:
            self.models[name] = eval(name)()
        
    def ClearModels(self):
        self.models.clear()

    def GetClimateDataPath(self):
        return os.path.join(self.repo, 'NCEPData.txt.gz')

    def GetImportsPath(self):
        return os.path.join(self.repo, 'imports')
        

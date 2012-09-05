"""
main_window.py

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
import wx.lib.rcsizer as rcsizer

from Calvin.reasoning import evidence, confidence, conclusions, engine, samples
import confidence_display, user_polling
import ACE.GUI.Util.Graphing

"""
Notes on planned GUI changes:
1. break arguments into classes instead of splattering them all over the screen
2. make each single argument expandable into useful evidence, all in one block instead
   of split up: make sure to highlight what is pro and what is con drastically enough
3. recurse
4. for simulations, allow them to display on the right side of the screen
   the user should never have to deal with extra windows if we can avoid it
5. should also use the right side of the screen for confidence gestalts and
   a small box and whisker plot of age and uncertainty
"""

class CalvinFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Calvin")
        
        self.SetBackgroundColour(wx.WHITE)
        self.curPanel = None
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        wx.ToolTip.Enable(True)
        wx.ToolTip.SetDelay(10)
        
        self.dataButton = wx.Button(self, label='Argue With More Data')
        self.dataButton.Show(False)
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.dataButton, border=5, flag=wx.ALL)
        
        self.treeBox = ArgumentBook(self)

        sizer.Add(self.treeBox, border=5, proportion=1, flag=wx.ALL|wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL|wx.EXPAND)
        
        self.Bind(wx.EVT_BUTTON, self.pollForData, self.dataButton)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.SetSizer(sizer)
        self.SetSize((1000, 600))
        self.Layout()
        
    def showArguments(self, args, sampleStuff):
        self.sampleStuff = sampleStuff
        self.args = args
        self.__showArgs()
        
    def __showArgs(self):
        self.treeBox.showArgs(self.args)
                    
        self.dataButton.Show(samples.needData())
        self.pollData = (samples.landformPoll, samples.samplePoll)
        #self.treeBox.Expand(the_root)
        #self.treeBox.SelectItem(the_root)
        
        self.treeBox.SetFocus()
        self.Layout()
        
    def pollForData(self, evt):
        samples.landformData = self.sampleStuff[0].copy()
        samples.confidenceEntry = self.sampleStuff[1].copy()
        samples.sampleList = self.sampleStuff[2][:]
        samples.landformPoll = self.pollData[0][:]
        samples.samplePoll = self.pollData[1][:]
        
        user_polling.doLandformPolling()
        user_polling.doSamplePolling()
        
        self.Show(False)
        
        conclusions.reset()
        args = engine.explainAges()
        
        newWindow = CalvinFrame()
        newWindow.showArguments(args, self.sampleStuff)
        newWindow.Show()
        
        self.Close()
        self.Destroy()
        
        #well, this is sort of horrible, but trying to delete the existing pages from the
        #tree seems to be worse, so whatever

    def argSelected(self, evt):
       data = self.treeBox.GetPyData(evt.GetItem())
       if data is not None:
           self.clearArgument()
           if hasattr(data, '__iter__'):
               self.displaySummary(data)
           else:
               self.displayArgument(data)
    
    def clearArgument(self):
        if self.curPanel is None:
            return
        
        self.argSizer.Remove(self.curPanel)
        self.curPanel.Show(False)
        
    def displayArgument(self, data):
        self.curPanel = data.getGUIItem()
        
        if self.curPanel is None:
            self.curPanel = ArgumentPanel(self, data)
            
        self.argSizer.Add(self.curPanel, border=5, flag=wx.ALL|wx.EXPAND, proportion=2)
        self.curPanel.Show(True)
        self.Layout()
        
    def displaySummary(self, dataList):
        self.curPanel = SummaryPanel(self, dataList)
        self.argSizer.Add(self.curPanel, border=5, flag=wx.ALL|wx.EXPAND, proportion=2)
        self.curPanel.Show(True)
        self.Layout()
        
    def onClose(self, event):
        self.treeBox.Destroy()
        self.Destroy()
        
class ArgumentBook(wx.Treebook):
    
    #this is the top-level book that shows each argument in a tree thingie
    
    def __init__(self, parent):
        wx.Treebook.__init__(self, parent, id=-1)
        
            
    def showArgs(self, args):
        self.root = None
        args.sort(reverse=True)
        
        self.root = self.PageEntry('All Arguments', SummaryPanel(self, args), True)
        
        self.panel = wx.Panel(self)
        self.root.addChild(self.PageEntry('Conflicted', self.panel, True))
        self.root.addChild(self.PageEntry('Accepted', self.panel, True))
        self.root.addChild(self.PageEntry('Rejected', self.panel, True))
        self.root.addChild(self.PageEntry('Little Evidence', self.panel, True))
        
        #so the next step here is to drill down as I add each argument...
        for argument in args:
            if argument.conflict:
                myRoot = 0
            elif argument.confidence.valid < confidence.Validity.prob:
                myRoot = 3
            elif argument.confidence.isTrue():
                myRoot = 1
            else:
                myRoot = 2
                
            self.__displayUnderNode(self.root.getChild(myRoot), argument)
            
        self.__displayPages()
        
    def __displayPages(self):
        #print 'now displaying'
        self.root.displayRoot(self)
        
    def __displayUnderNode(self, entry, evid):
        page = self.PageEntry(evid.getUnifiedString(), None)
        entry.addChild(page)
        
        if evid.__class__.__name__ == 'Argument':
            ev = evid.getAllEvid()
            
            if len(ev) > 0:
                for rule in ev:        
                    self.__displayRuleUnderNode(page, rule)
        elif evid.__class__.__name__ == 'Simulation':
            if type(evid.guiItem) == type(''):
                stPage = self.PageEntry(evid.guiItem, None)
                entry.addChild(stPage)
            elif evid.guiItem.__class__.__name__ == 'Argument':
                self.__displayUnderNode(entry, evidence.Argument(evid.guiItem))
            else:
                page.window = evid.guiItem.makeFigure(self)
            
                    
    def __displayRuleUnderNode(self, entry, rule):
        topRule = self.PageEntry('RULE: ' + rule.getConclusionString(), None)
        entry.addChild(topRule)
        rhses = rule.rhsList
        
        for calc in [rhs for rhs in rhses if rhs.isCalculation()]:
            data = self.PageEntry(calc.getRuleString(rule.env), None)
            topRule.addChild(data)
            
            self.__displayUnderNode(data, calc)
            
        evid = [rhs for rhs in rhses if not rhs.isCalculation()]
        for notCalc in evid[:-1]:
            data = self.PageEntry(notCalc.getRuleString(rule.env) + rule.getJoinWord(), None)
            topRule.addChild(data)
            
            self.__displayUnderNode(data, notCalc)
            
            
        if len(evid) > 0:
            data = self.PageEntry(evid[-1].getRuleString(rule.env) + 
                                  rule.getImplicationString(), None)
            topRule.addChild(data)
            
            self.__displayUnderNode(data, evid[-1])
            
        #data = self.PageEntry(rule.getImplicationString(), None)
        #entry.addChild(data)
        
    
        
    class PageEntry:
        
        def __init__(self, text, window, shouldExpand = False):
            self.text = text
            self.window = window
            self.children = []
            self.shouldExpand = shouldExpand
            
        def addChild(self, child):
            self.children.append(child)
            
        def getChild(self, index):
            return self.children[index]
        
        def displayRoot(self, parent):
            parent.AddPage(self.window, self.text)
            
            nextInd = 0
            for child in self.children:
                nextInd = child.displayChild(0, nextInd + 1, parent)
                #nextInd += 1
                
            if self.shouldExpand:
                parent.ExpandNode(0)
                
            return nextInd
                
        def displayChild(self, parInd, myInd, parent):
            parent.InsertSubPage(parInd, self.window, self.text)
            
            
            nextInd = myInd
            for child in self.children:
                nextInd = child.displayChild(myInd, nextInd + 1, parent)
                #nextInd += 1
                
            #if len(self.children) > 0:
            #parent.ExpandNode(myInd)
            if self.shouldExpand:
                parent.ExpandNode(myInd)
                
            return nextInd
        
        
class SummaryPanel(wx.Panel):
    
    #this panel needs to display a summary of all arguments generated.
    
    def __init__(self, parent, args):
        wx.Panel.__init__(self, parent)
        
        argList = [arg for arg in args if arg.isValid()]
        sizer = rcsizer.RowColSizer()

        panel = wx.Panel(self, size=(1, 1))
        sizer.Add(panel, col=confidence.Validity.RANKS, row=confidence.Applic.RANKS)
        
        #so what I really want to do is put in a grid, no? nah. Just expanding rows/cols is good enough
        base = [None] * confidence.Validity.RANKS
        panels = []
        for i in xrange(confidence.Applic.RANKS):
            sizer.AddGrowableRow(i)
            panels.append(base[:])
        for i in xrange(confidence.Validity.RANKS):
            sizer.AddGrowableCol(i)
            
    
        def addArgument(arg):
            index = confidence_display.getIndex(arg.confidence)
            if index is None:
                return
            panel = panels[index[0]][index[1]]
            if panel is None:
                panel = wx.Panel(self)
                panels[index[0]][index[1]] = panel
                
                box = wx.StaticBox(panel, wx.ID_ANY, "RULE")
            
                color = wx.Colour(*confidence_display.getColor(arg.confidence))
                box.SetForegroundColour(color)
                box.SetBackgroundColour(color)
            
                bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
                panel.SetSizer(bsizer)
                
                sizer.Add(panel, flag=wx.EXPAND, row=index[0], col=index[1])
                
            bsizer = panel.GetSizer()
            label = wx.StaticText(panel, label=arg.getUnifiedString())
            bsizer.Add(label, flag=wx.EXPAND, proportion=1)
        
            
        for arg in argList:
            addArgument(arg)
            
        self.SetSizer(sizer)
        
        
class ArgumentPanel(wx.Panel):
    
    #from calvin.confidence import Confidence, Applic, Validity
    
    #this doesn't work, but I want to do something like this with Confidence
    #to color/index, since this is really a user interface issue, not an
    #issue of confidence itself, it shouldn't be in there.
    #__CONF_INFO = {Confidence(Applic.vf, Validity.poor):(('R', 'G', 'B'), ('x', 'y'))}'
    
    def __init__(self, parent, argument):
        wx.Panel.__init__(self, parent)
        
        self.argument = argument
        self.SetBackgroundColour(wx.WHITE)
        
        self.__mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        
        self.__topLabel = wx.StaticText(self, label=argument.getTitleString(), style=wx.ALIGN_CENTER)
        self.__topLabel.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, 
                                        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(self.__topLabel, flag=wx.EXPAND, proportion=1)
        
        self.__mainSizer.Add(topSizer, flag=wx.EXPAND | wx.BOTTOM, border=5)
        
        self.__ruleSizer = wx.BoxSizer(wx.HORIZONTAL)
        box = wx.StaticBox(self)
        bSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.__gridSizer = wx.GridSizer(rows=confidence.Applic.RANKS,
                                        cols=confidence.Validity.RANKS,
                                        vgap=1, hgap=1)
        self.__colorPanels = []
        for i in xrange(confidence.Applic.RANKS * confidence.Validity.RANKS):
            panel = wx.Panel(self)
            self.__colorPanels.append(panel)
            self.__gridSizer.Add(panel, flag=wx.ALIGN_CENTER)
            
        self.__subArgs = {}
        
        self.__makeRulePanel(argument.getProEvid())
        
        gCenter = wx.BoxSizer(wx.VERTICAL)
        #gCenter.AddStretchSpacer()
        bSizer.Add(self.__gridSizer, flag=wx.EXPAND, proportion=1)
        gCenter.Add(bSizer, flag=wx.ALIGN_CENTER)
        #gCenter.AddStretchSpacer()
        self.__ruleSizer.Add(gCenter, flag=wx.EXPAND | wx.ALL, border=15)
        
        self.__makeRulePanel(argument.getConEvid())
        
        self.__mainSizer.Add(self.__ruleSizer, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__mainSizer)
        self.Layout()
        
        argument.setGUIItem(self)
        
        
    def __makeRulePanel(self, rules):
        scrolledWindow = wx.ScrolledWindow(self)
        panel = wx.Panel(scrolledWindow)
        panel.SetBackgroundColour(wx.WHITE)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        rules.sort()
        
        #mmm, hack.
        if len(rules) > 0 and not rules[0].confidence.isTrue():
            rules.reverse()
        
        while len(rules) > 0:
            conf = rules[-1].confidence
            
            innerPanel = wx.Panel(panel)
            innerSizer = wx.BoxSizer(wx.VERTICAL)
            
            size = 10
            
            while len(rules) > 0 and rules[-1].confidence == conf:
                rule = rules.pop()
                size += 5
                self.__createRuleWidget(rule, innerPanel, innerSizer)
                
            index = confidence_display.getIndex(conf)
            colorPanel = self.__colorPanels[index[0] * confidence.Validity.RANKS + index[1]]
            colorPanel.SetBackgroundColour(wx.Color(*confidence_display.getColor(conf)))
            colorPanel.SetSize((size, size))    
            
            innerPanel.SetSizer(innerSizer)
            innerPanel.SetToolTip(wx.ToolTip(str(conf)))
            sizer.Add(innerPanel)
            sizer.AddSpacer(30)
            
        panel.SetSizer(sizer)
        sSizer = wx.BoxSizer(wx.HORIZONTAL)
        sSizer.Add(panel, flag=wx.EXPAND, proportion=1)
        scrolledWindow.SetSizer(sSizer)
        scrolledWindow.SetScrollRate(20, 20)
        scrolledWindow.EnableScrolling(True, True)
        
        self.__ruleSizer.Add(scrolledWindow, flag=wx.EXPAND, proportion=1)
            
    def __createRuleWidget(self, rule, panel, sizer):
        box = wx.StaticBox(panel, wx.ID_ANY, "RULE")
            
        color = wx.Colour(*confidence_display.getColor(rule.confidence))
        box.SetForegroundColour(color)
        box.SetBackgroundColour(color)
        boxSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        topLabel = wx.StaticText(panel, label=rule.getRuleString())
        topLabel.SetToolTip(wx.ToolTip(str(rule.quality)))
        boxSizer.Add(topLabel, flag=wx.TOP | wx.BOTTOM | wx.EXPAND, border=3)
        
        boxSizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        
        for rhs in rule.rhsList:
            label = wx.StaticText(panel, label=rhs.getUnifiedString())
            label.SetBackgroundColour(wx.Color(230, 230, 255))
            # FIXME
            
            if rhs.getToolTipText() is not None:
                label.SetToolTip(wx.ToolTip(str(rhs.getToolTipText())))
            
            if rhs.hasExpansion():
                self.__subArgs[label] = rhs
                label.Bind(wx.EVT_LEFT_DCLICK, self.__expandLabel)
                label.SetBackgroundColour(wx.Color(220, 240, 240))
            boxSizer.Add(label, flag=wx.TOP | wx.BOTTOM | wx.EXPAND, border=3)
            
        boxSizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        
        endLabel = wx.StaticText(panel, label=rule.getConclusionString())
        boxSizer.Add(endLabel, flag=wx.TOP | wx.EXPAND, border=3)
            
        sizer.Add(boxSizer, flag=wx.EXPAND)
        
    def __expandLabel(self, evt):
        rhs = self.__subArgs[evt.GetEventObject()]
        
        if rhs.isArgument():
            self.showSubArgument(rhs)
        elif rhs.isSimulation():
            self.showSimulation(rhs)
        
    def showSubArgument(self, argument):
        frame = wx.Frame(self, title="Sub Argument")
        panel = ArgumentPanel(frame, argument)
        frame.Show(True)
        
    def showSimulation(self, simulation):
        self.__showGUIItem(simulation.guiItem)
            
    def __showGUIItem(self, item):
        if type(item) == type(""):
            frame = wx.Frame(self, title="Simulation")
            frame.SetBackgroundColour(wx.WHITE)
            label = wx.StaticText(frame, label=item)
            frame.Show(True)
        elif type(item) == type([]):
            for element in item:
                self.__showGUIItem(element)
        elif item.__class__.__name__ == 'SavedPlot':
            item.showFigure()
        else:
            self.showSubArgument(evidence.Argument(item))
        
            

        
        
        
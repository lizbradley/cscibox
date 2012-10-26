"""
initial_polling.py

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

This module contains stuff to ask the user for data needed to process samples
(before processing begins). This is done by creating and displaying a big ol'
wizard.
"""

import wx
import wx.wizard as wizard
import  wx.lib.intctrl as intctrl
from Calvin.reasoning import samples, confidence


def setInitialData():
    """
    Questions to ask:
    1. how many landforms do these samples represent?
    2. which samples go with which landforms?
    3. what are the expected landform ages (known and estimated)?
        - give confidences for these
    4. what are the stratographic constraints from geomorphology?
        - and possibly also for these
    (can run from here, I think)
    5. tell me about the climate of the region
    6. tell me more about these samples? (also include in matrix or not, weathering degree)
    7. might ask some general landform questions, here
    """
    if len(samples.sampleList) <= 1:
        errorDialog = wx.MessageDialog(None, 
                     "Calvin analyzes how well sample ages agree with each other " +
                     "and what processes may cause ages to disagree.\n" +
                     "Therefore, Calvin may only be run on more than one sample at a time.\n" +
                     "Calvin cannot be run on the samples you have selected.",
                     "Cannot Run Calvin", style=wx.OK)
        errorDialog.ShowModal()
        errorDialog.Destroy()
        return False
    return showWizard()
    
    #fallthrough to here means there was some error.
    
    

def showWizard():
    wiz = InitialDataWizard()

    val = wiz.runWizard()
    if val:
        wiz.setData()
    
    wiz.Destroy()
    
    return val
    
class InitialDataWizard(wizard.Wizard):
    
    def __init__(self):
        wizard.Wizard.__init__(self, None, -1, 'Polling Wizard of Doom')
        
        self.firstPage = None
        #insert a thing that checks if we can advance and vetoes if needed
        self.Bind(wizard.EVT_WIZARD_PAGE_CHANGING, self.pageChanging)
        
    def runWizard(self):
        self.firstPage = LandformCountPage(self)
        self.GetPageAreaSizer().Add(self.firstPage)
        return self.RunWizard(self.firstPage)
    
    def setData(self):
        self.firstPage.setData()
        
    def pageChanging(self, event):
        if event.GetDirection() and not self.GetCurrentPage().canAdvance():
            event.Veto()
        
        

class LandformCountPage(wizard.PyWizardPage):
    
    def __init__(self, parent):
        wizard.PyWizardPage.__init__(self, parent)
        self.parent = parent
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                                'In order to fully analyze the ages of these samples, ' +
                                'I need to ask a few questions about the ' +
                                'samples and landforms first.'))
        sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.ALL|wx.EXPAND, border=5)
        sizer.AddStretchSpacer()
        
        spinSizer = wx.BoxSizer(wx.HORIZONTAL)
        spinSizer.Add(wx.StaticText(self, -1, 'How many landforms are represented by these ' + 
                                    str(len(samples.sampleList)) + ' samples?'))
        
        self.spinner = wx.SpinCtrl(self, wx.ID_ANY)
        self.spinner.SetRange(1, len(samples.sampleList))
        self.spinner.SetValue(1)
        
        spinSizer.Add(self.spinner)
        sizer.Add(spinSizer)
        
        self.choices = self.__getAgeChoices()
        self.ageInput = wx.RadioBox(self, wx.ID_ANY, 
                                    "Which 'age' attribute should analysis be based on?", 
                                    choices=self.choices,
                                    majorDimension=1)
        
        sizer.Add(self.ageInput, flag=wx.ALL|wx.CENTER, border=5)
        sizer.AddStretchSpacer()
        
        self.SetSizer(sizer)
        
        self.nextPage = LandformAssortPage(self.parent, self)
        
    def __getAgeChoices(self):
        agevals = {}
        
        for sample in samples.sampleList:
            ages = sample.getKeysContaining('age')
            for age in ages:
                if sample.has_key(age + ' uncertainty'):
                    if agevals.has_key(age):
                        agevals[age] += 1
                    else:
                        agevals[age] = 1
                        
        choices = []
                        
        for age, count in agevals.iteritems():
            if count == len(samples.sampleList):
                choices.append(age)
                
        return choices
    
    def setData(self):
        ageValue = self.ageInput.GetStringSelection()
        samples.initEnv['age'] = ageValue
        samples.initEnv['age uncertainty'] = ageValue + ' uncertainty'
        self.nextPage.setData()
    
    def GetNext(self):
        self.nextPage.setNumLandforms(self.spinner.GetValue())
        return self.nextPage
        #next step here is to set up the landform-assort so it can add/remove without
        #too much suffering...
        #this of course should be altered to uh, not make a million fucking pages
        #that sit around and suck.
        
    def canAdvance(self):
        return True
    
    def GetPrev(self):
        return None
    
class LandformAssortPage(wizard.PyWizardPage):
    
    def __init__(self, parent, prev):
        wizard.PyWizardPage.__init__(self, parent)
        
        self.parent = parent
        self.landformItems = []
        self.numLandforms = 0
        self.prevPage = prev
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Please assign samples to landforms'))
        
        self.scroller = wx.ScrolledWindow(self, wx.ID_ANY)
        
        self.scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scroller.SetSizer(self.scrollSizer)
        self.scroller.SetScrollRate(0, 20)
        
        self.nextPage = LandformRelationPage(self.parent, self.numLandforms, self)
            
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(self.scroller, flag=wx.EXPAND|wx.RIGHT, border=4, proportion=1)
        
        uncatSizer = wx.BoxSizer(wx.VERTICAL)
        uncatSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Unassigned Samples'))
        
        self.sampleBox = SampleList(self)
        self.sampleBox.addSamples(samples.sampleList)
        
        uncatSizer.Add(self.sampleBox, flag=wx.EXPAND, proportion=1)
        hSizer.Add(uncatSizer, flag=wx.EXPAND)
        sizer.Add(hSizer, flag=wx.EXPAND, proportion=1)
        
        self.setNumLandforms(1)
        self.SetSizer(sizer)
        
    def setNumLandforms(self, numLandforms):
        if numLandforms == self.numLandforms:
            #don't need to do anything here
            return
        
        #number of landforms changed. For now, just clear and restart everything
        self.numLandforms = numLandforms
        
        for item in self.landformItems:
            self.scrollSizer.Remove(item)
            item.Destroy()
        
        self.landformItems = []
        self.sampleBox.Clear()
        
        for i in xrange(numLandforms):
            item = LandformAssortItem(self.scroller, i+1, self)
            self.landformItems.append(item)
            self.scrollSizer.Add(item, flag=wx.RIGHT, border=25)
            
        if self.numLandforms > 1:
            self.sampleBox.addSamples(samples.sampleList)
        else:
            self.landformItems[0].addSamples(samples.sampleList)
            
        self.scrollSizer.Layout()
        self.scroller.FitInside()
        
        #horrible horrible hack
        self.nextPage = LandformRelationPage(self.parent, self.numLandforms, self)
        
    def GetNext(self):
        if self.numLandforms > 1:
            return self.nextPage
        else:
            return None
    
    def GetPrev(self):
        return self.prevPage
    
    def grabSelected(self):
        return self.sampleBox.removeSelectedSamples()
    
    def addItems(self, items):
        self.sampleBox.addSamples(items)
        
    def setData(self):
        for item in self.landformItems:
            item.setData()
        self.nextPage.setData()
            
    def canAdvance(self):
        #should really pop up an error message here...
        return all([item.canAdvance() for item in self.landformItems]) and \
               self.sampleBox.GetCount() == 0
        
        
class LandformAssortItem(wx.Panel):
    def __init__(self, parent, index, realparent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        #put this sucker in a cute little box, please
        box = wx.StaticBox(self, wx.ID_ANY, 'Landform ' + str(index))
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.parent = realparent
        
        formSizer = wx.BoxSizer(wx.VERTICAL)
        
        typeSizer = self.__getTitledSizer(wx.HORIZONTAL, "Type (e.g. 'moraine'): ")
        
        self.typeInput = wx.TextCtrl(self)
        typeSizer.Add(self.typeInput)
        formSizer.Add(typeSizer, flag=wx.EXPAND)
        
        estSizer = self.__getTitledSizer(wx.HORIZONTAL, 'Estimated Age (if any): ')
        
        self.ageInput = self.__getIntCtrl()
        estSizer.Add(self.ageInput)
        formSizer.Add(estSizer, flag=wx.EXPAND)
        
        self.confBox = wx.RadioBox(self, wx.ID_ANY, 'Confidence in estimate',
                                   choices=['low', 'moderate', 'high', 'certain'],
                                   majorDimension=2)
        formSizer.Add(self.confBox, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=7)
        
        knownSizer = self.__getTitledSizer(wx.HORIZONTAL, 'Known age (if any): \n' +
                                                        '  (e.g. from other isotopes)')
        
        self.knownInput = self.__getIntCtrl()
        knownSizer.Add(self.knownInput, flag=wx.ALIGN_CENTER_VERTICAL)
        formSizer.Add(knownSizer, flag=wx.EXPAND)
        
        minSizer = self.__getTitledSizer(wx.HORIZONTAL, 'Absolute minimum age (if any): \n' +
                                                        '  (e.g. from 14C limits)')
        
        self.minInput = self.__getIntCtrl()
        minSizer.Add(self.minInput, flag=wx.ALIGN_CENTER_VERTICAL)
        formSizer.Add(minSizer, flag=wx.EXPAND)
        
        maxSizer = self.__getTitledSizer(wx.HORIZONTAL, 'Absolute maximum age (if any): \n' +
                                                        '  (e.g. from 14C limits)')
        
        self.maxInput = self.__getIntCtrl()
        maxSizer.Add(self.maxInput, flag=wx.ALIGN_CENTER_VERTICAL)
        formSizer.Add(maxSizer, flag=wx.EXPAND)
        
        sizer.Add(formSizer, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=7, proportion=1)
        
        sampleSizer = self.__getTitledSizer(wx.VERTICAL, 
                                            'Samples in Landform ' + str(index), False)
        
        self.sampleBox = SampleList(self)
        sampleSizer.Add(self.sampleBox, flag=wx.EXPAND, proportion=1)
        sizer.Add(sampleSizer, flag=wx.EXPAND)
        
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        leftButton = wx.Button(self, wx.ID_ANY, '<-', style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.onLeft, leftButton)
        rightButton = wx.Button(self, wx.ID_ANY, '->', style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.onRight, rightButton)
        
        buttonSizer.AddStretchSpacer()
        buttonSizer.Add(leftButton, flag=wx.ALL, border=10)
        buttonSizer.Add(rightButton, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        buttonSizer.AddStretchSpacer()
        sizer.Add(buttonSizer, flag=wx.EXPAND)
        
        self.SetSizer(sizer)
        
    def onLeft(self, evt):
        self.sampleBox.addSamples(self.parent.grabSelected())
        
    def onRight(self, evt):
        self.parent.addItems(self.sampleBox.removeSelectedSamples())
        
    def addSamples(self, samples):
        self.sampleBox.addSamples(samples)
        
    def __getIntCtrl(self):
        input = intctrl.IntCtrl(self)
        input.SetMin(0)
        input.SetLimited(True)
        input.SetNoneAllowed(True)
        input.SetValue(None)
        
        return input
    
    def __getTitledSizer(self, orient, title, spacer=True):
        sizer = wx.BoxSizer(orient)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, title, style=wx.ALIGN_CENTER), 
                  flag=wx.EXPAND|wx.ALL, border=3)
        if spacer:
            sizer.AddStretchSpacer()
        
        return sizer
    
    def setData(self):
        data = {'type':self.typeInput.GetValue()}
        confData = {}
        if self.ageInput.GetValue() is not None:
            data['estimated age'] = self.ageInput.GetValue()
            confData['estimated age'] = confidence.Validity.getValidity(self.confBox.GetSelection())
        if self.minInput.GetValue() is not None:
            data['known minimum age'] = self.minInput.GetValue()
        if self.maxInput.GetValue() is not None:
            data['known maximum age'] = self.maxInput.GetValue()
        if self.knownInput.GetValue() is not None:
            data['known age'] = self.knownInput.GetValue()
            
        samples.landformQueue.append((data, confData,
                                      self.sampleBox.getAllData()))
        
    def canAdvance(self):
        return len(self.typeInput.GetValue()) > 0 and self.sampleBox.GetCount() > 0
    
class SampleList(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, wx.ID_ANY, style=wx.LB_EXTENDED)
        
    def addSamples(self, samples):
        for sample in samples:
            self.addSample(sample)
            
    def addSample(self, sample):
        self.Append(str(sample), sample)
        
    def removeSelectedSamples(self):
        """
        removes all samples currently selected and returns a list
        of the samples removed.
        """
        sels = [item for item in self.GetSelections()]
        selData = [self.GetClientData(ind) for ind in sels]
    
        sels.sort(reverse=True)
        for selection in sels:
            self.Delete(selection)
        
        return selData
    
    def getAllData(self):
        return [self.GetClientData(index) for index in xrange(self.GetCount())]
        
        
class LandformRelationPage(wizard.PyWizardPage):
    def __init__(self, parent, numLandforms, prev):
        wizard.PyWizardPage.__init__(self, parent)
        self.prevPage = prev
        
        self.relations = []
        self.formList = ['Landform ' + str(i+1) for i in xrange(numLandforms)]
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                                'Tell me about any stratographic relationships ' +
                                'between these landforms'))
        
        self.scroller = wx.ScrolledWindow(self, wx.ID_ANY)
        
        self.scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scroller.SetSizer(self.scrollSizer)
        self.scroller.SetScrollRate(0, 20)
        
        sizer.Add(self.scroller, flag=wx.EXPAND, proportion=1)
        
        self.addButton = wx.Button(self, wx.ID_ANY, 'Add Relationship')
        self.Bind(wx.EVT_BUTTON, self.addItem, self.addButton)
        sizer.Add(self.addButton, flag=wx.ALL, border=5)
        
        self.addItem(None)
        
        self.SetSizer(sizer)
        
    def addItem(self, evnt):
        relation = RelationItem(self.scroller, self, self.formList)
        self.relations.append(relation)
        self.scrollSizer.Add(relation)
        
        self.scrollSizer.Layout()
        self.scroller.FitInside()
        
    def deleteItem(self, item):
        del self.relations[self.relations.index(item)]
        
        self.scrollSizer.Layout()
        self.scroller.FitInside()
        
    def GetNext(self):
        return None
    
    def GetPrev(self):
        return self.prevPage
    
    def setData(self):
        for item in self.relations:
            item.setData()
        
    def canAdvance(self):
        return True
        
        
class RelationItem(wx.Panel):
    relations = ['>', '<', '~=']
    def __init__(self, parent, realParent, formList):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self.parent = realParent
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.firstCombo = wx.Choice(self, wx.ID_ANY, choices=formList)
        sizer.Add(self.firstCombo, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        
        self.compCombo = wx.Choice(self, wx.ID_ANY, choices=self.relations)
        sizer.Add(self.compCombo, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        
        self.secondCombo = wx.Choice(self, wx.ID_ANY, choices=formList)
        sizer.Add(self.secondCombo, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        
        self.confBox = wx.RadioBox(self, wx.ID_ANY, 'Confidence',
                                   choices=['low', 'moderate', 'high', 'certain'])
        sizer.Add(self.confBox)
        
        self.removeButton = wx.Button(self, wx.ID_ANY, 'Remove')
        self.Bind(wx.EVT_BUTTON, self.removeMe, self.removeButton)
        sizer.Add(self.removeButton, flag=wx.LEFT|wx.ALIGN_CENTER, border=10)
        
        self.SetSizer(sizer)
        
    def removeMe(self, evt):
        self.Show(False)
        self.parent.deleteItem(self)
        self.Destroy()
        
    def setData(self):
        if self.firstCombo.GetSelection() >= 0 and self.compCombo.GetSelection() >= 0 and \
           self.secondCombo.GetSelection() >= 0 and \
           self.firstCombo.GetSelection() != self.secondCombo.GetSelection():
            ageFld = samples.initEnv['age']
            if self.compCombo.GetSelection() < 2:
                if self.compCombo.GetSelection() == 0:
                    larger = self.firstCombo.GetSelection()
                    smaller = self.secondCombo.GetSelection()
                else:
                    smaller = self.firstCombo.GetSelection()
                    larger = self.secondCombo.GetSelection()
                
                smallMin = reduce(lambda x, y: samples.sampleMin(x, y, ageFld), 
                                  samples.landformQueue[smaller][2])[ageFld]
                largeMax = reduce(lambda x, y: samples.sampleMax(x, y, ageFld), 
                                  samples.landformQueue[larger][2])[ageFld]
                                  
                samples.landformQueue[smaller][0]['stratographic maximum age'] = largeMax
                samples.landformQueue[smaller][1]['stratographic maximum age'] = \
                    confidence.Validity.getValidity(self.confBox.GetSelection())
                samples.landformQueue[larger][0]['stratographic minimum age'] = smallMin
                samples.landformQueue[larger][1]['stratographic minimum age'] = \
                    confidence.Validity.getValidity(self.confBox.GetSelection())
            else: #~= case
                secondList = samples.landformQueue[self.secondCombo.GetSelection()][2]
                sum = reduce(lambda x, y: x + y, 
                             [sample[ageFld] for sample in secondList], 
                             0)
                l = len(secondList)
                if l == 0:
                    l = 1
                avg = sum / l
                
                landform = self.firstCombo.GetSelection()
                
                #not sure this is the right approach but we'll give it a try
                samples.landformQueue[landform][0]['estimated age'] = avg
                samples.landformQueue[landform][1]['estimated age'] = \
                    confidence.Validity.getValidity(self.confBox.GetSelection())
            
        
        
        
        
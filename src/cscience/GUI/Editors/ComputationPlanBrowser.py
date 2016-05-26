"""
ComputationPlanBrowser.py

* Copyright (c) 2006-2013, University of Colorado.
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

import os
import itertools

import wx
import wx.wizard
import  wx.lib.scrolledpanel as scrolled

from cscience import datastore
from cscience.GUI.Editors import MemoryFrame
from cscience.GUI import grid
from cscience.GUI import events
from cscience.framework import Workflow, ComputationPlan, View

datastore = datastore.Datastore()

class CplanGridTable(grid.UpdatingTable):
    def __init__(self, *args, **kwargs):
        self._plans = []
        self.names = []
        super(CplanGridTable, self).__init__(*args, **kwargs)

    @property
    def plans(self):
        return self._plans
    @plans.setter
    def plans(self, value):
        self._plans = value
        if value:
            names = set()
            for plan in value:
                names.update(plan.keys())
            names.remove('name')
            self.names = sorted(list(names))
        else:
            self.names = []
        self.reset_view()

    def raw_value(self, row, col):
        return str(self.plans[col][self.names[row]])
    def GetNumberRows(self):
        return len(self.names) or 1
    def GetNumberCols(self):
        return len(self.plans) or 1
    def GetValue(self, row, col):
        if not self.plans:
            return "Select one or more Computation Plans"
        return self.raw_value(row, col)
    def GetRowLabelValue(self, row):
        if not self.plans:
            return ''
        return self.names[row]
    def GetColLabelValue(self, col):
        if not self.plans:
            return "No Computation Plans Selected"
        return self.plans[col].name

class ComputationPlanBrowser(MemoryFrame):
    framename = 'cplanbrowser'

    class FlowDisplayPanel(scrolled.ScrolledPanel):

        class ComponentBlock(wx.Panel):
            def __init__(self, parent, name):
                    super(ComputationPlanBrowser.FlowDisplayPanel.ComponentBlock,
                          self).__init__(parent, wx.ID_ANY)
                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    self.arrow = wx.StaticBitmap(self, wx.ID_ANY,
                                       wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD))
                    self.compname = wx.StaticText(self, wx.ID_ANY, name,
                                       style=wx.ALIGN_CENTER | wx.BORDER_SIMPLE)
                    sizer.Add(self.arrow, flag=wx.ALL, border=5)
                    sizer.Add(self.compname, flag=wx.ALL, border=5)
                    self.SetSizer(sizer)


        def __init__(self, parent):
            super(ComputationPlanBrowser.FlowDisplayPanel, self).__init__(parent,
                                                        style=wx.BORDER_SUNKEN)
            self.SetBackgroundColour('white')
            self._workflow = None
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(sizer)
            self.SetupScrolling()

        @property
        def workflow(self):
            return self._workflow

        @workflow.setter
        def workflow(self, wname):
            self._workflow = datastore.workflows[wname]
            def addcomp(sizer, component):
                hsizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(hsizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
                hsizer.Add(ComputationPlanBrowser.FlowDisplayPanel.ComponentBlock(
                        self, component), border=5,
                        flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_LEFT)
                children = self._workflow.connections[component].values()
                if children:
                    childsizer = wx.BoxSizer(wx.VERTICAL)
                    hsizer.Add(childsizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
                    for child in children:
                        addcomp(childsizer, child)

            self.DestroyChildren()
            self.Sizer.Add(wx.StaticText(self, wx.ID_ANY, "<START>"),
                      border=10, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.TOP | wx.BOTTOM)
            #single entry point is assumed, so no need to do anything additional
            #here re: vertical display
            addcomp(self.Sizer, self._workflow.find_first_component())
            self.Layout()
            self.SetupScrolling()

    def __init__(self, parent):
        super(ComputationPlanBrowser, self).__init__(parent, id=wx.ID_ANY,
                                        title='Computation Plan Browser')

        menu_bar = wx.MenuBar()
        edit_menu = wx.Menu()
        copy_item = edit_menu.Append(wx.ID_COPY, "Copy\tCtrl-C",
                                     "Copy selected computation details")
        edit_menu.Enable(wx.ID_COPY, False)
        menu_bar.Append(edit_menu, "Edit")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.copy, copy_item)

        self.CreateStatusBar()

        flowwin = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)
        flowwin.SetMinimumPaneSize(100)
        self.flowpanel = ComputationPlanBrowser.FlowDisplayPanel(flowwin)

        treewin =  wx.SplitterWindow(flowwin, wx.ID_ANY, style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)
        treewin.SetMinimumPaneSize(100)
        treepanel = wx.Panel(treewin)
        self.planlist = wx.ListBox(treepanel, wx.ID_ANY, style=wx.LB_SINGLE,
                                   choices=["Computation Plans"])
        self.add_button = wx.Button(treepanel, wx.ID_ANY, "Create New Plan...")

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.add_button, border=5, flag=wx.ALL)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.planlist, flag=wx.EXPAND, proportion=1)
        sz.Add(buttonsizer)
        treepanel.SetSizer(sz)

        self.grid = grid.LabelSizedGrid(treewin, wx.ID_ANY)
        self.table = CplanGridTable(self.grid)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)

        treewin.SplitVertically(treepanel, self.grid)
        flowwin.SplitHorizontally(treewin, self.flowpanel)

        self.update_plans()

        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.allow_copy, self.grid)
        self.Bind(events.EVT_REPO_CHANGED, self.on_repository_altered)
        self.Bind(wx.EVT_LISTBOX, self.select_plan, self.planlist)
        self.Bind(wx.EVT_BUTTON, self.create_plan, self.add_button)
        self.SetSizer(None)


    def allow_copy(self, event):
        menu_bar = self.GetMenuBar()
        edit = menu_bar.GetMenu(menu_bar.FindMenu("Edit"))
        edit.Enable(wx.ID_COPY, bool(self.grid.SelectedRows))

    def copy(self, event):
        rowtext = ['\t'.join([plan.name for plan in self.table.plans])]
        for row in self.grid.SelectedRows:
            rowtext.append('\t'.join([self.table.GetRowLabelValue(row)] +
                                     [self.table.raw_value(row, col) for col in
                                      range(self.table.GetNumberCols())]))

        data = wx.TextDataObject()
        data.SetText(os.linesep.join(rowtext))
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def on_repository_altered(self, event):
        if 'cplans' in event.changed:
            self.update_plans()
        event.Skip()

    def update_plans(self):
        self.planlist.SetItems(datastore.computation_plans.keys())

    def create_plan(self, event):
        wiz = PlanWizard(self)
        if wiz.RunWizard():
            plan = wiz.make_plan()
            datastore.computation_plans.add(plan)
            events.post_change(self, 'cplans', plan.name)

            v = View('Data For "%s"' % plan.name)
            atts = datastore.workflows[plan.workflow].find_attributes()
            atts.difference_update(v)
            v.extend(atts)
            datastore.views.add(v)
            events.post_change(self, 'views', v.name)
            
        wiz.Destroy()

    def select_plan(self, event):
        item = self.planlist.GetStringSelection()
        try:
            plan = datastore.computation_plans[item]
        except KeyError:
            pass
        else:
            self.grid.ClearSelection()
            #TODO: clearly it's silly to view this in a grid...
            #Maybe sort by workflow? is that useful?
            self.table.plans = [plan]
            self.flowpanel.workflow = plan['workflow']


class WorkflowDialog(wx.Dialog):
    #TODO: I plan to replace all this with an OGL panel in the future...
    #TODO: allow multiple input/ output ports...
    class FlowPanel(scrolled.ScrolledPanel):

        class ComponentBlock(wx.Panel):

            def __init__(self, parent, index):
                super(WorkflowDialog.FlowPanel.ComponentBlock, self).__init__(
                                                            parent, wx.ID_ANY)
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.index = index
                self.arrow = wx.StaticBitmap(self, wx.ID_ANY,
                                   wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD))
                self.compchoice = wx.Choice(self, wx.ID_ANY,
                        choices=['<End Here>'] + datastore.component_library.keys())
                sizer.Add(self.arrow, flag=wx.ALL, border=5)
                sizer.Add(self.compchoice, flag=wx.ALL, border=5)
                self.SetSizer(sizer)


        def __init__(self, parent):
            super(WorkflowDialog.FlowPanel, self).__init__(parent,
                                                        style=wx.BORDER_SUNKEN)
            self.SetBackgroundColour('white')
            self.components = []
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, "<START>"), border=10,
                      flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.TOP | wx.BOTTOM)
            self.SetSizer(sizer)
            self.add_block()

        def add_block(self):
            newcomp = WorkflowDialog.FlowPanel.ComponentBlock(self, len(self.components))
            self.Bind(wx.EVT_CHOICE, self.change_component, newcomp.compchoice)
            self.Sizer.Add(newcomp, flag=wx.ALL, border=5)
            self.components.append(newcomp)
            self.SetupScrolling()

        def change_component(self, event):
            block = event.EventObject.Parent.index
            selection = event.Int
            if selection > 0:
                self.add_block()
            else:
                for component in self.components[block+1:]:
                    component.Destroy()

        def save_flow(self, workflow):
            #add first component to make sure it's there (in case we have only
            #1 in the workflow, for ex)
            workflow.add_component(self.components[0].compchoice.StringSelection)
            source, dest = itertools.tee(self.components)
            next(dest, None)
            for s, d in itertools.izip(source, dest):
                if d.compchoice.Selection > 0:
                    workflow.connect(s.compchoice.StringSelection,
                                     d.compchoice.StringSelection)


    def __init__(self, parent):
        #TODO: validation & error handling!
        super(WorkflowDialog, self).__init__(parent, wx.ID_ANY,
                    "Create New Method", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.nameentry = wx.TextCtrl(self, wx.ID_ANY, size=(150, -1))
        self.flowpanel = WorkflowDialog.FlowPanel(self)

        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(wx.StaticText(self, wx.ID_ANY, "Method Name:"), flag=wx.ALL|wx.CENTER,
               border=5)
        sz.Add(self.nameentry, flag=wx.ALL, border=5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sz)
        sizer.Add(self.flowpanel, proportion=3, flag=wx.EXPAND | wx.ALL, border=10)
        #TODO: actually set up live-updating details...
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Method Details"), proportion=1,
                  flag=wx.EXPAND | wx.ALL, border=10)
        btsizer = wx.BoxSizer(wx.HORIZONTAL)
        btsizer.Add(wx.Button(self, wx.ID_OK, 'Save'), flag=wx.RIGHT, border=10)
        btsizer.Add(wx.Button(self, wx.ID_CANCEL))
        sizer.Add(btsizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        self.SetSizer(sizer)

    def do_save(self):
        wname = self.nameentry.GetValue().strip()
        if not wname:
            wx.MessageBox("Please enter a name for this workflow",
                          "Name Required", wx.OK | wx.ICON_INFORMATION)
            return None
        workflow = Workflow(wname)
        self.flowpanel.save_flow(workflow)
        datastore.workflows.add(workflow)
        return workflow


class PlanWizard(wx.wizard.Wizard):

    class FramePage(wx.wizard.WizardPageSimple):
        #TODO: force workflow selection before adding next.
        def __init__(self, parent):
            super(PlanWizard.FramePage, self).__init__(parent)
            title = wx.StaticText(self, wx.ID_ANY, "Set Plan Name and Method")
            font = title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            title.SetFont(font)

            self.planname = wx.TextCtrl(self, wx.ID_ANY, size=(200, -1))
            self.flowchoice = wx.Choice(self, wx.ID_ANY,
                                        choices=datastore.workflows.keys())
            newbutton = wx.Button(self, wx.ID_ANY, "Create New Method...")

            #TODO: set up a little workflow viewer-panel for great justice.
            """
            flowbox = wx.StaticBox(self, wx.ID_ANY)
            flowsz = wx.StaticBoxSizer(flowbox, wx.HORIZONTAL)
            self.flowpanel = PlanWizard.FlowPanel(self)
            self.flowpanel.Disable()
            flowsz.Add(self.flowpanel, flag=wx.EXPAND, proportion=1)
            """

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self, wx.ID_ANY, 'Computation Plan Name:'),
                   flag=wx.ALL | wx.CENTER, border=5)
            sz.Add(self.planname, flag=wx.ALL, border=5)
            sizer.Add(sz, flag=wx.EXPAND)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self, wx.ID_ANY, "Use Method:"),
                      flag=wx.ALL | wx.CENTER, border=5)
            sz.Add(self.flowchoice, flag=wx.ALL, border=5)
            sz.Add(newbutton, flag=wx.ALL, border=5)
            sizer.Add(sz, flag=wx.EXPAND)
            self.SetSizer(sizer)

            self.Bind(wx.EVT_BUTTON, self.on_make_new, newbutton)

        @property
        def name(self):
            return self.planname.Value

        @property
        def workflow(self):
            return self.flowchoice.StringSelection

        def on_make_new(self, event):
            dialog = WorkflowDialog(self)
            while dialog.ShowModal() == wx.ID_OK:
                newflow = dialog.do_save()
                if newflow:
                    #current implementation of event seems to need to post it
                    #from an actual app-window, which is this window's grandparent, so...
                    events.post_change(self.GrandParent, 'workflows')
                    self.flowchoice.Append(newflow.name)
                    self.flowchoice.SetStringSelection(newflow.name)
                    break
            dialog.Destroy()

    class ParamPage(wx.wizard.WizardPageSimple):
        def __init__(self, parent):
            super(PlanWizard.ParamPage, self).__init__(parent)
            title = wx.StaticText(self, wx.ID_ANY, "Set Plan Parameters")
            font = title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            title.SetFont(font)

            self.parmframe = scrolled.ScrolledPanel(self)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sizer.Add(self.parmframe, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
            self.SetSizer(sizer)

        def for_workflow(self, workflow):
            self.parmframe.DestroyChildren()
            workflow = datastore.workflows[workflow]
            sizer = wx.FlexGridSizer(0, 2, 5, 5)
            self.parmframe.SetSizer(sizer)
            self.parameter_controls = {}
            for param in workflow.find_parameters():
                #TODO: filter choices here by whether it has the required fields.
                sel = wx.Choice(self.parmframe, wx.ID_ANY, choices=datastore.milieus.keys())
                sizer.Add(wx.StaticText(self.parmframe, wx.ID_ANY, '%s:' % param))
                sizer.Add(sel)
                self.parameter_controls[param] = sel
            sizer.AddGrowableCol(1)
            self.parmframe.SetupScrolling()

        @property
        def parameters(self):
            return dict([(name, cont.StringSelection) for
                         name, cont in self.parameter_controls.iteritems()])


    def __init__(self, parent):
        #TODO: this can have a bmp, which would be pretty handy actually
        super(PlanWizard, self).__init__(parent, wx.ID_ANY, "Create Computation Plan",
                                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.framepage = PlanWizard.FramePage(self)
        self.parmpage = PlanWizard.ParamPage(self)

        wx.wizard.WizardPageSimple_Chain(self.framepage, self.parmpage)
        self.GetPageAreaSizer().Add(self.framepage)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.update_parmpage)

    def update_parmpage(self, event):
        if event.GetDirection() and hasattr(event.Page, 'workflow'):
            self.parmpage.for_workflow(event.Page.workflow)

            if not event.Page.name:
                wx.MessageBox("Please enter a name for this computation plan",
                              "Name Required", wx.OK | wx.ICON_INFORMATION)
                event.Veto()
                return
            if not event.Page.workflow:
                wx.MessageBox("You need to select a method for this computation plan",
                              "Workflow Required", wx.OK | wx.ICON_INFORMATION)
                event.Veto()
                return
        event.Skip()

    def make_plan(self):
        plan = ComputationPlan(self.framepage.name)
        plan['workflow'] = self.framepage.workflow
        plan.update(self.parmpage.parameters)
        return plan

    def RunWizard(self):
        return super(PlanWizard, self).RunWizard(self.framepage)

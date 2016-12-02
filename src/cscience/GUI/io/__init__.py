import os
import csv
import shutil
import tempfile
import json
import random
from collections import namedtuple

import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled
import bagit

from cscience import datastore
from cscience.GUI import grid
from cscience.framework import samples, datastructures

import LiPD_reader as lipd

datastore = datastore.Datastore()

class ImportWizard(wx.wizard.Wizard):
    #TODO: fix back & forth to actually work.

    def __init__(self, parent):
        super(ImportWizard, self).__init__(parent, wx.ID_ANY, "Import Samples",
                                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.corepage = ImportWizard.CorePage(self)
        self.fieldpage = ImportWizard.FieldPage(self)
        self.confirmpage = ImportWizard.ConfirmPage(self)
        self.successpage = ImportWizard.SuccessPage(self)

        wx.wizard.WizardPageSimple_Chain(self.corepage, self.fieldpage)
        wx.wizard.WizardPageSimple_Chain(self.fieldpage, self.confirmpage)
        wx.wizard.WizardPageSimple_Chain(self.confirmpage, self.successpage)

        #we seem to need to add all the pages to the pageareasizer manually
        #or the next/back buttons move around on resize, whee!
        self.GetPageAreaSizer().Add(self.corepage)
        self.GetPageAreaSizer().Add(self.fieldpage)
        self.GetPageAreaSizer().Add(self.confirmpage)
        self.GetPageAreaSizer().Add(self.successpage)
        self.temp = lipd.TemporaryDirectory()
        self.tempdir = self.temp.get_name()

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.dispatch_changing)

    @property
    def saverepo(self):
        return self.successpage.dosave
    @property
    def swapcore(self):
        return self.successpage.doswap
    @property
    def corename(self):
        return self.corepage.core_name

    def RunWizard(self):
        dialog = wx.FileDialog(self,
                               "Please select a LiPD file containing sample data",
                               defaultDir=os.getcwd(),
                               wildcard="CSV Files (*.lpd)|*.zip|All Files|*.*",
                               style=wx.OPEN | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        self.path = dialog.GetPath()
        #destroy the dialog now so no problems happen on early return
        dialog.Destroy()
        # TODO: adapt the import to handle LiPD data.
        # Should use the bagit utility to check to make sure the data is not corrupt
        if result != wx.ID_OK:
            return False

        self.data = lipd.readLiPD(self.tempdir,self.path)

        # strip extra spaces, so users don't get baffled
        self.corepage.setup(self.data)

        #self.files = ([i["filename"] for j in self.data.get("paleoData",[]) for i in j.get("paleoMeasurementTable",[])]
        #    + [i["filename"] for j in self.data.get("chronData",[]) for i in j.get("chronMeasurementTable",[])])

        ret = super(ImportWizard, self).RunWizard(self.corepage)
        self.temp.cleanup()
        return ret

    def dispatch_changing(self, event):
        #TODO: handle back as well; do enough cleanup it all works...
        if event.Direction:
            if event.Page is self.corepage:
                self.confirm_core_data(event)
            elif event.Page is self.fieldpage:
                self.do_file_read(event)
            elif event.Page is self.confirmpage:
                self.do_sample_import(event)

    def confirm_core_data(self, event):
        if not self.corename:
            wx.MessageBox("Please assign a name to this core before continuing.",
                          "Core Name Required", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return
        elif self.corepage.new_core.GetValue() and self.corename in datastore.cores:
            wx.MessageBox("You already have a core named %s. Please choose the "
                          "existing core option or enter a different name." %
                          self.corename,
                          "Core Name Duplicate", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return

        try:
            latlng = self.corepage.latlng
        except (TypeError, ValueError):
            wx.MessageBox("Please enter a valid latitude and longitude for this core",
                          "Lat/Long Required", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return

        if latlng[0] < -90 or latlng[0] > 90:
            wx.MessageBox("Invalid latitude value",
                          "Invalid Latitude", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return
        if latlng[1] < -180 or latlng[1] > 180:
            wx.MessageBox("Invalid longitude value",
                          "Invalid Longitude", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return

        self.fieldpage.setup(self.data)

    def do_file_read(self, event):
        self.fielddict = dict([w.fieldassoc for w in self.fieldpage.fieldwidgets
                               if w.fieldassoc])
        if 'depth' not in self.fielddict.values():
            wx.MessageBox("Please assign a column for sample depth before continuing.",
                          "Depth Field Required", wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return
        self.unitdict = dict([w.unitassoc for w in self.fieldpage.fieldwidgets
                              if w.unitassoc])
        self.errdict = dict([w.errassoc for w in self.fieldpage.fieldwidgets
                             if w.errassoc])
        self.errconv = {}
        for key, val in self.errdict.iteritems():
            for v in val:
                self.errconv[v] = key

        self.rows = []

        print self.fielddict

        pdata = {k.get("variableName",""):k.get("data",[])
            for j in self.data.get("paleoData",[])
            for i in j.get("paleoMeasurementTable",[])
            for k in i.get("columns",{})
            if k.get(u"variableName") in self.fielddict}

        cdata = {k.get("variableName"): k.get("data",[])
            for j in self.data.get("chronData",[])
            for i in j.get("chronMeasurementTable",[])
            for k in i.get("columns",{})
            if k.get(u"variableName") in self.fielddict}


        pflipped = [{} for i in pdata["depth"]]
        cflipped = [{} for i in cdata["depth"]]

        for key,value in pdata.iteritems():
            for i in range(len(value)):
                pflipped[i][key] = value[i]

        for key,value in cdata.iteritems():
            for i in range(len(value)):
                cflipped[i][key] = value[i]

        flipped = sorted(pflipped + cflipped, key=lambda x: x["depth"])

        for index, line in enumerate(flipped, 1):
            print line
            #do appropriate type conversions...; handle units!
            newline = {}
            for key, value in line.iteritems():
                #don't try to import total blanks.
                if key in self.errconv:
                    attname = self.errconv[key]
                    fname = key
                else:
                    fname = self.fielddict.get(key, None)
                    attname = fname
                try:
                    if fname:
                        if value:
                            newline[fname] = \
                                datastore.sample_attributes.input_value(attname, value)
                        else:
                            newline[fname] = None
                except KeyError:
                    #ignore columns we've elected not to import
                    pass
                except ValueError:
                    #TODO: give ignore line/fix item/give up options
                    wx.MessageBox("%s on row %i has an incorrect type. "
                                  "Please update the csv file and try again." % (key, index),
                                  "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                    event.Veto()
                    return
            unitline = {}
            #now that we have all the values in the row, do a second pass for
            #unit & error handling
            for key, value in newline.iteritems():
                if key in self.errconv:
                    #skip error fields, they get handled with the parent.
                    continue
                att = datastore.sample_attributes[key]
                if value is None:
                    continue
                if att.is_numeric():
                    uncert = None
                    if key in self.errdict:
                        errkey = self.errdict[key]
                        if len(errkey) > 1:
                            uncert = (newline.get(errkey[0], 0), newline.get(errkey[1], 0))
                        else:
                            uncert = newline.get(errkey[0], 0)
                    unitline[key] = datastructures.UncertainQuantity(value,
                                            self.unitdict.get(key, 'dimensionless'), uncert)
                    #convert units (yay, quantities handles all that)
                    #TODO: maybe allow user to select units for display in some sane way...
                    unitline[key].units = att.unit
                else:
                    unitline[key] = value

            self.rows.append(unitline)

        #doing it this way to keep cols ordered as in source material
        imported = [self.fielddict[k] for k in cdata or k in pdata if
                    k in self.fielddict]
        self.confirmpage.setup(imported, self.rows)

    def do_sample_import(self, event):
        cname = self.corename
        core = datastore.cores.get(cname)
        if core is None:
            core = samples.Core(cname)
            datastore.cores[cname] = core
        for item in self.rows:
            # TODO -- need to update existing samples if they exist, not
            # add new ones!
            s = samples.Sample('input', item)
            core.add(s)
        all_core_properties = samples.Sample('input', {})
        source = self.corepage.source_name

        if source:
            all_core_properties['input']['Provenance'] = source

        latlng = self.corepage.latlng
        all_core_properties['input']['Core Site'] = datastructures.GeographyData(
            latlng[0], latlng[1])
        guid = self.corepage.core_guid
        if guid:
            all_core_properties['input']['Core GUID'] = guid

        core.properties = all_core_properties
        print "setting new properties for core"
        core.loaded = True

    class CorePage(wx.wizard.WizardPageSimple):
        """
        Write down core-wide data (of doom) before looking at field-specific
        correlations (also of doom)
        """

        def __init__(self, parent):
            super(ImportWizard.CorePage, self).__init__(parent)

            title = wx.StaticText(self, wx.ID_ANY, "Core Data")
            font = title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            title.SetFont(font)

            corebox = self.make_corebox()

            #ask here for lat/lng, id#, etc...
            #need pre-shown for required/common, eventually(?) add a facility to add whatever
            self.lat_entry = wx.TextCtrl(self, wx.ID_ANY)
            self.lng_entry = wx.TextCtrl(self, wx.ID_ANY)
            latlng = wx.BoxSizer(wx.HORIZONTAL)
            latlng.Add(wx.StaticText(self, wx.ID_ANY, 'Latitude +90(N) to -90(S)'),
                       flag=wx.ALIGN_CENTRE)
            latlng.Add(self.lat_entry, flag=wx.ALL, border=5)
            latlng.Add(wx.StaticText(self, wx.ID_ANY, 'Longitude +180(E) to -180(W)'),
                       flag=wx.ALIGN_CENTRE | wx.LEFT, border=5)
            latlng.Add(self.lng_entry, flag=wx.ALL, border=5)

            self.guid = wx.TextCtrl(self, wx.ID_ANY)
            gsizer = wx.BoxSizer(wx.HORIZONTAL)
            gsizer.Add(wx.StaticText(self, wx.ID_ANY, 'Global Unique Core Identifier'),
                       flag=wx.ALIGN_CENTRE)
            gsizer.Add(self.guid, flag=wx.ALL, border=5)

            self.source_panel = self.make_sourcebox()

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sizer.Add(corebox)
            sizer.Add(latlng)
            #required/optional line
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=10)
            sizer.Add(gsizer)
            sizer.Add(self.source_panel)

            self.SetSizer(sizer)

        def make_corebox(self):
            corebox = wx.Panel(self)

            self.new_core = wx.RadioButton(corebox, wx.ID_ANY, 'Create new core',
                                           style=wx.RB_GROUP)
            self.existing_core = wx.RadioButton(corebox, wx.ID_ANY, 'Add to existing core')

            self.new_core_panel = wx.Panel(corebox, size=(300, -1))
            self.core_name_box = wx.TextCtrl(self.new_core_panel, wx.ID_ANY)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(self.new_core_panel, wx.ID_ANY, 'Core Name:'),
                   border=5, flag=wx.ALL)
            sz.Add(self.core_name_box, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
            self.new_core_panel.SetSizer(sz)

            self.existing_core_panel = wx.Panel(corebox, size=(300, -1))
            cores = datastore.cores.keys()
            if not cores:
                self.existing_core.Disable()
            else:
                self.core_select = wx.ComboBox(self.existing_core_panel, wx.ID_ANY, cores[0],
                                               choices=cores, style=wx.CB_READONLY)
                sz = wx.BoxSizer(wx.HORIZONTAL)
                sz.Add(wx.StaticText(self.existing_core_panel, wx.ID_ANY, 'Select Core:'),
                       border=5, flag=wx.ALL)
                sz.Add(self.core_select, border=5, proportion=1,
                       flag=wx.ALL | wx.EXPAND)
                self.existing_core_panel.SetSizer(sz)

            rsizer = wx.BoxSizer(wx.HORIZONTAL)
            rsizer.Add(self.new_core, border=5, flag=wx.ALL)
            rsizer.Add(self.existing_core, border=5, flag=wx.ALL)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(rsizer, flag=wx.EXPAND)
            sizer.Add(self.new_core_panel, border=5, flag=wx.ALL)
            sizer.Add(self.existing_core_panel, border=5, flag=wx.ALL)
            corebox.SetSizer(sizer)

            self.Bind(wx.EVT_RADIOBUTTON, self.on_coretype, self.new_core)
            self.Bind(wx.EVT_RADIOBUTTON, self.on_coretype, self.existing_core)
            self.existing_core_panel.Hide()
            self.new_core.SetValue(True)
            return corebox

        def make_sourcebox(self):
            source_panel = wx.Panel(self)
            self.add_source_check = wx.CheckBox(source_panel, wx.ID_ANY,
                                                "Record Provenance as")
            self.source_name_input = wx.TextCtrl(source_panel, wx.ID_ANY, size=(250, -1))
            self.source_name_input.Enable(self.add_source_check.IsChecked())
            source_sizer = wx.BoxSizer(wx.HORIZONTAL)
            source_sizer.Add(self.add_source_check, border=5, flag=wx.ALL)
            source_sizer.Add(self.source_name_input, border=5, flag=wx.ALL)
            source_panel.SetSizer(source_sizer)

            self.Bind(wx.EVT_CHECKBOX, self.on_addsource, self.add_source_check)
            return source_panel

        def setup(self,data):
            #basename = os.path.splitext(os.path.basename(filepath))[0]
            self.core_name_box.SetValue(data[u"dataSetName"])
            self.source_name_input.SetValue(data[u"dataSetName"])
            self.lat_entry.SetValue(str(data[u'geo'][u'geometry'][u'coordinates'][0]))
            self.lng_entry.SetValue(str(data[u'geo'][u'geometry'][u'coordinates'][1]))

        def on_coretype(self, event):
            self.new_core_panel.Show(self.new_core.GetValue())
            self.existing_core_panel.Show(self.existing_core.GetValue())
            self.Sizer.Layout()

        def on_addsource(self, event):
            self.source_name_input.Enable(self.add_source_check.IsChecked())

        @property
        def core_name(self):
            if self.new_core.GetValue():
                return self.core_name_box.GetValue()
            else:
                return self.core_select.GetValue()

        @property
        def core_guid(self):
            return self.guid.GetValue() or None

        @property
        def latlng(self):
            return (float(),
                    float())

        @property
        def source_name(self):
            if self.add_source_check.IsChecked():
                return self.source_name_input.GetValue()
            else:
                return None

    class FieldPage(wx.wizard.WizardPageSimple):
        """
        Set up a dictionary of file field names -> cscibox field names
        -- allow on-the-fly attribute creation
        """

        class AssocSelector(wx.Panel):

            ignoretxt = "Ignore this Field"
            noerrtxt = "No Error"

            def __init__(self, parent, fielddata, allfields):
                self.fieldname = fielddata.get(u"variableName")
                self.units = fielddata.get("units")
                self.data = fielddata.get("data")
                super(ImportWizard.FieldPage.AssocSelector, self).__init__(
                    parent, style=wx.BORDER_SIMPLE)

                #import x field from csv as att...
                #TODO:this should maybe be, like, bold?
                fldlbl = wx.StaticText(self, wx.ID_ANY, self.fieldname,
                                       style=wx.ALIGN_LEFT)
                self.fcombo = wx.ComboBox(self, wx.ID_ANY, self.ignoretxt,
                                          choices=[self.ignoretxt] +
                                          [att.name for att in datastore.sample_attributes
                                          if not att.is_virtual],
                                          style=wx.CB_READONLY)

                #unit setup
                unitpanel = wx.Panel(self, wx.ID_ANY)
                self.ucombo = wx.ComboBox(unitpanel, wx.ID_ANY, choices=('dimensionless',),
                                          style=wx.CB_READONLY)
                self.unittext = wx.StaticText(unitpanel, wx.ID_ANY, 'dimensionless')
                self.unittext.SetMinSize(self.ucombo.GetSize())
                self.ucombo.SetMinSize(self.ucombo.GetSize())
                usz = wx.BoxSizer(wx.VERTICAL)
                usz.Add(self.ucombo, flag=wx.EXPAND, proportion=1)
                usz.Add(self.unittext, flag=wx.EXPAND, proportion=1)
                unitpanel.SetSizer(usz)
                self.ucombo.Hide()

                #error setup
                errchoices = ([self.noerrtxt])# +
                              #[fld[u"variableName"] for fld in allfields if u"variableName" in fld and fld[u"variableName"] != self.fieldname])
                self.errpanel = wx.Panel(self, wx.ID_ANY)
                errlbl = wx.StaticText(self.errpanel, wx.ID_ANY, 'Error:')
                self.asymcheck = wx.CheckBox(self.errpanel, wx.ID_ANY, 'asymmetric')
                self.sympanel = wx.Panel(self.errpanel, wx.ID_ANY)
                self.ecombo = wx.ComboBox(self.sympanel, wx.ID_ANY, self.noerrtxt,
                                          choices=errchoices, style=wx.CB_READONLY)
                ssz = wx.BoxSizer(wx.HORIZONTAL)
                ssz.Add(self.ecombo)
                self.sympanel.SetSizer(ssz)

                self.asympanel = wx.Panel(self.errpanel, wx.ID_ANY)
                plbl = wx.StaticText(self.asympanel, wx.ID_ANY, '+')
                mlbl = wx.StaticText(self.asympanel, wx.ID_ANY, '/ -')
                self.epcombo = wx.ComboBox(self.asympanel, wx.ID_ANY, self.noerrtxt,
                                           choices=errchoices, style=wx.CB_READONLY)
                self.emcombo = wx.ComboBox(self.asympanel, wx.ID_ANY, self.noerrtxt,
                                           choices=errchoices, style=wx.CB_READONLY)
                assz = wx.BoxSizer(wx.HORIZONTAL)
                assz.Add(plbl, border=3, flag=wx.LEFT)
                assz.Add(self.epcombo)
                assz.Add(mlbl, border=3, flag=wx.LEFT)
                assz.Add(self.emcombo)
                self.asympanel.SetSizer(assz)

                errsz = wx.BoxSizer(wx.HORIZONTAL)
                errsz.Add(errlbl, border=5, flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
                errsz.Add(self.asymcheck, border=5, flag=wx.EXPAND | wx.RIGHT)
                errsz.Add(self.sympanel, flag=wx.EXPAND, proportion=1)
                errsz.Add(self.asympanel, flag=wx.EXPAND, proportion=1)
                self.asympanel.Show(False)
                self.errpanel.SetSizer(errsz)
                self.errpanel.Show(False)

                #top layout
                sz = wx.BoxSizer(wx.HORIZONTAL)
                stacksz = wx.BoxSizer(wx.VERTICAL)
                topsz = wx.BoxSizer(wx.HORIZONTAL)

                sz.Add(fldlbl, border=5, proportion=1,
                       flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
                topsz.Add(self.fcombo, flag=wx.ALIGN_RIGHT)
                topsz.Add(unitpanel, border=5, flag=wx.RIGHT | wx.LEFT | wx.EXPAND)
                stacksz.Add(topsz, flag=wx.ALIGN_RIGHT)
                stacksz.Add(self.errpanel, flag=wx.ALIGN_LEFT | wx.EXPAND)
                sz.Add(stacksz, flag=wx.EXPAND)

                self.SetSizer(sz)

                self.Bind(wx.EVT_COMBOBOX, self.sel_field_changed, self.fcombo)
                self.Bind(wx.EVT_CHECKBOX, self.err_asym_changed, self.asymcheck)

                #try to pre-set useful associations...
                #simplest case -- using our same name.

                if self.fieldname in datastore.sample_attributes:
                    self.fcombo.SetValue(self.fieldname)
                    self.sel_field_changed()
                else:
                    #other obvious case -- name of one is extension of the other
                    for att in datastore.sample_attributes:
                        if self.fieldname in att.name or att.name in self.fieldname:
                            self.fcombo.SetValue(att.name)
                            self.sel_field_changed()
                            break
                    #TODO: dictionary of common renamings?


                #import traceback
                #traceback.print_stack()

                '''
                if self.fieldname in datastore.sample_attributes:
                    self.fcombo.SetValue(self.fieldname)
                    self.sel_field_changed()
                else:
                    #other obvious case -- name of one is extension of the other
                    for att in datastore.sample_attributes:
                        if self.fieldname in att.name or att.name in self.fieldname:
                            self.fcombo.SetValue(att.name)
                            self.sel_field_changed()
                            break
                    #TODO: dictionary of common renamings?
                '''


            def add_err_bindings(self, func):
                self.Bind(wx.EVT_COMBOBOX, func, self.ecombo)
                self.Bind(wx.EVT_COMBOBOX, func, self.epcombo)
                self.Bind(wx.EVT_COMBOBOX, func, self.emcombo)

            def err_asym_changed(self, event=None):
                isasym = self.asymcheck.GetValue()
                self.sympanel.Show(not isasym)
                self.asympanel.Show(isasym)
                self.Layout()

            def sel_field_changed(self, event=None):
                value = self.fcombo.GetValue()
                if value == self.ignoretxt:
                    unit = ''
                    unitset = ('',)
                    haserr = False
                else:
                    att = datastore.sample_attributes[value]
                    unit = str(att.unit)
                    unitset = datastructures.get_conv_units(unit)
                    haserr = att.has_error

                self.unittext.SetLabel(unitset[0])
                self.ucombo.SetItems(unitset)
                self.ucombo.SetStringSelection(unit)
                self.unittext.Show(len(unitset) == 1)
                self.ucombo.Show(len(unitset) > 1)
                self.errpanel.Show(haserr)
                self.GetParent().Layout()

            @property
            def fieldassoc(self):
                if not self.IsShown():
                    return None
                sel = self.fcombo.GetValue()
                if sel == self.ignoretxt:
                    return None
                else:
                    return (self.fieldname, sel)

            @property
            def unitassoc(self):
                if not self.ucombo.IsShown():
                    return None
                field = self.fieldassoc
                if not field:
                    return None
                sel = self.ucombo.GetValue()
                if sel:
                    return (field[1], sel)
                return None

            @property
            def selerror(self):
                if self.errpanel.IsShown():
                    if self.sympanel.IsShown():
                        sel = self.ecombo.GetValue()
                        if sel and sel != self.noerrtxt:
                            return (sel,)
                    else:
                        pos = self.epcombo.GetValue()
                        if not pos or pos == self.noerrtxt:
                            pos = None
                        neg = self.emcombo.GetValue()
                        if not neg or neg == self.noerrtxt:
                            neg = None
                        return (neg, pos)
                return None

            @property
            def errassoc(self):
                sel = self.selerror
                if sel:
                    return (self.fcombo.GetValue(), sel)
                return None


        def __init__(self, parent):
            super(ImportWizard.FieldPage, self).__init__(parent)

            self.title = wx.StaticText(self, wx.ID_ANY, "Sample Associations")
            font = self.title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            self.title.SetFont(font)

            #TODO: these could definitely be convinced to align better...
            flabelframe = wx.Panel(self)
            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.Add(wx.StaticText(flabelframe, wx.ID_ANY, 'Import Source Column'),
                   border=5, proportion=1, flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
            sz.Add(wx.StaticText(flabelframe, wx.ID_ANY, 'as CSIBox Field',
                                 style=wx.ALIGN_CENTER),
                   proportion=1, flag=wx.EXPAND)
            sz.Add(wx.StaticText(flabelframe, wx.ID_ANY, 'Source Unit'),
                   border=5, flag=wx.RIGHT | wx.LEFT | wx.EXPAND)
            flabelframe.SetSizer(sz)
            self.fieldframe = scrolled.ScrolledPanel(self)
            self.fieldwidgets = []

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sizer.Add(flabelframe, flag=wx.EXPAND)
            sizer.Add(self.fieldframe, proportion=1, flag=wx.EXPAND)

            self.SetSizer(sizer)

        def setup(self, data):
            self.title.SetLabelText('Sample Associations for "%s"' % data[u"dataSetName"])
            sz = wx.BoxSizer(wx.VERTICAL)

            for i in data[u"chronData"]:
                for j in i[u"chronMeasurementTable"]:
                    for k in j[u"columns"]:
                        widg = ImportWizard.FieldPage.AssocSelector(self.fieldframe, k, j[u"columns"])
                        widg.add_err_bindings(self.hideused)
                        self.fieldwidgets.append(widg)
                        sz.Add(widg, flag=wx.EXPAND)
            """
            for i in data[u"paleoData"]:
                for j in i[u"paleoMeasurementTable"]:
                    for k in j[u"columns"]:
                        widg = ImportWizard.FieldPage.AssocSelector(self.fieldframe, k, j[u"columns"])
                        widg.add_err_bindings(self.hideused)
                        self.fieldwidgets.append(widg)
                        sz.Add(widg, flag=wx.EXPAND)
            """
            self.fieldframe.SetSizer(sz)
            self.fieldframe.SetupScrolling()

            self.Sizer.Layout()

        def hideused(self, event=None):
            errs = []
            for widg in self.fieldwidgets:
                err = widg.selerror
                if err:
                    errs.extend(err)

            for widg in self.fieldwidgets:
                widg.Show(widg.fieldname not in errs)

            self.Layout()

    class ConfirmPage(wx.wizard.WizardPageSimple):

        def __init__(self, parent):
            super(ImportWizard.ConfirmPage, self).__init__(parent)

            title = wx.StaticText(self, wx.ID_ANY, "Confirm Import")
            font = title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            title.SetFont(font)

            self.gridpanel = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sizer.Add(self.gridpanel, proportion=1, flag=wx.EXPAND)
            sizer.Add(wx.StaticText(self, wx.ID_ANY,
                      "Press 'Next' to import these samples as displayed"),
                      border=5, flag=wx.ALL | wx.ALIGN_RIGHT)

            self.SetSizer(sizer)

        def setup(self, fields, rows):
            #TODO: add some text about new/existing core, core name

            g = grid.LabelSizedGrid(self.gridpanel, wx.ID_ANY)
            g.CreateGrid(len(rows), len(fields))
            g.EnableEditing(False)
            for index, att in enumerate(fields):
                g.SetColLabelValue(index, att.replace(' ', '\n'))

            # fill out grid with values
            for row_index, sample in enumerate(rows):
                g.SetRowLabelValue(row_index, 'input')
                for col_index, att in enumerate(fields):
                    g.SetCellValue(row_index, col_index, str(sample.get(att, None)))

            g.AutoSize()

            sz = wx.BoxSizer(wx.VERTICAL)
            sz.Add(g, proportion=1, flag=wx.EXPAND)
            self.gridpanel.SetSizer(sz)
            self.Layout()

    class SuccessPage(wx.wizard.WizardPageSimple):

        def __init__(self, parent):
            super(ImportWizard.SuccessPage, self).__init__(parent)

            title = wx.StaticText(self, wx.ID_ANY, "Success")
            font = title.GetFont()
            font.SetPointSize(font.PointSize * 2)
            font.SetWeight(wx.BOLD)
            title.SetFont(font)

            self.savecheck = wx.CheckBox(self, wx.ID_ANY, 'Save repository?')
            self.swapcheck = wx.CheckBox(self, wx.ID_ANY, 'Switch to imported core?')
            self.savecheck.SetValue(False)
            self.swapcheck.SetValue(True)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
            sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                      border=5)
            sizer.Add(self.swapcheck, wx.ALL | wx.ALIGN_LEFT, border=5)
            sizer.Add(self.savecheck, wx.ALL | wx.ALIGN_LEFT, border=5)

            self.SetSizer(sizer)
            self.Sizer.Layout()

        @property
        def dosave(self):
            return self.savecheck.IsChecked()

        @property
        def doswap(self):
            return self.swapcheck.IsChecked()


def dist_filename(sample, att):
    #complicated filename to enforce useful unique-ness
    return os.extsep.join(('dist{depth:.4f}_{attname}_{run}'.format(
                                depth=float(sample['depth'].rescale('cm').magnitude),
                                attname=att, run=sample['run']),
                           'csv')).replace(' ', '_')


def export_samples(exp_samples, LiPD=False, core_data=None):
    # This function will currently only export the viewed columns and samples
    # of the displayed core in the GUI. There are two main modes: LiPD True or
    # False.
    #
    # If LiPD is False (the default and used by 'Export Samples' in the
    # 'file' dropdown) then there will be .csv files with labeled columns
    # exported for each computation plan and each sample with
    # UncertainQuantities
    #
    # If LiPD is True (Used by 'Export LiPD' in the 'file' dropdown) then the
    # output files will be identical to those of the False condition with three
    # key differences:
    # 1. The columns do not have labels in the .csv files
    # 2. There is one extra 'metadata.json' file that stores all metadata,
    #    column information, and links to each of the appropriate .csv files
    # 3. All of the data is packaged using 'bagit' which is designed for
    #    archiving/transfering data with a built-in way to verify the data
    #
    # No matter what the status of LiPD the final folder will be compressed and
    # saved in the location the user selects.

    # add header labels -- need to use iterator to get computation_plan/id correct

    wildcard = "zip File (*.zip)|*.zip|"               \
               "tar File (*.tar)|*.tar|"               \
               "gzip'ed tar File (*.gztar)|*.gztar|"   \
               "bzip2'ed tar File (*.bztar)|*.bztar"

    print core_data.properties

    dlg = wx.FileDialog(None, message="Save samples in ...", defaultDir=os.getcwd(),
                        defaultFile="samples.zip", wildcard=wildcard,
                        style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
    dlg.SetFilterIndex(0)

    if dlg.ShowModal() == wx.ID_OK:
        tempdir = tempfile.mkdtemp()

        # set of the currently visible computation plans
        displayedRuns = set([i.run for i in exp_samples])

        # Make the .csv's and return the filenames
        csv_fnames = create_csvs(exp_samples, LiPD,
                                 tempdir, displayedRuns)
        temp_fnames = [i[0] for i in csv_fnames]

        # If this is a LiPD export, write the LiPD file
        if LiPD:
            fname_LiPD = create_LiPD_JSON(csv_fnames, core_data, tempdir)
            temp_fnames.append(fname_LiPD)

        savefile, ext = os.path.splitext(dlg.GetPath())

        os.chdir(tempdir)

        if LiPD:
            bag = bagit.make_bag(tempdir, {'Made By:':'Output Automatically Generated by CScibox',
                                          'Contact-Name':'TODO: FIX THIS'})
            #validate the bagging process and print out errors if there are any
            try:
                bag.validate()

            except bagit.BagValidationError, e:
                for d in e.details:
                    if isinstance(d, bag.ChecksumMismatch):
                        print "expected %s to have %s checksum of %s but found %s" % \
                            (e.path, e.algorithm, e.expected, e.found)

        result = shutil.make_archive(savefile, ext[1:])
        os.chdir(os.path.dirname(savefile))

        shutil.rmtree(tempdir)

    dlg.Destroy()


def create_csvs(exp_samples, noheaders,
                tempdir, displayedRuns):
    # function to create necessary .csv files for export
    row_dicts = {}
    keylist = {}
    dist_dicts = {}

    for run in displayedRuns:
        row_dicts[run] = []
        keylist[run] = set()
        # export columns applicable to displayed runs

    for sample in exp_samples:
        run = sample.run
        if run not in keylist:
            continue
        row_dict = {}

        for key, val in sample.iteritems():
            if val is None:
                continue
            keylist[run].add(key)
            if hasattr(val, 'magnitude'):
                row_dict[key] = val.magnitude
                mag = val.uncertainty.magnitude

                if len(mag) == 1:
                    err_att = '%s Error' % key
                    row_dict[err_att] = mag[0].magnitude

                    # append keylist
                    keylist[run].add(err_att)

                elif len(mag) == 2:
                    minus_err_att = '%s Error-' % key
                    row_dict[minus_err_att] = mag[0].magnitude
                    plus_err_att = '%s Error+' % key
                    row_dict[plus_err_att] = mag[1].magnitude

                    # append keylist
                    keylist[run].add(minus_err_att)
                    keylist[run].add(plus_err_att)

                if val.uncertainty.distribution:
                    # store the distribution data as x,y pairs
                    fname = dist_filename(sample, key)
                    d_key = fname.strip('.csv')

                    # add data to dictionary for later output
                    dist_dicts[d_key] = zip(val.uncertainty.distribution.x,
                        val.uncertainty.distribution.y)
            else:
                try:
                    # This apparently happens if it's a pq.Quantity object
                    row_dict[key] = val.magnitude
                except AttributeError:
                    row_dict[key] = val

        row_dicts[run].append(row_dict)

    # store output filenames here
    fnames = []

    for run in row_dicts:
        keys = list(keylist[run])
        if noheaders:
            rows = []
        else:
            rows = [keys]

        for row_dict in row_dicts[run]:
            rows.append([row_dict.get(key, '') or '' for key in keys])

        fname = run.replace(' ', '_') + ".csv"
        fnames.append((fname,keys))

        with open(os.path.join(tempdir, fname), 'wb') as sdata:
            csv.writer(sdata, quoting=csv.QUOTE_NONNUMERIC).writerows(rows)

        for fname, dist in dist_dicts.iteritems():
            fnames.append(fname + ".csv")

            dist.insert(0, ('x', 'y'))

            with open(os.path.join(tempdir, fname + ".csv"), 'wb') as distfile:
                csv.writer(distfile).writerows(dist)

    return fnames


def create_LiPD_JSON(names, mdata, tempdir):
    # function to create the .jsonld structure for LiPD output

    metadata = {"LiPDVersion": "1.2",
                "chronData": [],
                "paleoData": [],
                "dataSetName": "TODO",
                "geo": {
                    "type": "Feature",
                    "geometry": {
                        "coordinates": [0,0],
                        "type": "Point"
                    }
                }
            }

    for i in names:
        metadata["chronData"].append({
            "filename":i[0],
            "columns":[
                    {"variableName":i[1][j],
                     "TSid": "CSB"+str(random.randrange(1000000)),
                     "number": j}
                      for j in range(len(i[1]))]
            })

    # write metadata
    mdfname = 'metadata.json'
    with open(os.path.join(tempdir, mdfname), 'w') as mdfile:
        # sort keys and add indenting so the file can have repeatable form
        # and can be more easily readable by humans
        mdfile.write(json.dumps(metadata, indent=2, sort_keys=True))

    return mdfname

import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled

import os
import csv
import shutil
import tempfile

from cscience import datastore
from cscience.GUI import grid
from cscience.framework import samples, Core, Sample, UncertainQuantity

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
                "Please select a CSV file containing sample data",
                defaultDir=os.getcwd(), wildcard="CSV Files (*.csv)|*.csv|All Files|*.*",
                style=wx.OPEN | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        self.path = dialog.GetPath()
        #destroy the dialog now so no problems happen on early return
        dialog.Destroy()

        if result != wx.ID_OK:
            return False

        with open(self.path, 'rU') as input_file:
            #allow whatever sane csv formats we can manage, here
            sniffer = csv.Sniffer()
            #TODO: report error here on _csv.Error so the user knows wha hoppen
            dialect = sniffer.sniff(input_file.read(1024))
            dialect.skipinitialspace = True
            input_file.seek(0)

            #mild hack to make sure the file isn't empty and does have data,
            #before we start importing...
            #I would use the same reader + tell/seek but per
            #http://docs.python.org/2/library/stdtypes.html#file.tell
            #I'm not 100% confident that will work.
            tempreader = csv.DictReader(input_file, dialect=dialect)
            if not tempreader.fieldnames:
                wx.MessageBox("Selected file is empty.", "Operation Cancelled",
                              wx.OK | wx.ICON_INFORMATION)
                return False
            try:
                dataline = tempreader.next()
            except StopIterationException:
                wx.MessageBox("Selected file appears to contain no data.",
                              "Operation Cancelled", wx.OK | wx.ICON_INFORMATION)
                return False

            input_file.seek(0)
            self.reader = csv.DictReader(input_file, dialect=dialect)
            #strip extra spaces, so users don't get baffled
            self.reader.fieldnames = [name.strip() for name in self.reader.fieldnames]
            self.corepage.setup(self.path)

            return super(ImportWizard, self).RunWizard(self.corepage)

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

        self.fieldpage.setup(self.corename, self.reader.fieldnames)

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
        for index, line in enumerate(self.reader, 1):
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
                                datastore.sample_attributes.convert_value(attname, value)
                        else:
                            newline[fname] = None
                except KeyError:
                    #ignore columns we've elected not to import
                    pass
                except ValueError:
                    #TODO: give ignore line/fix item/give up options
                    wx.MessageBox("%s on row %i has an incorrect type."
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
                if att.is_numeric() and value:
                    uncert = None
                    if key in self.errdict:
                        errkey = self.errdict[key]
                        if len(errkey) > 1:
                            uncert = (newline.get(errkey[0], 0), newline.get(errkey[1], 0))
                        else:
                            uncert = newline.get(errkey[0], 0)
                    unitline[key] = UncertainQuantity(value, self.unitdict.get(key, 'dimensionless'), uncert)
                    #convert units (yay, quantities handles all that)
                    #TODO: maybe allow user to select units for display in some sane way...
                    unitline[key].units = att.unit
                else:
                    unitline[key] = value

            self.rows.append(unitline)

        #doing it this way to keep cols ordered as in source material
        imported = [self.fielddict[k] for k in self.reader.fieldnames if
                    k in self.fielddict]
        self.confirmpage.setup(imported, self.rows)

    def do_sample_import(self, event):
        cname = self.corename
        core = datastore.cores.get(cname, None)
        if core is None:
            core = Core(cname)
            datastore.cores[cname] = core
        for item in self.rows:
            #TODO -- need to update existing samples if they exist, not
            #add new ones!
            s = Sample('input', item)
            core.add(s)
        all = Sample('input', {'depth':'all'})
        source = self.corepage.source_name
        if source:
            all['input']['Provenance'] = source
        latlng = self.corepage.latlng
        all['input']['Latitude'] = latlng[0]
        all['input']['Longitude'] = latlng[1]
        guid = self.corepage.core_guid
        if guid:
            all['input']['Core GUID'] = guid
        core.add(all)
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
            latlng.Add(wx.StaticText(self, wx.ID_ANY, 'Latitude'),
                       flag=wx.ALIGN_CENTRE)
            latlng.Add(self.lat_entry, flag=wx.ALL, border=5)
            latlng.Add(wx.StaticText(self, wx.ID_ANY, 'Longitude'),
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

        def setup(self, filepath):
            basename = os.path.splitext(os.path.basename(filepath))[0]
            self.core_name_box.SetValue(basename)
            self.source_name_input.SetValue(basename)

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
            return (float(self.lat_entry.GetValue()),
                    float(self.lng_entry.GetValue()))

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

            def __init__(self, parent, fieldname, allfields):
                self.fieldname = fieldname
                super(ImportWizard.FieldPage.AssocSelector, self).__init__(
                                                parent, style=wx.BORDER_SIMPLE)

                #import x field from csv as att...
                #TODO:this should maybe be, like, bold?
                fldlbl = wx.StaticText(self, wx.ID_ANY, self.fieldname,
                                     style=wx.ALIGN_LEFT)
                self.fcombo = wx.ComboBox(self, wx.ID_ANY, self.ignoretxt,
                        choices=[self.ignoretxt] +
                                [att.name for att in datastore.sample_attributes],
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
                errchoices = ([self.noerrtxt] +
                              [fld for fld in allfields if fld != self.fieldname])
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
                    unitset = samples.get_conv_units(unit)
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

        def setup(self, corename, fields):
            self.title.SetLabelText('Sample Associations for "%s"' % corename)

            sz = wx.BoxSizer(wx.VERTICAL)
            for name in fields:
                widg = ImportWizard.FieldPage.AssocSelector(self.fieldframe, name, fields)
                widg.add_err_bindings(self.hideused)
                self.fieldwidgets.append(widg)
                sz.Add(widg, flag=wx.EXPAND)
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
                    g.SetCellValue(row_index, col_index, str(sample[att]))

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


main_filename = os.extsep.join(('sample_data', 'csv'))
def dist_filename(sample, att):
    #complicated filename to enforce useful unique-ness
    return os.extsep.join(('dist{depth:.4f}_{attname}_{cplan}'.format(
                                depth=float(sample['depth'].rescale('cm').magnitude),
                                attname=att, cplan=sample['computation plan']),
                           'csv'))

def export_samples(columns, exp_samples, mdata):
    # add header labels -- need to use iterator to get computation_plan/id correct

    wildcard = "zip File (*.zip)|*.zip|"               \
               "tar File (*.tar)|*.tar|"               \
               "gzip'ed tar File (*.gztar)|*.gztar|"   \
               "bzip2'ed tar File (*.bztar)|*.bztar"

    dlg = wx.FileDialog(None, message="Save samples in ...", defaultDir=os.getcwd(),
                        defaultFile="samples.zip", wildcard=wildcard,
                        style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
    dlg.SetFilterIndex(0)

    if dlg.ShowModal() == wx.ID_OK:
        row_dicts = []
        dist_dicts = {}
        keylist = set(columns)
        for sample in exp_samples:
            row_dict = {}
            for att in columns:
                if hasattr(sample[att], 'magnitude'):
                    row_dict[att] = sample[att].magnitude
                    mag = sample[att].uncertainty.magnitude
                    if len(mag) == 1:
                        err_att = '%s Error' % att
                        row_dict[err_att] = mag[0].magnitude
                        keylist.add(err_att)
                    elif len(mag) == 2:
                        minus_err_att = '%s Error-'%att
                        row_dict[minus_err_att] = mag[0].magnitude
                        plus_err_att = '%s Error+'%att
                        row_dict[plus_err_att] = mag[1].magnitude
                        keylist.add(minus_err_att)
                        keylist.add(plus_err_att)
                    if sample[att].uncertainty.distribution:
                        #just going to store these as an un-headered list of x, y
                        #points on each row.
                        fname = dist_filename(sample, att)
                        dist_dicts[fname] = zip(sample[att].uncertainty.distribution.x,
                                                sample[att].uncertainty.distribution.y)
                else:
                    try:
                        #This apparently happens if it's a pq.Quantity object
                        row_dict[att] = sample[att].magnitude
                    except AttributeError:
                        row_dict[att] = sample[att]
            row_dicts.append(row_dict)

        # write metadata

        # mdata will only be 1 element long
        md = mdata[0]
        mdkeys = []
        mdvals = []
        for att in md.atts:
            mdkeys.append(att.name)
            mdvals.append(att.value)
        for vc in md.vcs:
            mdkeys.append('cplan')
            mdvals.append(vc.name)
            for att in vc.atts:
                mdkeys.append(att.name)
                mdvals.append(att.value)

        keys = sorted(list(keylist))
        rows = [keys]
        for row_dict in row_dicts:
            rows.append([row_dict.get(key, '') or '' for key in keys])

        tempdir = tempfile.mkdtemp()
        with open(os.path.join(tempdir,'metadata.csv'),'wb') as mdfile:
            csv.writer(mdfile).writerows([mdkeys,mdvals])

        with open(os.path.join(tempdir, main_filename), 'wb') as sdata:
            csv.writer(sdata).writerows(rows)

        for key in dist_dicts:
            with open(os.path.join(tempdir, key), 'wb') as distfile:
                csv.writer(distfile).writerows(dist_dicts[key])

        savefile = dlg.GetPath()
        savefile, ext = os.path.splitext(dlg.GetPath())

        os.chdir(tempdir)
        result = shutil.make_archive(savefile, ext[1:])
        os.chdir(os.path.dirname(savefile))

        os.remove(os.path.join(tempdir, main_filename))
        for key in dist_dicts:
            os.remove(os.path.join(tempdir, key))
        os.remove(os.path.join(tempdir,'metadata.csv'))
        os.removedirs(tempdir)

    dlg.Destroy()

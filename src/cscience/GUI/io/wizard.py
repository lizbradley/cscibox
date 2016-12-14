import os
import datetime
import re

import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled

from cscience import datastore
from cscience.GUI import grid
from cscience.framework import samples, datastructures

import readers
from multiprocessing.managers import public_methods

datastore = datastore.Datastore()

class ImportWizard(wx.wizard.Wizard):
    #TODO: fix back & forth to actually work.

    def __init__(self, parent):
        super(ImportWizard, self).__init__(parent, wx.ID_ANY, "Import Samples",
                                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.corepage = CorePage(self)
        self.metapage = MetaPage(self)
        self.fieldpage = FieldPage(self)
        self.confirmpage = ConfirmPage(self)
        self.successpage = SuccessPage(self)

        wx.wizard.WizardPageSimple_Chain(self.corepage, self.metapage)
        wx.wizard.WizardPageSimple_Chain(self.metapage, self.fieldpage)
        wx.wizard.WizardPageSimple_Chain(self.fieldpage, self.confirmpage)
        wx.wizard.WizardPageSimple_Chain(self.confirmpage, self.successpage)

        #we seem to need to add all the pages to the pageareasizer manually
        #or the next/back buttons move around on resize, whee!
        self.GetPageAreaSizer().Add(self.corepage)
        self.GetPageAreaSizer().Add(self.metapage)
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
                               "Please select a LiPD or CSV file containing sample data",
                               defaultDir=os.getcwd(),
                               wildcard="CSV Files (*.csv)|*.csv|" +
                                        "LiPD Files(*.lpd, *.lipd)|*.lpd;*.lipd|" +
                                        "Zip Files (*.zip)|*.zip|" +
                                        "All Files|*.*",
                               style=wx.OPEN | wx.DD_CHANGE_DIR)
        result = dialog.ShowModal()
        self.path = dialog.GetPath()
        #destroy the dialog now so no problems happen on early return
        dialog.Destroy()
        # Should use the bagit utility to check to make sure the data is not corrupt
        if result != wx.ID_OK:
            return False

        #.lpd, .lipd, .zip == LiPD

        try:
            fname = self.path.lower()
            if fname.endswith('.lpd') or fname.endswith('.lipd') or fname.endswith('.zip'):
                #archive, so we assume it's a LiPD fild
                self.reader = readers.LiPDReader(self.path)
            else:
                self.reader = readers.CSVReader(self.path)
        except Exception as ex:
            wx.MessageBox("Sorry, there was an error opening the selected file. Please try again.\n" +
                          "Error: %s" % ex.message)
            return False

        self.corepage.setup(self.reader.core_name)
        return super(ImportWizard, self).RunWizard(self.corepage)

    def dispatch_changing(self, event):
        #TODO: handle back as well; do enough cleanup it all works...
        if event.Direction:
            if event.Page is self.corepage:
                self.confirm_core_data(event)
            elif event.Page is self.metapage:
                self.confirm_metadata(event)
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

        self.metapage.setup(self.corename, self.reader.get_known_metadata())

    def confirm_metadata(self, event):
        try:
            geo = self.metapage.get_geodata()
        except ValueError as ve:
            wx.MessageBox("Please enter a valid latitude and longitude for this core. " +
                          ve.message + '.', "Latitude/Longitude Invalid",
                          wx.OK | wx.ICON_INFORMATION)
            event.Veto()
            return

        self.fieldpage.setup(self.corename, self.reader.get_unit_dict())

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

        reader = self.reader.get_data_reader(self.fielddict)
        self.rows = []

        for index, line in enumerate(reader, 1):
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
        imported = [self.fielddict[k] for k in self.reader.fieldnames if
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

        all_core_properties = samples.Sample('input', {'Core Site':self.metapage.get_geodata()})
        all_core_properties['input'].update(self.metapage.get_inputs())
        core.properties = all_core_properties

        core.loaded = True

class CorePage(wx.wizard.WizardPageSimple):
    """
    Write down core-wide data (of doom) before looking at field-specific
    correlations (also of doom)
    """

    def __init__(self, parent):
        super(CorePage, self).__init__(parent)

        title = wx.StaticText(self, wx.ID_ANY, "Core Data")
        font = title.GetFont()
        font.SetPointSize(font.PointSize * 2)
        font.SetWeight(wx.BOLD)
        title.SetFont(font)

        corebox = self.make_corebox()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                  border=5)
        sizer.Add(corebox, flag=wx.ALIGN_CENTER_HORIZONTAL)


        self.SetSizer(sizer)

    def make_corebox(self):
        corebox = wx.Panel(self)

        self.new_core = wx.RadioButton(corebox, wx.ID_ANY, 'Create new core',
                                       style=wx.RB_GROUP)
        self.existing_core = wx.RadioButton(corebox, wx.ID_ANY, 'Add to existing core')

        self.new_core_panel = wx.Panel(corebox, size=(400, -1))
        self.core_name_box = wx.TextCtrl(self.new_core_panel, wx.ID_ANY)
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(wx.StaticText(self.new_core_panel, wx.ID_ANY, 'Core Name:'),
               border=5, flag=wx.ALL)
        sz.Add(self.core_name_box, border=5, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.new_core_panel.SetSizer(sz)

        self.existing_core_panel = wx.Panel(corebox, size=(400, -1))
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

    def setup(self, default_name):
        self.core_name_box.SetValue(default_name)

    def on_coretype(self, event):
        self.new_core_panel.Show(self.new_core.GetValue())
        self.existing_core_panel.Show(self.existing_core.GetValue())
        self.Sizer.Layout()

    @property
    def core_name(self):
        if self.new_core.GetValue():
            return self.core_name_box.GetValue()
        else:
            return self.core_select.GetValue()

class MetaPage(wx.wizard.WizardPageSimple):

    class GeoInput(wx.Panel):
        def __init__(self, parent, id):
            super(MetaPage.GeoInput, self).__init__(parent, id)

            self.lat_entry = wx.TextCtrl(self, wx.ID_ANY)
            self.lng_entry = wx.TextCtrl(self, wx.ID_ANY)

            self.elev_entry = wx.TextCtrl(self, wx.ID_ANY)
            self.name_entry = wx.TextCtrl(self, wx.ID_ANY)

            sizer = wx.BoxSizer(wx.VERTICAL)
            lsizer = wx.BoxSizer(wx.HORIZONTAL)
            lsizer.Add(wx.StaticText(self, wx.ID_ANY, 'Latitude (+90(N) to -90(S))'),
                       flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=2)
            lsizer.Add(self.lat_entry, flag=wx.LEFT | wx.RIGHT, border=5)
            lsizer.Add(wx.StaticText(self, wx.ID_ANY, 'Longitude (+180(E) to -180(W))'),
                       flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=2)
            lsizer.Add(self.lng_entry, flag=wx.LEFT | wx.RIGHT, border=5)
            sizer.Add(lsizer, flag=wx.EXPAND)
            lsizer = wx.BoxSizer(wx.HORIZONTAL)
            lsizer.Add(wx.StaticText(self, wx.ID_ANY, "Elevation (optional)"),
                      flag=wx.ALIGN_CENTER_VERTICAL)
            lsizer.Add(self.elev_entry, flag=wx.LEFT | wx.RIGHT, border=5)
            lsizer.Add(wx.StaticText(self, wx.ID_ANY, "Site Name (optional)"),
                      flag=wx.ALIGN_CENTER_VERTICAL)
            lsizer.Add(self.name_entry, proportion=1, flag=wx.LEFT | wx.RIGHT, border=5)
            sizer.Add(lsizer, flag=wx.EXPAND)

            self.SetSizerAndFit(sizer)

        def GetValue(self):
            return datastructures.GeographyData(self.lat_entry.GetValue(),
                            self.lng_entry.GetValue(),
                            self.elev_entry.GetValue() or None,
                            self.name_entry.GetValue() or None)

        def SetValue(self, value):
            if not value:
                return
            self.lat_entry.SetValue(str(value.lat))
            self.lng_entry.SetValue(str(value.lon))
            if value.elev is not None:
                self.elev_entry.SetValue(str(value.elev))
            if value.sitename is not None:
                self.name_entry.SetValue(str(value.sitename))


    class TimeInput(wx.Panel):
        def __init__(self, parent, id):
            super(MetaPage.TimeInput, self).__init__(parent, id)

            self.dateentry = wx.DatePickerCtrl(self, wx.ID_ANY, style=wx.DP_DROPDOWN)
            self.hour = wx.TextCtrl(self, wx.ID_ANY)
            self.minute = wx.TextCtrl(self, wx.ID_ANY)
            self.second = wx.TextCtrl(self, wx.ID_ANY)
            self.set_inputs(wx.DateTime.Now())

            #set some sizes for tighter layout:
            for ctrl in (self.hour, self.minute, self.second):
                w, h = ctrl.GetSize()
                dc = wx.ClientDC(ctrl)
                tsize = dc.GetTextExtent(ctrl.GetValue())[0]
                ctrl.SetMinSize((tsize+10, h))
                ctrl.SetSize(ctrl.GetMinSize())
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, "Date"))
            sizer.Add(self.dateentry, flag=wx.ALIGN_TOP)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, "Time (24 hr)"))
            sizer.Add(self.hour, flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT | wx.RIGHT,
                      border=2)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, ":"))
            sizer.Add(self.minute, flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT | wx.RIGHT,
                      border=2)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, ":"))
            sizer.Add(self.second, flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT | wx.RIGHT,
                      border=2)
            self.SetSizer(sizer)

        def set_inputs(self, dt):
            self.dateentry.SetValue(dt)
            self.hour.SetValue('%02i' % dt.Hour)
            self.minute.SetValue('%02i' % dt.Minute)
            self.second.SetValue('%02i' % dt.Second)

        def GetValue(self):
            dt = self.dateentry.GetValue()
            entry = datetime.datetime(dt.Year, dt.Month, dt.Day,
                                      int(self.hour.GetValue()),
                                      int(self.minute.GetValue()),
                                      int(self.second.GetValue()))
            return datastructures.TimeData(entry.timetuple())

        def SetValue(self, value):
            self.set_inputs(wx.DateTimeFromDateTime(datetime.datetime(value)))


    class PublistInput(wx.Panel):

        class PubInput(wx.Panel):
            def __init__(self, parent):
                super(MetaPage.PublistInput.PubInput, self).__init__(parent, wx.ID_ANY)

                self.structpanel = wx.Panel(self, wx.ID_ANY)
                self.unstructpanel = wx.Panel(self, wx.ID_ANY)

                self.struct_check = wx.CheckBox(self, wx.ID_ANY,
                                                "Use Unstructured Citation")

                self.auth_panel = wx.Panel(self.structpanel, wx.ID_ANY)
                self.auth_set = []
                add_auth_btn = wx.Button(self.auth_panel, wx.ID_ANY, " + ")
                add_auth_btn.SetMinSize((30, -1))
                sub_auth_btn = wx.Button(self.auth_panel, wx.ID_ANY, " - ")
                sub_auth_btn.SetMinSize((30, -1))

                apbsz = wx.BoxSizer(wx.HORIZONTAL)
                apbsz.Add(wx.StaticText(self.auth_panel, wx.ID_ANY, "Authors (Last, First)"))
                apbsz.Add(add_auth_btn, flag=wx.LEFT, border=10)
                apbsz.Add(sub_auth_btn)
                self.apsizer = wx.BoxSizer(wx.VERTICAL)
                self.apsizer.Add(apbsz)
                self.auth_panel.SetSizer(self.apsizer)

                self.add_author()

                self.title = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.journal = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.year = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.volume = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.issue = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.pages = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.report_num = wx.TextCtrl(self.structpanel, wx.ID_ANY)
                self.doi = wx.TextCtrl(self.structpanel, wx.ID_ANY)

                ssizer = wx.BoxSizer(wx.VERTICAL)
                hor = wx.BoxSizer(wx.HORIZONTAL)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Title"))
                hor.Add(self.title, proportion=1)
                ssizer.Add(hor, flag=wx.EXPAND)
                ssizer.Add(self.auth_panel, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

                hor = wx.BoxSizer(wx.HORIZONTAL)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "In Journal"))
                hor.Add(self.journal, proportion=1)
                ssizer.Add(hor, flag=wx.EXPAND)
                hor = wx.BoxSizer(wx.HORIZONTAL)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Volume"))
                hor.Add(self.volume, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=2)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Year"))
                hor.Add(self.year, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=2)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Issue"))
                hor.Add(self.issue, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=2)
                ssizer.Add(hor)
                hor = wx.BoxSizer(wx.HORIZONTAL)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Pages"))
                hor.Add(self.pages, flag=wx.RIGHT, border=2)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "Report Number"))
                hor.Add(self.report_num)
                ssizer.Add(hor)

                hor = wx.BoxSizer(wx.HORIZONTAL)
                hor.Add(wx.StaticText(self.structpanel, wx.ID_ANY, "DOI"))
                hor.Add(self.doi, proportion=1, flag=wx.TOP, border=5)
                ssizer.Add(hor, flag=wx.EXPAND)
                self.structpanel.SetSizer(ssizer)

                self.alternate = wx.TextCtrl(self.unstructpanel, wx.ID_ANY)
                usizer = wx.BoxSizer(wx.HORIZONTAL)
                usizer.Add(wx.StaticText(self.unstructpanel, wx.ID_ANY, "Citation String"))
                usizer.Add(self.alternate, proportion=1)
                self.unstructpanel.SetSizer(usizer)

                topbox = wx.StaticBox(self, wx.ID_ANY)
                topsizer = wx.StaticBoxSizer(topbox, wx.VERTICAL)

                rmvbtn = wx.Button(self, wx.ID_ANY, "- Remove")
                topsizer.Add(rmvbtn, flag=wx.ALIGN_RIGHT)
                self.Bind(wx.EVT_BUTTON, self.remove, rmvbtn)

                topsizer.Add(self.struct_check)
                topsizer.Add(self.structpanel, flag=wx.EXPAND)
                topsizer.Add(self.unstructpanel, flag=wx.EXPAND)
                self.show_struct()
                self.SetSizer(topsizer)

                self.Bind(wx.EVT_CHECKBOX, self.show_struct, self.struct_check)
                self.Bind(wx.EVT_BUTTON, self.add_author, add_auth_btn)
                self.Bind(wx.EVT_BUTTON, self.sub_author, sub_auth_btn)

            def add_author(self, event=None):
                pane = wx.Panel(self.auth_panel, wx.ID_ANY)
                lname = wx.TextCtrl(pane, wx.ID_ANY)
                fname = wx.TextCtrl(pane, wx.ID_ANY)

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(lname, proportion=1, flag=wx.TOP, border=2)
                sizer.Add(wx.StaticText(pane, wx.ID_ANY, ", "), flag=wx.ALIGN_BOTTOM)
                sizer.Add(fname, proportion=1, flag=wx.TOP, border=2)
                pane.SetSizer(sizer)

                self.auth_set.append((pane, lname, fname))
                self.apsizer.Add(pane, flag=wx.LEFT | wx.EXPAND, border=10)
                #self.auth_panel.Layout()
                self.Layout()

            def sub_author(self, event=None):
                if len(self.auth_set) <= 1:
                    #can't remove last author
                    return
                pane, _, _ = self.auth_set.pop()
                self.apsizer.Hide(pane)
                self.apsizer.Remove(pane)
                self.auth_panel.Layout()
                self.Layout()

            def show_struct(self, event=None):
                #Add & remove from sizer if needed here.
                self.structpanel.Show(not self.struct_check.IsChecked())
                self.unstructpanel.Show(self.struct_check.IsChecked())
                self.Layout()

            def remove(self, event=None):
                self.Parent.remove_pub(self)

            def GetValue(self):
                if self.struct_check.IsChecked():
                    #actually the "unstructured" check, cuz naming is hard
                    pub = datastructures.Publication(alternate=self.alternate.GetValue())
                else:
                    pub = datastructures.Publication(title=self.title.GetValue(),
                        authors=[(last.GetValue(), first.GetValue()) for
                                 _, last, first in self.auth_set if
                                 last.GetValue() or first.GetValue()],
                        journal=self.journal.GetValue(), year=self.year.GetValue(),
                        volume=self.volume.GetValue(), issue=self.issue.GetValue(),
                        pages=self.pages.GetValue(), report_num=self.report_num.GetValue(),
                        doi=self.doi.GetValue())

                if pub.is_valid():
                    return pub
                else:
                    return None

            def SetValue(self, value):
                self.struct_check.SetValue(bool(value.alternate))
                self.show_struct()

                self.title.SetValue(unicode(value.title))
                self.journal.SetValue(unicode(value.journal))
                self.year.SetValue(unicode(value.year))
                self.volume.SetValue(unicode(value.volume))
                self.issue.SetValue(unicode(value.issue))
                self.pages.SetValue(unicode(value.pages))
                self.report_num.SetValue(unicode(value.report_num))
                self.doi.SetValue(unicode(value.doi))

                while len(self.auth_set) > 1:
                    self.sub_author()
                for author in value.authors:
                    _, last, first = self.auth_set[-1]
                    last.SetValue(unicode(author[0]))
                    first.SetValue(unicode(author[1]))
                    self.add_author()
                #and then take off the last one. Gross, but I feel lazy.
                self.sub_author()

            def Layout(self):
                super(MetaPage.PublistInput.PubInput, self).Layout()
                self.Parent.Layout()

        def __init__(self, parent, id):
            super(MetaPage.PublistInput, self).__init__(parent, id)

            addbtn = wx.Button(self, wx.ID_ANY, "+ Add Publication")
            self.pubs = []
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(addbtn)
            self.add_pub()
            self.SetSizer(self.sizer)

            self.Bind(wx.EVT_BUTTON, self.add_pub, addbtn)

        def add_pub(self, event=None):
            pub = MetaPage.PublistInput.PubInput(self)
            self.pubs.append(pub)
            self.sizer.Add(pub, flag=wx.EXPAND)
            self.Layout()

        def remove_pub(self, pub):
            del self.pubs[self.pubs.index(pub)]
            self.sizer.Hide(pub)
            self.sizer.Remove(pub)
            self.Layout()

        def Layout(self):
            super(MetaPage.PublistInput, self).Layout()
            self.Parent.Layout()

        def GetValue(self):
            return datastructures.PublicationList([pub.GetValue() for
                                            pub in self.pubs if pub.GetValue()])

        def SetValue(self, value):
            self.Freeze()

            for pub in self.pubs:
                self.remove_pub(pub)

            for pub in value.publications:
                self.add_pub()
                self.pubs[-1].SetValue(pub)

            self.Layout()
            self.Thaw()


    handled_types = {"float":wx.TextCtrl, "string":wx.TextCtrl,
                     "integer":wx.TextCtrl, "boolean":wx.TextCtrl,
                     "time":TimeInput, "geography":GeoInput,
                     "publication list":PublistInput}
    class MetaInput(wx.Panel):
        inittxt = "<Choose Field>"

        def __init__(self, parent):
            super(MetaPage.MetaInput, self).__init__(parent)

            self.fieldchoice = wx.ComboBox(self, wx.ID_ANY, self.inittxt,
                    choices=[self.inittxt] +
                     [att.name for att in datastore.core_attributes if
                      att.name != "Core Site" and
                      att.type_ in MetaPage.handled_types],
                    style=wx.CB_READONLY)
            self.inputthing = wx.Panel(self, wx.ID_ANY)
            self.inputthing.SetMinSize(self.fieldchoice.GetSize())

            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer.Add(self.fieldchoice, border=5, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)
            self.sizer.AddStretchSpacer(1)
            self.sizer.Add(self.inputthing, border=5, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT)

            self.SetSizer(self.sizer)

            self.Bind(wx.EVT_COMBOBOX, self.sel_field_changed, self.fieldchoice)

        def sel_field_changed(self, event=None):
            value = self.fieldchoice.GetValue()
            if value == self.inittxt:
                fieldtype = ''
            else:
                att = datastore.core_attributes[value]
                fieldtype = att.type_

            self.set_inputtype(fieldtype)

        def set_inputtype(self, fieldtype):
            inputtype = MetaPage.handled_types.get(fieldtype, wx.Panel)
            if type(self.inputthing) != inputtype:
                self.Freeze()
                self.sizer.Hide(self.inputthing)
                self.sizer.Remove(self.inputthing)
                
                self.inputthing = inputtype(self, wx.ID_ANY)
                self.inputthing.SetMinSize((500, -1))
                self.sizer.Add(self.inputthing, border=5, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT)
            
                self.Layout()
                self.Thaw()
            
        def Layout(self):
            super(MetaPage.MetaInput, self).Layout()
            self.Parent.Layout()
            try:
                self.Parent.SetupScrolling()
            except AttributeError:
                pass

        def GetValue(self):
            if self.fieldchoice.GetStringSelection() != self.inittxt and \
               hasattr(self.inputthing, 'GetValue'):
                return (self.fieldchoice.GetStringSelection(), 
                        self.inputthing.GetValue())

        def SetValue(self, valuename, value):
            if not value:
                self.fieldchoice.SetStringSelection(self.inittxt)
                self.set_inputtype("")
                return

            if valuename in self.fieldchoice.GetStrings():
                self.fieldchoice.SetStringSelection(valuename)
            else:
                self.fieldchoice.SetStringSelection(self.inittxt)
            
            self.set_inputtype(getattr(value, 'typename', 'string'))
            self.inputthing.SetValue(value)

    def __init__(self, parent):
        super(MetaPage, self).__init__(parent)
        self.fields = []

        self.title = wx.StaticText(self, wx.ID_ANY, "Metadata")
        font = self.title.GetFont()
        font.SetPointSize(font.PointSize * 2)
        font.SetWeight(wx.BOLD)
        self.title.SetFont(font)

        addbtn = wx.Button(self, wx.ID_ANY, "+ Add Field")

        flabelframe = wx.Panel(self)
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(wx.StaticText(flabelframe, wx.ID_ANY, 'Record Metadata Field'),
               border=5, flag=wx.RIGHT | wx.LEFT)
        sz.AddStretchSpacer(1)
        sz.Add(wx.StaticText(flabelframe, wx.ID_ANY, 'as Value',
                             style=wx.ALIGN_RIGHT))
        sz.AddSpacer((150, 0))
        flabelframe.SetSizer(sz)

        self.fieldpanel = scrolled.ScrolledPanel(self)

        self.siteentry = MetaPage.GeoInput(self.fieldpanel, wx.ID_ANY)
        sz = wx.BoxSizer(wx.HORIZONTAL)

        sz.Add(wx.StaticText(self.fieldpanel, wx.ID_ANY, "Core Site"),
               border=5, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sz.AddStretchSpacer(1)
        sz.Add(self.siteentry, flag=wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT, border=5)
        sz.AddSpacer((100, 0))

        self.fieldsizer = wx.BoxSizer(wx.VERTICAL)
        self.fieldsizer.Add(sz, flag=wx.EXPAND)
        self.fieldsizer.Add(wx.StaticLine(self.fieldpanel, wx.ID_ANY),
                            flag=wx.EXPAND | wx.ALL, border=5)
        self.fieldpanel.SetSizer(self.fieldsizer)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.title, flag=wx.ALIGN_CENTRE | wx.ALL, border=5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY), flag=wx.EXPAND | wx.ALL,
                  border=5)
        sizer.Add(addbtn, border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(flabelframe, border=5, flag=wx.EXPAND | wx.BOTTOM)
        sizer.Add(self.fieldpanel, flag=wx.EXPAND, proportion=1)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.addinput, addbtn)

    def addinput(self, event=None):
        input = MetaPage.MetaInput(self.fieldpanel)
        delbutton = wx.Button(self.fieldpanel, wx.ID_ANY, "Delete")
        line = wx.StaticLine(self.fieldpanel, wx.ID_ANY)
        bitsizer = wx.BoxSizer(wx.HORIZONTAL)
        bitsizer.Add(input, proportion=1, flag=wx.EXPAND)
        bitsizer.Add(delbutton, flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, border=5)

        def del_field(event):
            try:
                index = self.fields.index(input)
            except ValueError:
                #assume field is already removed and something weird happened
                return
            del self.fields[index]
            self.fieldsizer.Hide(line)
            self.fieldsizer.Remove(line)
            self.fieldsizer.Hide(bitsizer)
            self.fieldsizer.Remove(bitsizer)

            self.fieldpanel.Layout()
            self.fieldpanel.SetupScrolling()

        self.Bind(wx.EVT_BUTTON, del_field, delbutton)
        self.fields.append(input)
        self.fieldsizer.Add(bitsizer, flag=wx.EXPAND)
        self.fieldsizer.Add(line, flag=wx.EXPAND | wx.ALL, border=5)

        self.fieldpanel.Layout()
        self.fieldpanel.SetupScrolling()

    def get_geodata(self):
        return self.siteentry.GetValue()

    def get_inputs(self):
        return dict([fld.GetValue() for fld in self.fields if fld.GetValue()])

    def setup(self, corename, meta):
        self.title.SetLabelText('Metadata for "%s"' % corename)
        self.siteentry.SetValue(meta.pop('Core Site', None))
        for key, val in meta.iteritems():
            self.addinput()
            self.fields[-1].SetValue(key, val)


class FieldPage(wx.wizard.WizardPageSimple):
    """
    Set up a dictionary of file field names -> cscibox field names
    -- allow on-the-fly attribute creation
    """

    class AssocSelector(wx.Panel):

        ignoretxt = "Ignore this Field"
        noerrtxt = "No Error"

        def __init__(self, parent, fielddata, unitdict):
            self.fieldname = fielddata
            self.units = unitdict.get(fielddata, None)

            super(FieldPage.AssocSelector, self).__init__(
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
            errchoices = ([self.noerrtxt] +
                          [fld for fld in unitdict if fld != self.fieldname])

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
            #we look for one name containing the other, case-insensitive
            #(if there are multiple matches, we just take the first. deal.)
            if self.fieldname in datastore.sample_attributes:
                #give priority to ==
                self.fcombo.SetValue(self.fieldname)
                self.sel_field_changed()
            else:
                fieldregex = ".*" + self.fieldname + ".*"
                fieldre = re.compile(fieldregex, re.I)
                for att in datastore.sample_attributes:
                    if att.name in self.fieldname or fieldre.match(att.name):
                        self.fcombo.SetValue(att.name)
                        self.sel_field_changed()
                        break
                    
            errorregex = self.fieldname + r".*(error|uncertainty)"
            errorre = re.compile(errorregex, re.I)
            for s in unitdict:
                if errorre.match(s):
                    self.ecombo.SetValue(s)
                    #TODO: event?
                    break

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
            if self.units and self.units in self.ucombo.GetStrings():
                self.ucombo.SetStringSelection(self.units)
            else:
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
        super(FieldPage, self).__init__(parent)

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

    def setup(self, corename, fieldunits):
        self.title.SetLabelText('Sample Associations for "%s"' % corename)

        sz = wx.BoxSizer(wx.VERTICAL)
        for name in fieldunits:
            widg = FieldPage.AssocSelector(self.fieldframe, name, fieldunits)
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
        super(ConfirmPage, self).__init__(parent)

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
        super(SuccessPage, self).__init__(parent)

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

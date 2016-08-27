import os
import sys
import config

import wx
import quantities

library = {}

from cscience.framework.datastructures import UncertainQuantity

class _ComponentType(type):
    """
    Auto-registers any class extending BaseComponent (or another component type)
    in the component library.
    """
    def __new__(cls, name, bases, dct):
        lib_entry = dct.pop('visible_name', name)
        newclass = super(_ComponentType, cls).__new__(cls, name, bases, dct)
        if lib_entry and lib_entry != 'BaseComponent':
            library[lib_entry] = newclass
        return newclass

class BaseComponent(object):
    """Base class for workflow components."""

    __metaclass__ = _ComponentType

    def __init__(self):
        self.connections = dict.fromkeys(self.output_ports())
        self.workflow = None
        self.collections = None
        self.computation_plan = None

    def prepare(self, paleobase, workflow, experiment):
        self.paleobase = paleobase
        self.workflow = workflow
        self.computation_plan = experiment

        parms = getattr(self, 'params', {})
        for parm in parms:
            self.paleobase[parm] = self.paleobase[self.computation_plan[parm]]

    def __call__(self, core, progress_dialog):
        """Default implementation of the worker function of a component;
        this function calls run_component and then returns the output port
        and the current set of samples. Useful for the standard case of a
        simple, linear component that does no filtering.
        """
        try:
            self.run_component(core, progress_dialog)
            return [(self.connections['output'], core)]
        except Exception as e:
            import traceback
            print traceback.format_exc()
            raise

    def run_component(self, core, progress_dialog):
        """By default, actual work is done here so components need not worry
        about input/output specifics."""
        raise NotImplementedError("Components run_component method "
                                  "or override __call__ method")

    def user_inputs(self, core, input_data):
        #TODO: attributes?
        inputdlg = InputQuery(core, input_data)
        if inputdlg.ShowModal() == wx.ID_OK:
            result = inputdlg.result
            for name, input in result.iteritems():
                self.set_value(core, name, input)
        inputdlg.Destroy()
        return result

    def set_value(self, core, name, value):
        core['all'][name] = value
        core.partial_run.addvalue(name, value)

    def connect(self, component, name='output'):
        self.connections[name] = component.input_port()

    def input_port(self):
        return self

    def get_connection(self, name='output'):
        return self.connections[name]

    @classmethod
    def output_ports(cls):
        return ('output',)

    @classmethod
    def get_plugin_location(cls, plugin_name):
        #TODO: allow plugins to live in multiple different locations.
        plugin_loc = config.plugin_location

        if not os.path.isabs(plugin_loc):
            #TODO: does this actually work with the installer bundle?
            if getattr(sys, 'frozen', False):
                # we are running in a |PyInstaller| bundle
                basedir = sys._MEIPASS
            else:
                # we are running in a normal Python environment
                basedir = os.path.dirname(__file__)
            return os.path.join(basedir, os.path.pardir, os.path.pardir,
                               plugin_loc, plugin_name)
        else:
            return os.path.join(plugin_loc, plugin_name)


#TODO: better error checking!
class InputQuery(wx.Dialog):
    class BooleanInput(wx.RadioBox):
        def __init__(self, parent):
            super(InputQuery.BooleanInput, self).__init__(parent, wx.ID_ANY, label="",
                                               choices=['Yes', 'No'])
        def get_value(self):
            #not, since we have No in the 1 position
            return not self.GetSelection()

    class StringInput(wx.TextCtrl):
        def get_value(self):
            return self.GetValue()

    class NumericInput(wx.TextCtrl):
        def __init__(self, parent, type_=float, unit=None, defval=0, minmax=(None, None)):
            super(InputQuery.NumericInput, self).__init__(parent, wx.ID_ANY)

            self.type_ = type_
            self.minmax = minmax
            self.unit = unit
            self.defval = defval
            if minmax[0] and self.defval < minmax[0]:
                self.defval = minmax[0]
            if minmax[1] and self.defval > minmax[1]:
                self.defval = minmax[1]
            self.defval = str(self.defval)
            self.SetValue(self.defval)
            self.SetSelection(-1, -1)

            self.Bind(wx.EVT_KILL_FOCUS, self.check_input)
            self.Bind(wx.EVT_SET_FOCUS, self.highlight)

        def show_error(self, err):
            if err:
                self.SetValue(self.defval)
                self.SetBackgroundColour('red')
                self.SetSelection(-1, -1)
            else:
                self.SetBackgroundColour('white')

        def check_input(self, event):
            try:
                val = self.type_(self.GetValue())
            except ValueError:
                self.show_error(True)
            else:
                if self.minmax[0] is not None and val < self.minmax[0]:
                    self.show_error(True)
                elif self.minmax[1] is not None and val > self.minmax[1]:
                    self.show_error(True)
                else:
                    self.show_error(False)

            event.Skip()

        def highlight(self, event):
            #wait till all selections are actually finshed, then select
            wx.CallAfter(self.SetSelection, -1, -1)
            event.Skip()

        def get_value(self):
            val = self.type_(self.GetValue())
            if self.unit:
                return quantities.Quantity(val, self.unit)
            else:
                return val

    class ErrorInput(wx.Panel):
        def __init__(self, parent, type_=float, unit=None, minmax=(None, None)):
            super(InputQuery.ErrorInput, self).__init__(parent, wx.ID_ANY)
            self.main_input = InputQuery.NumericInput(self, type_, None, minmax)
            self.err_input = InputQuery.NumericInput(self, type_)

            self.unit = unit

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(self.main_input, flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT,
                      border=2, proportion=1)
            sizer.Add(wx.StaticText(self, label='+/-'), flag=wx.ALL, border=2)
            sizer.Add(self.err_input, flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT,
                      border=2, proportion=1)
            self.SetSizer(sizer)

        def get_value(self):
            return UncertainQuantity(self.main_input.get_value(), self.unit,
                                     self.err_input.get_value())

    class LabelledInput(wx.Panel):
        def __init__(self, parent, label, control_type, params=[], extra={}):
            super(InputQuery.LabelledInput, self).__init__(parent)

            tooltip = extra.pop('helptip', '')
            self.control = control_type(self, *params, **extra)
            if tooltip:
                helplabel = wx.StaticText(self, wx.ID_ANY, tooltip)
                helplabel.SetFont(helplabel.GetFont().Scale(.9))
                

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.StaticText(self, label=label), flag=wx.ALL, border=2)
            if tooltip:
                csizer = wx.BoxSizer(wx.VERTICAL)
                csizer.Add(self.control, flag=wx.EXPAND, proportion=1)
                csizer.Add(helplabel, flag=wx.LEFT, border=10)
                sizer.Add(csizer, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
            else:
                sizer.Add(self.control, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
            if params[1]: #unit
                sizer.Add(wx.StaticText(self, label=params[1]), flag=wx.ALL, border=2)
            self.SetSizer(sizer)

        def get_value(self):
            return self.control.get_value()

    def __init__(self, core, dataneeded):
        #TODO: the sizing on these is really freaking annoying; I should get that
        #fixed.
        super(InputQuery, self).__init__(None, title='Please Provide Input', style=wx.CAPTION)

        self.dataneeded = dataneeded
        self.controls = {}

        scrolledwindow = wx.ScrolledWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        #TODO set control default values as appropriate from core
        for details in self.dataneeded:
            sizer.Add(self.create_control(details[0], details[1:], scrolledwindow),
                      flag=wx.EXPAND | wx.ALL, border=3)

        scrolledwindow.SetSizer(sizer)
        scrolledwindow.SetScrollRate(20, 20)
        scrolledwindow.EnableScrolling(True, True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(scrolledwindow, flag=wx.EXPAND | wx.ALL, border=2, proportion=1)
        sizer.Add(wx.Button(self, wx.ID_OK), flag=wx.CENTER|wx.ALL, border=5)
        self.SetSizer(sizer)

        scrolledwindow.Layout()
        self.Centre()
        self.Layout()

    def create_control(self, name, details, parent):
        attdata = details[0]
        otherparms = details[2] if len(details) > 2 else {}
        defval = details[1] if len(details) > 1 else 0
        params = []
        if attdata[0] == 'boolean':
            ctrl = InputQuery.BooleanInput
        elif attdata[0] == 'string':
            ctrl = InputQuery.StringInput
        else:
            ctrl = InputQuery.ErrorInput if attdata[2] else InputQuery.NumericInput
            type_ = int if attdata[0] == 'integer' else float
            params = [type_, attdata[1], defval] #unit

        ctrl = InputQuery.LabelledInput(parent, name, ctrl, params, otherparms)
        self.controls[name] = ctrl
        return ctrl

    @property
    def result(self):
        return dict([(name, ctrl.get_value()) for name, ctrl in self.controls.items()])



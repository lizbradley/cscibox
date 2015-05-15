"""
File for storing valuable widgets. Let us avoid the
God file.
"""

import wx
# from wx.lib.agw import foldpanelbar as fpb
from wx.lib.agw import pycollapsiblepane as pcp

"""
Simply a combo box with a more abstracted interface
as a dictionary of choices and arguments to actions.
"""
class CalChoice(wx.Choice): # <class T>
    # Choices is a dictionary of (string -> T)
    def __init__(self, parent, items):

        self.selected = None
        strings, self.values = zip( *items ) # unzip -- because python :-(

        wx.Choice.__init__(self, parent, wx.NewId(), choices=strings)

        self.listeners = []
        self.Bind(wx.EVT_CHOICE,self.__options_changed,id=self.GetId())
        self.SetSelection(0)
        self.__options_changed(None)

    # attaches a listener which is
    # fired once an event occured in general
    #
    # f : Function (this -> T -> void)
    def add_change_listener( self, f ):
        self.listeners.append(f)

    def get_selected(self):
        return self.selected

    # Called when the options have changed
    def __options_changed(self,_):
        self.selected = self.values[self.GetCurrentSelection()]
        
        # Iterate through all of the listeners!
        for f in self.listeners:
            f(self, self.selected)

class CalRadioButtonGroup(wx.Panel): # <class T>
    ''' Put together as the CalChoice. The tuples are actually
        the name of each button, but is associated with the underlying
        attribute which is not necessarily a string. The dictionary
        is of type (String -> T) where T is generic '''
    def __init__(self, a_items, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.selection_handlers = []
        self.elements = {}

        sizer = wx.GridSizer(len(a_items), 1)
        i = 0
        for (key, val) in a_items:
            tmp = wx.RadioButton(self, wx.ID_ANY, key)
            tmp.Bind(wx.EVT_RADIOBUTTON, self.__mk_event_handler(val))
            self.elements[key] = tmp
            sizer.Add(tmp, i, wx.EXPAND)
            i += 1
        self.selection = None
        self.SetSizerAndFit(sizer)

    ''' Return the currently selected item '''
    def get_selection(self):
        return self.selection
        
    ''' The listener needs to be a function that
        takes the type T and does something '''
    def add_change_listener(self, handler):
        self.selection_handlers.append(handler)

    def __mk_event_handler(self, typ):
        # This is a curried function
        def handle(_):
            self.selection = typ
            for f in self.selection_handlers: f(typ)
        return handle

class CalCheckboxPanel(wx.Panel): # <class T>
    ''' Same concept as above '''
    def __init__(self, a_items, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.change_handlers = []
        self.elements = {}

        sizer = wx.GridSizer(len(a_items), 1)
        i = 0
        for (key, val) in a_items:
            tmp = wx.CheckBox(self, wx.ID_ANY, key)
            tmp.Bind(wx.EVT_CHECKBOX, self.__mk_event_handler(val))
            self.elements[key] = (val, tmp)
            sizer.Add(tmp, i, wx.EXPAND)
            i += 1
        self.SetSizerAndFit(sizer)
        self.selected = []

    ''' func :: [T] -> T -> void 
        that is, func takes the list of selected
        attributtes and the newly added one and
        does not return anything '''
    def add_change_listener(self, func):
        self.change_handlers.append(func)

    def fire_change(self, new):
        self.selected = self.__get_selected()
        for f in self.change_handlers:
            f(self.selected, new)

    def get_selected(self):
        return self.selected

    def __get_selected(self):
        ret = []
        for (_, (val, chk)) in self.elements.items():
            if chk.IsChecked():
                ret.append(val)
        return ret

    def __mk_event_handler(self, new):
        def handle(_):
            #new.Skip()
            self.fire_change(new)
        return handle

class CalListBox(wx.ListBox):
    ''' Choices is a list of tuples like the rest '''
    def __init__(self, choices, *args, **kwargs):
        snd = [a for (_, a) in choices] # unzip the choices
        fst = [a for (a, _) in choices]
        wx.ListBox.__init__(self, choices=fst, *args, **kwargs)
        self.selection_listeners = []
        self.values = snd
        self.selections = ()
        self.Bind(wx.EVT_LISTBOX, lambda _: self.fire_selection_event())

    def fire_selection_event(self):
        selections = self.__get_selections()
        for f in self.selection_listeners:
            f(selections)

    ''' Returns a [T] '''
    def get_selections(self):
        return self.selections

    ''' Returns a [T] '''
    def __get_selections(self):
        # Get all of the selected values
        self.selections = [self.values[i]
                            for i in range(len(self.values))
                                if self.IsSelected(i)]
        return self.get_selections()
    
    ''' Listener must be of type [T] -> void '''
    def add_change_listener(self, listener):
        self.selection_listeners.append(listener)

"""We want the pane to be invisible when collapsed, so we have to make some
minor modifications to PyCollapsiblePane
I'm stealing and throwing out a lot of what this class does. Might be good to
look in to exactly what of it we're using and maybe just write our own class if
it would be smaller than the below.
"""
class CalCollapsiblePane(pcp.PyCollapsiblePane):

    #Copied code below from wx source so I could make a few modifications.
    #Fixing the bug of the small extra space above the bar. Essentially, I've
    #taken over the AGW flag CP_GTK_EXPANDER to mean no expander at all.
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, agwStyle=wx.CP_DEFAULT_STYLE |
                 wx.CP_GTK_EXPANDER, validator=wx.DefaultValidator,
                 name="PyCollapsiblePane"):
        """
        Default class constructor.

        :param `parent`: the L{PyCollapsiblePane} parent. Must not be ``None``;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `label`: The initial label shown in the button which allows the
         user to expand or collapse the pane window.
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `style`: the underlying `wx.PyPanel` window style;
        :param `agwStyle`: the AGW-specifi window style. This can be a combination of the
         following bits:

         ==================== =========== ==================================================
         Window Styles        Hex Value   Description
         ==================== =========== ==================================================
         ``CP_NO_TLW_RESIZE``         0x2 By default L{PyCollapsiblePane} resizes the top level window containing it when its own size changes. This allows to easily implement dialogs containing an optionally shown part, for example, and so is the default behaviour but can be inconvenient in some specific cases -- use this flag to disable this automatic parent resizing then.
         ``CP_GTK_EXPANDER``          0x4 Uses a GTK expander instead of a button.
         ``CP_USE_STATICBOX``         0x8 Uses a `wx.StaticBox` around L{PyCollapsiblePane}.
         ``CP_LINE_ABOVE``           0x10 Draws a line above L{PyCollapsiblePane}.
         ==================== =========== ==================================================

        :param `validator`: the validator associated to the L{PyCollapsiblePane};
        :param `name`: the widget name.

        """

        wx.PyPanel.__init__(self, parent, id, pos, size, style, name)

        self._pButton = self._pStaticLine = self._pPane = self._sz = None
        self._strLabel = label
        self._bCollapsed = True
        self._agwStyle = agwStyle

        self._pPane = wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        self._pPane.Hide()

        self._pButton = wx.Button(self)
        self._pButton.Hide()
        self._sz = wx.BoxSizer(wx.HORIZONTAL)
        self.SetExpanderDimensions(0, 0)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        if self.IsExpanded():
            self.expanded_width = self.GetSize().width

    def DoGetBestSize(self):
        """Overriding PyCollapsiblePane's DoGetBestSize()"""
        if self.IsExpanded():
            return super(CalCollapsiblePane, self).DoGetBestSize()
        else:
            return wx.Size(0,0)

    #Below copied from wxPython source exactly, then modified to fix the bug where
    #collapsing the options pane resized the window
    def OnStateChange(self, sz):
        """
        Handles the status changes (collapsing/expanding).

        :param `sz`: an instance of `wx.Size`.
        """
        # minimal size has priority over the best size so set here our min size
        self.SetMinSize(sz)
        self.SetSize(sz)
        if self.IsExpanded():
            self.expanded_width = self.GetSize().width

        if self.HasAGWFlag(wx.CP_NO_TLW_RESIZE):
            # the user asked to explicitely handle the resizing itself...
            return

        # NB: the following block of code has been accurately designed to
        #     as much flicker-free as possible be careful when modifying it!

        top = wx.GetTopLevelParent(self)
        if top:
            # NB: don't Layout() the 'top' window as its size has not been correctly
            #     updated yet and we don't want to do an initial Layout() with the old
            #     size immediately followed by a SetClientSize/Fit call for the new
            #     size that would provoke flickering!

            # we shouldn't attempt to resize a maximized window, whatever happens
            if not top.IsMaximized():

                cur_size = top.GetSize()
                if self.IsCollapsed(): # expanded -> collapsed transition
                   cur_size.width -= self.expanded_width
                else: #collapsed -> expanded transition
                    cur_size.width += self.GetSize().width
                top.SetSize(cur_size)

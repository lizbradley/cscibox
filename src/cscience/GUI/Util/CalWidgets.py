"""
File for storing valuable widgets. Let us avoid the
God file.
"""

import wx

"""
Simply a combo box with a more abstracted interface
as a dictionary of choices and arguments to actions.
"""
class CalChoice(wx.Choice): # <class T>
    # Choices is a dictionary of (string -> T)
    def __init__(self, parent, choices):
        items = choices.items() # list of (string,T)
        strings, self.values = zip( *items ) # unzip -- because python :-(

        wx.Choice.__init__(self, parent, wx.NewId(), choices=strings)

        self.listeners = []
        self.Bind(wx.EVT_CHOICE,self.__options_changed,id=self.GetId())

    # attaches a listener which is
    # fired once an event occured in general
    #
    # f : Function (T -> void)
    def attach_selection_listener( self, f ):
        self.listeners.append(f)

    # Called when the options have changed
    def __options_changed(self,_):
        t = self.values[self.GetCurrentSelection()]
        
        # Iterate through all of the listeners!
        for f in self.listeners:
            f(t)

import wx
from wx.lib.agw import aui
from cscience.GUI import icons

from cscience.GUI.Util.CalWidgets import CalChoice

''' Class which is a toolbar specific to the
PlotWindow '''
class Toolbar(aui.AuiToolBar): # {
    def __init__(self, parent, indattrs):
        aui.AuiToolBar.__init__(self, parent, wx.ID_ANY,
                                  agwStyle=aui.AUI_TB_HORZ_TEXT)
        self.icons = self.setup_art()

        self.invar_change_listener = None
        self.options_pressed_listener = None
        
        # Checkbox's to tell which axis should be on the
        # bottom. {
        text = "Independent Axis:"
        self.AddLabel(wx.ID_ANY, text, width=self.GetTextExtent(text)[0])
    
        l_id = wx.NewId()
        self.AddRadioTool(l_id, '',
                          self.icons['y_axis'], 
                          self.icons['y_axis'])

        l_id = wx.NewId()
        self.AddRadioTool(l_id, '',
                          self.icons['x_axis'], 
                          self.icons['x_axis'])
        # }

        # The different choices for the data to plot {
        choice_arr = [(i,None) for i in indattrs]
        choice_dict = dict(choice_arr)
        invar_choice = CalChoice(self, choice_dict) 
        invar_choice.add_change_listener( lambda x: self.__on_invar_changed(x) )

        self.AddControl(invar_choice)

        choice_dict = dict(choice_arr + [('<Multiple>','')])
        depvar_choice = CalChoice(self, choice_dict) 
        self.AddControl(depvar_choice)
        # }


        self.AddSeparator()

        options_button_id = wx.NewId()

        self.AddSimpleTool(options_button_id, "", self.icons['graphing_options'])

        self.Realize()
        self.Bind(wx.EVT_TOOL, self.__on_options_pressed, id=options_button_id)
    
    def __on_invar_changed( self, invar ):
        self.invar_change_listener(invar)

    def on_invar_changed_do( self, func ):
        self.invar_change_listener = func

    def on_options_pressed_do( self, func ):
        # do something when the options button is pressed 
        self.options_pressed_listener = func

    def get_dependent_variable( self, func ):
        self.depvar_choice.get_selection()

    def __on_options_pressed(self, _):
        self.options_pressed_listener()

    def setup_art(self):
        # Setup the dictionary of artwork for easier and
        # more terse access to the database of icons
        art = [
              ("radio_on",icons.ART_RADIO_ON)
            , ("radio_off", icons.ART_RADIO_OFF)
            , ("graphing_options", icons.ART_GRAPHING_OPTIONS)
            , ("x_axis", icons.ART_X_AXIS)
            , ("y_axis", icons.ART_Y_AXIS)
            ]

        art_dic = {}
        for (name, loc) in art:
            art_dic[name] = wx.ArtProvider.GetBitmap(
                loc, wx.ART_TOOLBAR, (16, 16))
        return art_dic
# }

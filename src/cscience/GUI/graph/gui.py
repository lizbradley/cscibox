import os

import wx
from wx.lib.agw import aui
from wx.lib.agw import persist

from cscience.GUI import icons

import backend, options, plotting, events

def get_distribution(original_point):
    dist = original_point.uncertainty.distribution
    if hasattr(dist, "x"):
        x_points = dist.x
        y_points = dist.y
        return [backend.PlotPoint(x, y, None, None, None) for (x,y) in zip(x_points, y_points)]
    else:
        return None

class PlotWindow(wx.Frame):

    def __init__(self, parent, samples, view):
        super(PlotWindow, self).__init__(parent, wx.ID_ANY, samples[0]['core'])
        self.SetName('Plotting Window')
        
        self._mgr = aui.AuiManager(self,
                    agwFlags=aui.AUI_MGR_DEFAULT & ~aui.AUI_MGR_ALLOW_FLOATING)

        self.samples = backend.SampleCollection(samples, view)
        atts = self.samples.get_numeric_attributes()
        copts = options.PlotCanvasOptions()
        vopts = options.PlotOptionSet.from_vars(
                            atts, self.samples.get_computation_plans())
        
        self.toolbar = Toolbar(self, atts, copts, vopts)
        self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('gtoolbar').
                          Layer(10).Top().DockFixed().Gripper(False).
                          CaptionVisible(False).CloseButton(False))

        self.main_canvas = plotting.PlotCanvas(self)
        self._mgr.AddPane(self.main_canvas, aui.AuiPaneInfo().Name('Main Plot').
                          Layer(9).Left().Dock().Gripper(False).
                          CaptionVisible(False).CloseButton(False).Maximize().
                          Movable(False).Resizable(True))
        
        self.zoom_canv_ind = plotting.PlotCanvas(self)
        self._mgr.AddPane(self.zoom_canv_ind, aui.AuiPaneInfo().Name('Ivar Zoom').
                          Layer(0).Right().Top().Dock().Gripper(False).
                          CaptionVisible(False).Hide().
                          Movable(False).Resizable(True))
        self.zoom_canv_dep = plotting.PlotCanvas(self)
        self._mgr.AddPane(self.zoom_canv_dep, aui.AuiPaneInfo().Name('Dvar Zoom').
                          Layer(0).Right().Bottom().Dock().Gripper(False).
                          CaptionVisible(False).Hide().
                          Movable(False).Resizable(True))
        
        self.Bind(events.EVT_GRAPHPTS_CHANGED, self.build_pointset)
        self.Bind(events.EVT_GRAPHOPTS_CHANGED, self.update_options)
        self.Bind(events.EVT_GRAPH_PICK, self.show_zoom, self.main_canvas)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        #TODO: store options here perhaps?
        persist.PersistenceManager.Get().RegisterAndRestore(self)
        self._mgr.Update()
        
        self.build_pointset()
        
    def on_close(self, event):
        event.Skip()
        persist.PersistenceManager.Get().SaveAndUnregister(self)
        
    def show_zoom(self, event):
        self.Freeze()
            
        self.zoom_canv_ind.clear()
        self.zoom_canv_dep.clear()
        # get the distributions for both the independent
        # and dependent variables
        plot_points_x = get_distribution(event.point.xorig)
        plot_points_y = get_distribution(event.point.yorig)

        if plot_points_x:
            self.zoom_canv_ind.add_points(backend.PointSet(plot_points_x))
            self.zoom_canv_ind.update_graph()
        self._mgr.ShowPane(self.zoom_canv_ind, bool(plot_points_x))

        if plot_points_y:
            self.zoom_canv_dep.add_points(backend.PointSet(plot_points_y))
            self.zoom_canv_dep.update_graph()
        self._mgr.ShowPane(self.zoom_canv_dep, bool(plot_points_y))
        
        for pane in self._mgr.GetAllPanes():
            if pane.IsShown() and not all(pane.rect):
                #Pane is supposed to be visible but it's not showing up
                cursize = self.GetSize()
                cursize.x += pane.best_size.x
                self.SetSize(cursize)
                self.Center(wx.HORIZONTAL)
                break
        self.toolbar.enable_collapse(plot_points_x or plot_points_y)
        
        self._mgr.Update()
        self.Thaw()
        
    def collapse(self, evt=None):
        self.Freeze()
        self._mgr.ShowPane(self.zoom_canv_dep, False)
        self._mgr.ShowPane(self.zoom_canv_ind, False)
        self.toolbar.enable_collapse(False)
        
        #un-pick pt
        self._mgr.Update()
        self.Thaw()

    def build_pointset(self, evt=None):
        ivar = self.toolbar.independent_variable
        dvars = self.toolbar.depvar_options
        if not ivar:
            return

        self.main_canvas.clear()
        for dvar, opts in dvars.iteritems():
            self.main_canvas.pointsets.extend([
                        (self.samples.get_pointset(ivar, dvar, key), opts) for 
                        key, ig in opts.computation_plans.items() if ig])

        self.main_canvas.update_graph()
        
    def update_options(self, evt=None):
        self.main_canvas.canvas_options = self.toolbar.canvas_options

    def export_graph_image(self, evt=None):
        dlg = wx.FileDialog(self, message="Export plot as ...", defaultDir=os.getcwd(), 
                wildcard="Scalable Vector Graphics (*.svg)|*.svg| BMP File (*.bmp)|*.bmp| JPEG Image (*.jpg)|*.jpg| EPS File (*.eps)|*.eps| PDF File (*.pdf)|*.pdf", style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.main_canvas.export_to_file(path)
        dlg.Destroy()

class OptionsPane(wx.Dialog):
          
    def __init__(self, parent, curoptions):
        super(OptionsPane,self).__init__(parent)

        self.elements = {}
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        
        for label, key in [("Show Axes Labels", 'show_axes_labels'),
                           ("Show Legend", 'legend'),
                           ("Show Grid", 'show_grid'),
                           ("Invert X Axis", 'invert_x_axis'),
                           ("Invert Y Axis",  'invert_y_axis'),
                           ("Show Error Bars", 'show_error_bars'),
                           ("Large Font", 'large_font')]:
            cb = wx.CheckBox(self, wx.ID_ANY, label=label)
            cb.SetValue(getattr(curoptions, key))
            self.elements[key] = cb
            sizer.Add(cb, wx.EXPAND)
                 
        okbtn = wx.Button(self, wx.ID_OK)
        okbtn.SetDefault()
        cancelbtn = wx.Button(self, wx.ID_CANCEL)
        
        bsizer = wx.StdDialogButtonSizer()
        bsizer.Add(okbtn, flag=wx.ALL, border=5)
        bsizer.Add(cancelbtn, flag=wx.ALL, border=5)
        bsizer.Realize()
        sizer.Add(bsizer, border=5)
        
        self.SetSizerAndFit(sizer)
        
    def get_canvas_options(self):
        return options.PlotCanvasOptions(**dict([(key, cb.IsChecked()) 
                    for key, cb in self.elements.items()]))  

class ShapeCombo(wx.combo.OwnerDrawnComboBox):
    """
    An awesome combobox for matplotlib shapey goodness
    """
    #current failings: all my shapes are pinned to a size of ~10x10, which is
    #fine but highly important to know
    def draw_sq(dc, r): #s
        dc.DrawRectangle(r.x, r.y, 10, 10)
        
    def draw_cir(dc, r): #o
        dc.DrawCircle(r.x+5, r.y+5, 5)

    def draw_tri(dc, r): #^
        dc.DrawPolygon([(r.x, r.y+10), (r.x+5, r.y), (r.x+10, r.y+10)])
       
    def draw_dia(dc, r): #d
        dc.DrawPolygon([(r.x+2, r.y+5), (r.x+5, r.y), 
                        (r.x+8, r.y+5), (r.x+5, r.y+10)])
    
    def draw_sta(dc, r): #*
        dc.DrawPolygon([(r.x+2, r.y+10), (r.x+3, r.y+7),
                        (r.x, r.y+4), (r.x+4, r.y+4),
                        (r.x+5, r.y), (r.x+6, r.y+4),
                        (r.x+10, r.y+4), (r.x+7, r.y+7),
                        (r.x+8, r.y+10), (r.x+5, r.y+8)])
        
    SHAPES = {'s':draw_sq, 'o':draw_cir, 
              '^':draw_tri, 'd':draw_dia, 
              '*':draw_sta, '':lambda *args:0}
    
    def __init__(self, *args, **kwargs):
        super(ShapeCombo, self).__init__(*args, choices=('s', 'o', '^', 'd', '*', ''),
                                         style=wx.CB_READONLY, size=(48,-1), **kwargs)
    
    def OnDrawItem(self, dc, rect, item, flags):
        """
        Draws each item in the drop-down
        """
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)
        
        shape = self.GetString(item)
        dc.SetBrush(wx.Brush((0,0,0)))
        dc.SetPen(wx.Pen((0,0,0))) #even if we're highlighted, keep the pen black
        ShapeCombo.SHAPES[shape](dc, r)
    
    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        return 24
    
    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return 24
    

class StylePane(wx.Dialog):    
    class PaneRow(object):
        def __init__(self, parent, gsizer, row, name, option):
            
            self.checkbox = wx.CheckBox(parent, wx.ID_ANY, name)
            self.checkbox.SetValue(option.is_graphed)
            self.colorpicker = wx.ColourPickerCtrl(parent, wx.ID_ANY)
            self.colorpicker.SetColour(option.color)
            self.stylepicker = ShapeCombo(parent)
            self.stylepicker.SetStringSelection(option.fmt)
            self.interpchoice = wx.Choice(parent, choices=option.interpolations.keys())
            self.interpchoice.SetStringSelection(option.interpolation_strategy)
            self.chooseplan = wx.Button(parent, wx.ID_ANY, "Computation Plan..")
            self.planpopup = wx.PopupTransientWindow(parent, style=wx.SIMPLE_BORDER)
            self.planlist = wx.CheckListBox(self.planpopup, 
                                choices=option.computation_plans.keys())
            self.planlist.SetCheckedStrings([key for key, val in 
                                option.computation_plans.items() if val])
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.planlist, flag=wx.EXPAND, proportion=1)
            self.planpopup.SetSizerAndFit(sizer)
            
            parent.Bind(wx.EVT_BUTTON, self.popup_cplan, self.chooseplan)            
            gsizer.Add(self.checkbox, (row, 0), flag=wx.RIGHT, border=10)
            gsizer.Add(self.colorpicker, (row, 1))
            gsizer.Add(self.stylepicker, (row, 2))
            gsizer.Add(self.interpchoice, (row, 3))
            gsizer.Add(self.chooseplan, (row, 4))
            
        def popup_cplan(self, event):
            pos = self.chooseplan.ClientToScreen((0,0))
            sz = self.chooseplan.GetSize()
            self.planpopup.Position(pos, (0, sz[1]))
            self.planpopup.Popup()
        
        def get_option(self):
            cplans = dict([(plan, False) for plan in self.planlist.GetStrings()])
            for sel in self.planlist.GetCheckedStrings():
                cplans[sel] = True            
                        
            return options.PlotOptions(
                        is_graphed=self.checkbox.GetValue(),
                        color=self.colorpicker.GetColour(),
                        #GetStringSelection seems to be fussy; this seems to work in all cases.
                        fmt=self.stylepicker.GetString(self.stylepicker.GetSelection()),
                        interpolation_strategy=self.interpchoice.GetStringSelection(),
                        computation_plans=cplans)
    
    def __init__(self, parent, curoptions):
        super(StylePane, self).__init__(parent, wx.ID_ANY)
        
        self.vars = {}

        sizer = wx.GridBagSizer(2, 2)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Enabled"), (0, 0), flag=wx.RIGHT, border=10)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Color"), (0, 1))
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Style"), (0, 2))
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Interpolation"), (0, 3))
        
        optset = curoptions.items()
        optset.sort()
        for row, (name, opts) in enumerate(optset, 1):
            self.vars[name] = StylePane.PaneRow(self, sizer, row, name, opts)

        okbtn = wx.Button(self, wx.ID_OK)
        okbtn.SetDefault()
        cancelbtn = wx.Button(self, wx.ID_CANCEL)

        bsizer = wx.StdDialogButtonSizer()
        bsizer.AddButton(okbtn)
        bsizer.AddButton(cancelbtn)
        bsizer.Realize()

        sizer.AddGrowableCol(1)
        sizer.Add(bsizer, (row+1, 0), (1, 4))
        self.SetSizerAndFit(sizer)

    def get_option_set(self):
        return options.PlotOptionSet([(name, pane.get_option()) for 
                                      name, pane in self.vars.items()])

# class specific to a toolbar in the plot window
class Toolbar(aui.AuiToolBar):

    def __init__(self, parent, indattrs, baseopts, varopts):
        super(Toolbar, self).__init__(parent, wx.ID_ANY, agwStyle=aui.AUI_TB_HORZ_TEXT)
        
        #TODO: it ought to be possible to have the aui toolbar stuff manage
        #this guy more automagically
        depvar_id = wx.NewId()
        self.AddSimpleTool(depvar_id, 'Plot...',
            wx.ArtProvider.GetBitmap(icons.ART_GRAPHED_LINES, wx.ART_TOOLBAR, (16, 16)))
        self.AddLabel(wx.ID_ANY, 'vs', 13)
        self.invar_choice = wx.Choice(self, wx.ID_ANY, choices=indattrs)
        self.invar_choice.SetStringSelection('depth')
        self.AddControl(self.invar_choice)
        
        
        self.AddSeparator()
        export_id = wx.NewId()
        self.AddSimpleTool(export_id, 'Export...',
            wx.ArtProvider.GetBitmap(icons.ART_SAVE_IMAGE, wx.ART_TOOLBAR, (16, 16)))
        
        self.AddSeparator()
        options_id = wx.NewId()
        self.AddSimpleTool(options_id, 'Options',
            wx.ArtProvider.GetBitmap(icons.ART_GRAPHING_OPTIONS, wx.ART_TOOLBAR, (16, 16)))
        
        self.AddStretchSpacer()
        self.contract_id = wx.NewId()
        self.AddTool(self.contract_id, '',
            wx.ArtProvider.GetBitmap(icons.ART_CONTRACT_RS, wx.ART_TOOLBAR, (16, 16)),
            wx.NullBitmap, kind=aui.ITEM_NORMAL)
        self.EnableTool(self.contract_id, False)
        
        self.canvas_options = baseopts
        self.depvar_options = varopts
        
        self.Bind(wx.EVT_TOOL, self.show_options, id=options_id)
        self.Bind(wx.EVT_TOOL, self.show_dep_styles, id=depvar_id)
        self.Bind(wx.EVT_CHOICE, self.vars_changed, self.invar_choice)
        self.Bind(wx.EVT_WINDOW_MODAL_DIALOG_CLOSED, self.dialog_done)
        
        #these are handled by parent...
        self.Bind(wx.EVT_TOOL, self.Parent.export_graph_image, id=export_id)
        self.Bind(wx.EVT_TOOL, self.Parent.collapse, id=self.contract_id)
    
        self.Realize()        

    def enable_collapse(self, enable):
        self.EnableTool(self.contract_id, enable)

    def vars_changed(self, evt=None):
        wx.PostEvent(self, events.PointsChangedEvent(self.GetId()))
        
    def show_dep_styles(self, evt=None):
        StylePane(self, self.depvar_options).ShowWindowModal()
    
    def show_options(self, evt=None):
        OptionsPane(self, self.canvas_options).ShowWindowModal()
            
    def dialog_done(self, event):
        dlg = event.GetDialog()
        btn = event.GetReturnCode()
        if btn == wx.ID_OK:
            if hasattr(dlg, 'get_canvas_options'):
                self.canvas_options = dlg.get_canvas_options()
                wx.PostEvent(self, events.OptionsChangedEvent(self.GetId()))
            if hasattr(dlg, 'get_option_set'):
                self.depvar_options = dlg.get_option_set()
                self.vars_changed()
        dlg.Destroy()
            
            
    @property
    def independent_variable(self):
        return self.invar_choice.GetStringSelection()



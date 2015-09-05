import wx
import wx.lib.newevent

PointsChangedEvent, EVT_GRAPHPTS_CHANGED = wx.lib.newevent.NewCommandEvent()
OptionsChangedEvent, EVT_GRAPHOPTS_CHANGED = wx.lib.newevent.NewCommandEvent()
GraphPickEvent, EVT_GRAPH_PICK = wx.lib.newevent.NewCommandEvent()
RefreshAIEvent, EVT_REFRESH_AI = wx.lib.newevent.NewEvent()

R2ValueUpdateEvent, EVT_R2_UPDATE = wx.lib.newevent.NewCommandEvent()


import wx
import time
import cscience.GUI.graph.events


def run_with_annotations(annotations):
    time.sleep(0.5)

    print(annotations)

    evt = cscience.GUI.graph.events.RefreshAIEvent(att1='hi', att2=123)
    plotter_hndl = wx.FindWindowByName('Plotting Window')

    wx.PostEvent(plotter_hndl, evt)

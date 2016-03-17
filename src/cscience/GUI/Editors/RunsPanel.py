import wx

try:
    from agw import customtreectrl as CT
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as CT

class RunsPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY):
        super(wx.RunsPanel, self).
            __init__(parent, id, style=wx.RAISED_BORDER)

        self._m_tree = CT.CustomTreeCtrl(selfl)
        root = self._m_tree.AddRoot("Runs")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._m_tree, border=10)
        self.SetSizerAndFit(sizer)

    def add_run(self, run):
        runid = self._m_tree.AppendItem(root, run.name, ct_type=1)
        self._m_tree.AppendItem(runid, run.computation_plan["name"]);
        self._m_tree.AppendItem(runid, str(run.created_time));


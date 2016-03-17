import wx

import time
from cscience.framework import ComputationPlan
from cscience.framework.samples import Run

try:
    from agw import customtreectrl as CT
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.customtreectrl as CT

RUNS_PANEL_RENAME_ID = wx.NewId()
RUNS_PANEL_DELETE_ID = wx.NewId()

class RunsPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY):
        super(RunsPanel, self).__init__(parent, id, style=wx.RAISED_BORDER)

        self._m_tree = CT.CustomTreeCtrl(self)
        self._m_root = self._m_tree.AddRoot("Runs")
        self._m_clicked_item = None

        # a mapping from id's to the underlying objects
        self._m_id_map = {}

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._m_tree, wx.EXPAND, wx.EXPAND, border=10)
        self.SetSizerAndFit(sizer)

        self._m_tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        self._m_tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_edit_end)
        self._m_tree.Bind(wx.EVT_TREE_DELETE_ITEM, self.on_delete_item2)
        self._m_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_activated)

    def on_item_activated(self, evt):
        evt_item = evt.GetItem()

        if evt_item not in self._m_id_map:
            return

        if isinstance(self._m_id_map[evt_item], Run):
            self._m_tree.SetItemTextColour(evt.GetItem(), wx.Colour(0, 0, 0))

    def on_delete_item2(self, evt):
        if evt.GetItem() in self._m_id_map:
            del self._m_id_map[evt.GetItem()]

    def on_edit_item(self, evt):
        evt_item = self._m_clicked_item
        self._m_tree.EditLabel(evt_item)

    def on_delete_item(self, evt):
        evt_item = self._m_clicked_item
        self._m_tree.Delete(evt_item)

    def on_edit_end(self, evt):
        evt_item = evt.GetItem()

        if evt_item not in self._m_id_map:
            return

        associated_object = self._m_id_map[evt_item]

        print ("Update run. Set name = %s" % evt.GetLabel())
        if isinstance(associated_object, Run):
            associated_object.name = evt.GetLabel()

    def on_right_click(self, evt):
        evt_item = evt.GetItem()

        if evt_item not in self._m_id_map:
            return

        menu = None
        associated_object = self._m_id_map[evt_item]
        self._m_clicked_item = evt_item

        # begin case matching
        if isinstance(associated_object, ComputationPlan):
            menu = wx.Menu()
            menu.Append(wx.NewId(), "Rerun with different parameters")

        elif isinstance(associated_object, Run):
            menu = wx.Menu()

            menu.Append(RUNS_PANEL_RENAME_ID, "Rename")
            menu.Append(RUNS_PANEL_DELETE_ID, "Delete")

            wx.EVT_MENU(menu, RUNS_PANEL_RENAME_ID, self.on_edit_item)
            wx.EVT_MENU(menu, RUNS_PANEL_DELETE_ID, self.on_delete_item)
        # end case matching

        if menu:
            self._m_tree.PopupMenu(menu, evt.GetPoint())
            menu.Destroy()

    def add_run(self, run):
        run_id   = self._m_tree.AppendItem(self._m_root, run.name, ct_type=1)
        cplan_id = self._m_tree.AppendItem(run_id, run.computation_plan["name"]);
        date_id  = self._m_tree.AppendItem(run_id, time.strftime("%Y-%M-%D %H:%M:%S", run.created_time));
        self._m_tree.SetItemTextColour(run_id, wx.Colour(255, 0, 0))

        self._m_id_map[run_id] = run
        self._m_id_map[cplan_id] = run.computation_plan
        self._m_id_map[date_id] = run.created_time



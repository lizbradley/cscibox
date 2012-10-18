"""
CollectionBrowser.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import os.path

import wx
import wx.grid

from ACE.Framework.Collections        import Collections
from ACE.GUI.Dialogs.CreateCollection import CreateCollection

class CollectionBrowser(wx.Frame):
    def __init__(self,parent,repoman):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='Collection Browser')

        self.repoman = repoman

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        self.menuBar   = wx.MenuBar()
        
        editMenu = wx.Menu()
        copyItem = editMenu.Append(wx.ID_COPY, "Copy\tCtrl-C", "Copy selected collection items.")
        
        editMenu.Enable(wx.ID_COPY, False)
        
        self.menuBar.Append(editMenu, "Edit")

        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)
        
        collectionsLabel = wx.StaticText(self, wx.ID_ANY, "Data Collections")
        self.collectionLabel  = wx.StaticText(self, wx.ID_ANY, "Data Collection Type: <None>")
        
        self.collections = self.repoman.GetModel("Collections")
        self.collection  = None
        self.templates   = self.repoman.GetModel("Templates")
        
        self.collections_list = wx.ListBox(self, wx.ID_ANY, choices=self.collections.names(), style=wx.LB_SINGLE)

        self.grid   = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(1,1)
        self.grid.SetCellValue(0,0, "No Collection Selected.")
        self.grid.SetRowLabelValue(0, "")
        self.grid.SetColLabelValue(0, "")
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.AutoSize()
        self.grid.EnableEditing(False)

        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect, self.grid)
        
        self.selected_rows = set()

        self.ConfigureGrid()

        self.addButton    = wx.Button(self, wx.ID_ANY, "Create Data Collection...")
                
        columnOneSizer = wx.BoxSizer(wx.VERTICAL)
        columnOneSizer.Add(collectionsLabel, border=5, flag=wx.ALL)
        columnOneSizer.Add(self.collections_list, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        
        columnTwoSizer = wx.BoxSizer(wx.VERTICAL)
        columnTwoSizer.Add(self.collectionLabel)
        columnTwoSizer.Add(self.grid, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton,    border=5, flag=wx.ALL)

        columnSizer = wx.BoxSizer(wx.HORIZONTAL)
        columnSizer.Add(columnOneSizer, proportion=1, flag=wx.EXPAND)
        columnSizer.Add(columnTwoSizer, proportion=2, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(columnSizer, proportion=1, flag=wx.EXPAND)
        sizer.Add(buttonSizer, border=5, flag=wx.ALL)
        
        self.SetSizer(sizer)
        self.Layout()
        self.SetSize(self.GetBestSize())
        self.SetMinSize(self.GetSize())
        
        config = self.repoman.GetConfig()
        size   = eval(config.Read("windows/collectionbrowser/size", repr(self.GetSize())))
        loc    = eval(config.Read("windows/collectionbrowser/location", repr(self.GetPosition())))
        
        self.SetSize(size)
        self.SetPosition(loc)
        
        self.Bind(wx.EVT_BUTTON, self.OnCreateCollection, self.addButton)

        self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.collections_list)

        self.collections_list.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        repoman.AddWindow(self)

    def OnMove(self, event):
        x, y = event.GetPosition()
        config = self.repoman.GetConfig()
        config.Write("windows/collectionbrowser/location", "(%d,%d)" % (x,y))

    def OnSize(self, event):
        width, height = event.GetSize()
        config = self.repoman.GetConfig()                                                                                                   
        config.Write("windows/collectionbrowser/size", "(%d,%d)" % (width,height))
        self.Layout()

    def OnCloseWindow(self, event):
        self.repoman.RemoveWindow(self)
        self.GetParent().collectionBrowser = None
        del(self.GetParent().collectionBrowser)
        self.Destroy()

    # list box controls do not deliver deselection events when in 'single selection' mode
    # but it is still possible for the user to clear the selection from such a list
    # as such, we need to monitor the LEFT_UP events for each of our list boxes and
    # check to see if the selection got cleared without us knowning about it
    # if so, we need to update the user interface appropriately
    # this code falls under the category of "THIS SUCKS!" It would be much cleaner to
    # just be informed of list deselection events
    def OnLeftUp(self, event):
        index = self.collections_list.GetSelection()
        if index == -1:
            self.collection  = None
            self.ConfigureGrid()
            self.collectionLabel.SetLabel("Data Collection Type: <None>")
            self.Layout()
        event.Skip()

    def ConfigureGrid(self):
        self.grid.BeginBatch()
        if (self.grid.GetNumberCols() > 0):
            self.grid.DeleteCols(0, self.grid.GetNumberCols())
        if (self.grid.GetNumberRows() > 0):
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        if self.collection == None:
            self.grid.AppendRows(1)
            self.grid.AppendCols(1)
            self.grid.SetCellValue(0,0, "No Collection Selected.")
            self.grid.SetRowLabelValue(0, "")
            self.grid.SetColLabelValue(0, "")
            self.grid.AutoSize()
        else:
            fields = self.template.get_order()
            keys   = self.template.get_keys()
            
            self.grid.AppendRows(len(self.collection))
            self.grid.AppendCols(len(fields))

            for column, key in enumerate(keys):
                self.grid.SetColLabelValue(column, key)
                fields.remove(key)

            for column, att in enumerate(fields):
                    self.grid.SetColLabelValue(column+len(keys), att)
            
            for row, index in enumerate(sorted(self.collection.keys())):
                self.grid.SetRowLabelValue(row, "")

                if type(index) is not tuple:
                    tuple_index = (index,)
                else:
                    tuple_index = index
                
                for col in range(len(keys)):
                    self.grid.SetCellValue(row, col, str(tuple_index[col]))
                    
                if len(fields) == 1:
                    self.grid.SetCellValue(row, len(keys), str(self.collection[index]))
                else:
                    for col, att in enumerate(fields):
                        self.grid.SetCellValue(row, col+len(keys), str(self.collection[index][att]))
                
            self.grid.AutoSize()
            
        h,w = self.grid.GetSize()
        self.grid.SetSize((h+1, w))
        self.grid.SetSize((h, w))
        self.grid.EndBatch()
        self.grid.ForceRefresh()
        self.Layout()
        
    def OnRangeSelect(self, event):

        start = event.GetTopLeftCoords()[0]
        stop  = event.GetBottomRightCoords()[0]
        
        if event.Selecting():
            # print "Selecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop+1):
                self.selected_rows.add(i)
            # print "selected rows: %s" % self.selected_rows
        else:
            # print "DeSelecting: (%d, %d)" % (event.GetTopLeftCoords()[0], event.GetBottomRightCoords()[0])
            for i in range(start, stop+1):
                if i in self.selected_rows:
                    self.selected_rows.remove(i)
            # print "selected rows: %s" % self.selected_rows
            
        editMenu = self.menuBar.GetMenu(self.menuBar.FindMenu("Edit"))
        editMenu.Enable(wx.ID_COPY, False)

        if len(self.selected_rows) > 0:
            editMenu.Enable(wx.ID_COPY, True)

    def OnCopy(self, event):
        indexes = sorted(list(self.selected_rows))

        cols = self.grid.GetNumberCols()
        
        result = ""
        
        for i in range(cols):
            result = result + self.grid.GetColLabelValue(i) + "\t"
            
        result = result[0:-1]
        result = result + os.linesep
        
        for row in indexes:
            for col in range(cols):
                result = result + self.grid.GetCellValue(row, col) + "\t"
            result = result[0:-1]
            result = result + os.linesep

        data = wx.TextDataObject()
        data.SetText(result)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def OnCreateCollection(self, event):
        dlg = CreateCollection(self)
        if dlg.ShowModal() == wx.ID_OK:
            name          = dlg.get_name()
            template_name = dlg.get_template()
            path          = dlg.get_path()

            if name != "":
                if not self.collections.contains(name):
                    if template_name != "":
                        if path != "" and os.path.exists(path):
                            templates = self.repoman.GetModel("Templates")
                            template  = templates.get(template_name)
                            collection = template.newCollection(path)
                            self.collections.add(name,template_name,collection)
                            self.collections_list.Set(self.collections.names())
                            self.repoman.RepositoryModified()
                        else:
                            dialog = wx.MessageDialog(None, 'Problem with path name!', "Illegal Path Name", wx.OK | wx.ICON_INFORMATION)
                            dialog.ShowModal()
                    else:
                        dialog = wx.MessageDialog(None, 'Template name not specified!', "Illegal Template Name", wx.OK | wx.ICON_INFORMATION)
                        dialog.ShowModal()
                else:
                    dialog = wx.MessageDialog(None, 'Collection "' + name + '" already exists!', "Duplicate Collection", wx.OK | wx.ICON_INFORMATION)
                    dialog.ShowModal()
            else:
                dialog = wx.MessageDialog(None, 'Collection name not specified!', "Illegal Collection Name", wx.OK | wx.ICON_INFORMATION)
                dialog.ShowModal()
        dlg.Destroy()

    def OnSelect(self, event):
        name = self.collections_list.GetStringSelection()
        self.collection = self.collections.get(name)
        template_name = self.collections.get_template(name)
        self.template = self.templates.get(template_name)
        self.collectionLabel.SetLabel("Data Collection Type: %s" % (template_name))
        self.grid.ClearSelection()
        self.ConfigureGrid()
        self.Layout()

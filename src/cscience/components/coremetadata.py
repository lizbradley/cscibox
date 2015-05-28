"""
coremetadata.py

* Copyright (c) 2012-2015, University of Colorado.
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

This module lays out the data structure for displaying metadata of cores and virtual cores
"""

import wx
import wx.dataview as dv
import traceback

""" Code adapted from DVC_DataViewModel.py in demo code """

#----------------------------------------------------------------------
# We'll use instaces of these classes to hold our music data. Items in the
# tree will get associated back to the coresponding mdCoreAttribute or core object.

class mdCoreAttribute(object):
    # Attributes for a mdCore or mdVirtualCore
    def __init__(self, id, cplan, att, value, core):
        self.att = att
        self.value = value  # convert the value to string for display
        self.parent = core
        self.cplan = cplan
        self.id = id

    def __repr__(self):
        return 'Attribute: %s-%s' % (self.att, self.value)

class mdCore(object):
    # metadata for original imported core, with no computation plan
    def __init__(self, name):
        self.name = name
        self.atts = []
        self.vcs = []

    def __repr__(self):
        return 'Core: ' + self.name

class mdVirtualCore(mdCore):
    # metadata for a virtualcore: has a parent core
    def __init__(self,id, parent, name):
        mdCore.__init__(self, name)
        self.parent = parent
        self.id = str(id)

    def __repr__(self):
        return 'VC: ' + self.name

#----------------------------------------------------------------------

class CoreMetaData(dv.PyDataViewModel):
    def __init__(self, data):
        dv.PyDataViewModel.__init__(self)
        self.data = data
        self.log = []

        # The objmapper is an instance of DataViewItemObjectMapper and is used
        # to help associate Python objects with DataViewItem objects. Normally
        # a dictionary is used so any Python object can be used as data nodes.
        # If the data nodes are weak-referencable then the objmapper can use a
        # WeakValueDictionary instead. Each PyDataViewModel automagically has
        # an instance of DataViewItemObjectMapper preassigned. This
        # self.objmapper is used by the self.ObjectToItem and
        # self.ItemToObject methods used below.
        self.objmapper.UseWeakRefs(True)


    # Report how many columns this model provides data for.
    def GetColumnCount(self):
        #print('GetColumnCount')
        return len(self.GetColumnMap())

    # Store the column data types
    def GetColumnMap(self):
        mapper = { 0 : 'string',
                   1 : 'string',
                   2 : 'string'
                   }
        return mapper

    # Return type of specific column
    def GetColumnType(self, col):
        #print('GetColType')
        mapper = self.GetColumnMap()
        return mapper[col]

    def GetChildren(self, parent, children):
        #print('GetChildren')
        # The view calls this method to find the children of any node in the
        # control. There is an implicit hidden root node, and the top level
        # item(s) should be reported as children of this node. A List view
        # simply provides all items as children of this hidden root. A Tree
        # view adds additional items as children of the other items, as needed,
        # to provide the tree hierachy.
        ##self.log.write("GetChildren\n")

        # If the parent item is invalid then it represents the hidden root
        # item, so we'll use the core objects as its children and they will
        # end up being the collection of visible roots in our tree.

        if not parent:
            for core in self.data:
                children.append(self.ObjectToItem(core))
            return len(self.data)

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of it's child objects.
        node = self.ItemToObject(parent)

        if isinstance(node, mdVirtualCore):
            for mdcatt in node.atts:
                children.append(self.ObjectToItem(mdcatt))
            return len(node.atts)

        elif isinstance(node, mdCore):
            for mdvc in node.vcs:
                children.append(self.ObjectToItem(mdvc))
            for mdcatt in node.atts:
                children.append(self.ObjectToItem(mdcatt))
            return len(node.atts) + len(node.vcs)

        return 0

    def IsContainer(self, item):
        #print('IsContainer')
        # Return True if the item has children, False otherwise.
        ##self.log.write("IsContainer\n")

        # The hidden root is a container
        if not item:
            return True
        # in this model the mdCore and mdVirtualCore objects are containers
        node = self.ItemToObject(item)
        if isinstance(node, mdCore):
            return True
        # but everything else (the mdCoreAttribute objects) are not
        return False

    def GetParent(self, item):
        #print('GetParent')
        # Return the item which is this item's parent.
        ##self.log.write("GetParent\n")

        if not item:
            return dv.NullDataViewItem

        node = self.ItemToObject(item)
        if isinstance(node, mdVirtualCore):
            return self.ObjectToItem(node.parent)
        elif isinstance(node, mdCore):
            return dv.NullDataViewItem
        elif isinstance(node, mdCoreAttribute):
            return self.ObjectToItem(node.parent)

    def GetValue(self, item, col):
        # Fetch the data object for this item.
        #print('GetValue')
        node = self.ItemToObject(item)


        if isinstance(node, mdCore):
            # Core has no parents
            mapper = { 0 : node.name,
                       1 : "",
                       2 : ""
                       }
            return mapper[col]

        elif isinstance(node, mdCoreAttribute):
            # child of virtual core
            mapper = { 0 : node.cplan,
                       1 : node.att,
                       2 : node.value
                       }
            return mapper[col]

        else:
            raise RuntimeError("unknown node type")



    def GetAttr(self, item, col, attr):
        #print('GetAttr')
        ##self.log.write('GetAttr')
        node = self.ItemToObject(item)
        if isinstance(node, mdVirtualCore):
            attr.SetColour('orange')
            return True
        elif isinstance(node, mdCore):
            attr.SetColour('black')
            attr.SetBold(True)
            return True
        elif isinstance(node, mdCoreAttribute):
            attr.SetColour('gray')
        return False


    def SetValue(self, value, item, col):
        #print('SetValue')
        # Nothing here yet
        # TODO: possibly add ability to edit some of these form here?
        return
#----------------------------------------------------------------------

import wx
import wx.dataview as dv

""" Code adapted from DVC_DataViewModel.py in demo code """

#----------------------------------------------------------------------
# We'll use instaces of these classes to hold our music data. Items in the
# tree will get associated back to the coresponding CoreAttribute or core object.

class CoreAttribute(object):
    def __init__(self, id, att, title, core):
        self.id = id
        self.att = att
        self.value = value
        self.core = core

    def __repr__(self):
        return 'Attribute: %s-%s' % (self.att, self.value)


class Core(object):
    def __init__(self, name):
        self.name = name
        self.coreAttributes = []

    def __repr__(self):
        return 'Core: ' + self.name

#----------------------------------------------------------------------

class CoreMetaData(dv.PyDataViewModel):
    def __init__(self, data, log):
        dv.PyDataViewModel.__init__(self)
        self.data = data
        self.log = log

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
        return len(self.GetcolumnMap())

    # Store the column data types
    def GetColumnMap(self):
        mapper = { 0 : 'string',
                   1 : 'string',
                   2 : 'string'
                   }
        return mapper

    # Return type of specific column
    def GetColumnType(self, col):
        mapper = self.GetColumnMap()
        return mapper[col]

    def GetChildren(self, parent, children):
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
        if isinstance(node, Core):
            for CoreAttribute in node.coreAttributes:
                children.append(self.ObjectToItem(coreAttribute))
            return len(node.coreAttributes)
        return 0


    def IsContainer(self, item):
        # Return True if the item has children, False otherwise.
        ##self.log.write("IsContainer\n")

        # The hidden root is a container
        if not item:
            return True
        # and in this model the core objects are containers
        node = self.ItemToObject(item)
        if isinstance(node, core):
            return True
        # but everything else (the coreAttribute objects) are not
        return False


    #def HasContainerColumns(self, item):
    #    self.log.write('HasContainerColumns\n')
    #    return True


    def GetParent(self, item):
        # Return the item which is this item's parent.
        ##self.log.write("GetParent\n")

        if not item:
            return dv.NullDataViewItem

        node = self.ItemToObject(item)
        if isinstance(node, Core):
            return dv.NullDataViewItem
        elif isinstance(node, CoreAttribute):
            for g in self.data:
                if g.name == node.core:
                    return self.ObjectToItem(g)


    def GetValue(self, item, col):
        # Return the value to be displayed for this item and column. For this
        # example we'll just pull the values from the data objects we
        # associated with the items in GetChildren.

        # Fetch the data object for this item.
        node = self.ItemToObject(item)

        if isinstance(node, Core):
            # We'll only use the first column for the core objects,
            # for the other columns lets just return empty values
            mapper = { 0 : node.name,
                       1 : "",
                       2 : "",
                       }
            return mapper[col]


        elif isinstance(node, CoreAttribute):
            mapper = { 0 : node.core,
                       1 : node.att,
                       2 : node.value
                       }
            return mapper[col]

        else:
            raise RuntimeError("unknown node type")



    def GetAttr(self, item, col, attr):
        ##self.log.write('GetAttr')
        node = self.ItemToObject(item)
        if isinstance(node, core):
            attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False


    def SetValue(self, value, item, col):
        # self.log.write("SetValue: %s\n" % value)
        #
        # # We're not allowing edits in column zero (see below) so we just need
        # # to deal with CoreAttribute objects and cols 1 - 5
        #
        # node = self.ItemToObject(item)
        # if isinstance(node, CoreAttribute):
        #     if col == 1:
        #         node.artist = value
        #     elif col == 2:
        #         node.title = value
        #     elif col == 3:
        #         node.id = value
        #     elif col == 4:
        #         node.date = value
        #     elif col == 5:
        #         node.like = value


#----------------------------------------------------------------------

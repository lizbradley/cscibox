"""
datastructures.py

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
"""

import itertools

class StaticBinTree(object):
    def __init__(self, left, key, data, right):
        self.left = left
        self.key = key
        self.data = data
        self.right = right

    def get_range_nodes(self, key, currange=(None, None)):
        #NOTE: this function assumes the keys in the tree are UNIQUE!
        if key == self.key:
            return (self, self)
        elif key < self.key:
            newrange = (currange[0], self)
            #if currange[1]:
            #    print "doing left:", currange[1].key, self.key
            if self.left and (not currange[1] or currange[1].key > self.key):
                return self.left.get_range_nodes(key, newrange)
            else:
                return newrange
        else:
            #key > self.key
            newrange = (self, currange[1])
            #if currange[0]:
            #    print "doing right:", currange[0].key, self.key
            if self.right and (not currange[0] or currange[0].key < self.key):
                return self.right.get_range_nodes(key, newrange)
            else:
                return newrange


def collection_to_bintree(coll, keyname):
    """
    Takes a dictionary of dictionaries and the name of a sub-dictionary entry
    that is sortable (typically numeric, but feel free to
    use strings if that's somehow useful) and returns a static (cannot be
    modified) balanced binary tree containing lists of the input sub-dictionaries
    and sorted by the values under the passed key name. The
    advantage to this binary tree is that you can get a range of data instead
    of just a single value cheaply (which is quite inconvenient from the
    original dictionary). Note that the dictionary's original keys are discarded.
    """
    #assumes the milieu of interest is keyless
    vals = coll.values()
    vals.sort(key=lambda x: x[keyname])
    #force realization of iterators or they don't work properly, thannnnnks
    #itertools
    keyset = [(it[0], list(it[1])) for it in
              itertools.groupby(vals, key=lambda x: x[keyname])]

    def make_tree(keyset):
        #take a sorted list of keys and turn it into a sub-tree
        if not keyset:
            return None
        keylen = len(keyset)
        mid = len(keyset) / 2 # int rounding makes our tree slightly biased, oh well.
        return StaticBinTree(make_tree(keyset[:mid]), keyset[mid][0],
                             list(keyset[mid][1]), make_tree(keyset[mid+1:]))

    return make_tree(keyset)

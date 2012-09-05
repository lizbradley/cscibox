#!/usr/bin/env python
#
# Copyright (C) 2006 W. Evan Sheehan
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from optparse import OptionParser
from xml.dom import minidom, Node

options = OptionParser('%prog <input XML> <output XML>')
opts, args = options.parse_args()

oldDom = minidom.parse(args[0])
oldDom.normalize()
newDom = minidom.getDOMImplementation().createDocument(None, 'samples', None)

for sample in oldDom.getElementsByTagName('sample'):
    newSample = newDom.createElement('sample')
    newDom.documentElement.appendChild(newSample)
    for attr in sample.getElementsByTagName('att'):
        data = newDom.createElement('data')
        for child in attr.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                continue
            if child.tagName == 'val':
                data.appendChild(newDom.createTextNode(child.firstChild.data))
            elif child.tagName != 'type' and child.hasChildNodes():
                data.setAttribute(child.tagName, child.firstChild.data)
        if data.getAttribute('name') == 'name':
            newSample.setAttribute('name', data.firstChild.data)
        else:
            newSample.appendChild(data)

f = file(args[1], 'w')
newDom.writexml(f, addindent='\t', newl='\n')
f.close()

# vim: ts=4:sw=4:et

#!/usr/bin/env python

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

from csv import DictWriter
from optparse import OptionParser
from xml.dom.minidom import parse

options = OptionParser('%prog <input file> <output file>')

opts, args = options.parse_args()

if len(args) != 2:
    options.error('input and output file required')

dom = parse(args[0])
samples = []
cols = set(['name'])
for sample in dom.getElementsByTagName('sample'):
    s = {'name': str(sample.getAttribute('name'))}
    for data in sample.getElementsByTagName('data'):
        data.normalize()
        try:
            s[data.getAttribute('name')] = float(data.firstChild.data.strip())
        except (NameError, ValueError, SyntaxError):
            s[data.getAttribute('name')] = data.firstChild.data.strip()
        cols.add(data.getAttribute('name'))
    samples.append(s)

csv = file(args[1], 'w')
csv.write(','.join(['"%s"' % c for c in cols]) + '\n')
writer = DictWriter(csv, fieldnames=cols)
writer.writerows(samples)

# vim: ts=4:sw=4:et

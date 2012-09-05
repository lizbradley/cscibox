#!/usr/bin/env python

"""create_release.py will create a release version of the Age Calculation
Environment, aka ACE. It is a simple script that produces a folder of the
form ACE-MM-DD-YYYY containing three subdirectories---src, imports, and
repo---that include, respectively, the latest version of the ACE source code,
a set of .csv files that can be imported into ACE, and a default ACE repository.

The input to create_release.py is the path to a folder that already contains
these directories (i.e. the development version of ACE) and it copies across
the information that it needs to the destination folder that will live in the
same directory as the input folder.

create_release.py only copies source files and data files and leaves out files
that might otherwise accumluate in a directory used for development, such as
.pyc files, .DS_Store files, and the like."""

import os
import os.path
import sys
import time

from shutil import copytree

if len(sys.argv) != 2:
    print "Usage: create_release.py <ACE-DEVELOPMENT-DIRECTORY>"
    print "Error: wrong number of arguments."
    sys.exit(1)

dev_dir = sys.argv[1]
dev_dir = os.path.abspath(dev_dir)

if not os.path.exists(dev_dir):
    print "Usage: create_release.py <ACE-DEVELOPMENT-DIRECTORY>"
    print "Error: <%s> does not exist." % (dev_dir)
    sys.exit(1)

if not os.path.isdir(dev_dir):
    print "Usage: create_release.py <ACE-DEVELOPMENT-DIRECTORY>"
    print "Error: <%s> is not a directory." % (dev_dir)
    sys.exit(1)

src_path = os.path.join(dev_dir, "src")
rep_path = os.path.join(dev_dir, "repo")

src_cmp  = os.path.exists(src_path)
rep_cmp  = os.path.exists(rep_path)

if not (src_cmp and rep_cmp):
    print "Usage: create_release.py <ACE-DEVELOPMENT-DIRECTORY>"
    print "Error: <%s> is not an ACE Development Directory." % (dev_dir)
    sys.exit(1)

current_day = time.strftime("%m-%d-%Y", time.localtime())

dest_dir = os.path.dirname(dev_dir)
dest_dir = os.path.join(dest_dir, "ACE-%s" % (current_day))

if os.path.exists(dest_dir):
    print "Usage: create_release.py <ACE-DEVELOPMENT-DIRECTORY>"
    print "Error: <%s> already exists." % (dest_dir)
    sys.exit(1)

dest_src_path = os.path.join(dest_dir, "src")
dest_rep_path = os.path.join(dest_dir, "repo")

os.mkdir(dest_dir)

copytree(src_path, dest_src_path)
copytree(rep_path, dest_rep_path)

# remove .DS_Store files and .pyc files
# also remove .svn directories
for root, dirs, files in os.walk(dest_dir, topdown=False):
    for name in files:
        data_file = os.path.join(root, name)
        if ".svn" in data_file:
            os.remove(data_file)
        if data_file.endswith(".DS_Store"):
            os.remove(data_file)
        if data_file.endswith(".pyc"):
            os.remove(data_file)
    for name in dirs:
        data_dir = os.path.join(root, name)
        if ".svn" in data_dir:
            os.rmdir(data_dir)

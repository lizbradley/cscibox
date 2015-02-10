#!/usr/bin/env python

import os
import sys
import time
from os.path import expanduser
import subprocess

print "RESTORING THE BACKUP DATABASE..."
subprocess.call(['mongorestore', '--drop', '../database_dump/dump'], shell=False)
print "DONE!"

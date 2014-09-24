CScience
======

CScience is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

In development, this project depends on the following packages:

Python 2.7

wxPython -- currently tested against version 3.0.0.0 (available at http://www.wxpython.org/download.php)

numpy

scipy

matplotlib

happybase
pymongo
  ** coming (very) soon: you only need the one of these that you are actually using for your own database needs!

quantities (available at https://pypi.python.org/pypi/quantities)

Note that you will also need access to a running hbase or mongodb server.

================================================
One-Step Installer
================================================

As an alternative to running the source code directly, there is an installer (OSX and Windows) available here:

OSX (64 bit): https://github.com/ldevesine/Calvin/releases/tag/0.9
Windows (32 bit): https://github.com/ldevesine/Calvin/releases/tag/0.9_win

The only requirement for Mac is to be running OSX 10.6 (Snow Leopard) or greater. You do not need to install python or any packages when using the packaged release.

Windows executable is 32-bits, and can be run as a stand-alone executable, no installation is necessary.

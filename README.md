CScience
======

CScience is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

In development, this project depends on the following packages.  Installing them in this order
will likely reduce your unhappiness:

Python 2.7

wxPython -- currently tested against version 3.0.0.0 (available at http://www.wxpython.org/download.php)

numpy

scipy

matplotlib

pymongo 2.8 (install using: `pip install pymongo==2.8`)

quantities (available at https://pypi.python.org/pypi/quantities)

Note that you will also need access to a running mongodb server.
After you have started up your local mongodb server, you should populate it with initial data by 
using the mongorestore command (see http://docs.mongodb.org/manual/reference/program/mongorestore/ ) 
and the data stored in this repository at database_dump/dump/repository. This will give you a set 
of initial (public) data to work from.

CSciBox contains a number of code modules that were written by others:

- Bacon http://chrono.qub.ac.uk/blaauw/bacon.html

If you want to use Bacon, you need the compiled version.  You may need
to run the appropriate makefile in the src/plugins/bacon directory of
this distribution to produce that file.  This will create a directory 
in src/plugins/bacon called pluginfiles.  Move the contents of that directory
to src/cscience/components/cfiles.

- StratiCounter https://github.com/maiwinstrup/StratiCounter

If you want to use StratiCounter, you'll need to download the Matlab
2014b runtime http://www.mathworks.com/products/compiler/mcr/

Although the installation instructions above focus on using a local mongodb server for data storage, 
it is possible to use CScience with a remote mongodb installation or with hbase. To use a remote 
mongodb server, edit the db_location and db_port variables in the src/config.py file to point to 
your remote database. To run against an hbase server, you will also need to install the happybase 
python package and change the db_type variable to 'hbase'.


================================================
One-Step Installer
================================================

As an alternative to running the source code directly, there is an installer (OSX and Windows) available here:

https://github.com/ldevesine/Calvin/releases

Currently CSciBox has been tested on OSX 10.9 (Mavericks) and there is a separete release for OSX 10.7 and 10.8 (Lion and Mountain Lion)

Please send your email address to lizb@colorado.edu so that we can keep you informed of future updates and get any feedback you may have.

The only requirement for Mac is to be running OSX 10.6 (Snow Leopard) or greater. You do not need to install python or any packages when using the packaged release.

Windows executable is 32-bits, and can be run as a stand-alone executable, no installation is necessary.

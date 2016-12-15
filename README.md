# CSciBox
CSciBox is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

The project webpage is here:  [**CSciBox Webpage**](http://www.cs.colorado.edu/~lizb/cscience.html), and includes more detailed information about the project and a simple tutorial.

There are two options for those who want to use the software.


Before running cscibox you need to start a MongoDB sever. To start a server on the terminal use:

    sudo mongod

If this is your first time running CSciBox you will also need to load our database:


    mongorestore /usr/local/lib/python2.7/site-packages/CSciBox-0.11.1-py2.7.egg/database_dump


## Dependencies
In development, this project depends on the following packages.  Installing them in this order
will likely reduce your unhappiness:

1. [Python 2.7](https://www.python.org/downloads/)

2. [wxPython](http://www.wxpython.org/download.php) -- currently tested against version 3.0.0.0, Used for the GUI

3. [scipy/numpy/matplotlib](http://www.scipy.org/install.html) -- follow link for instructions on installation, Used for calculations and plotting. 1.4.x is required; although it will work with some older versions, not all features will work with older versions.

4. [pymongo 2.8](http://api.mongodb.org/python/current/installation.html) (install using: `pip install pymongo==2.8`) -- Database for storage of all data

5. [quantities](https://pypi.python.org/pypi/quantities) -- Used for handling engineering units

6. [bagit](http://libraryofcongress.github.io/bagit-python/) -- Used for exporting data

There is a Windows installer (OSX and Windows) available here: [**CSciBox Releases**](https://github.com/ldevesine/Calvin/releases) (slightly out of date).

Currently CSciBox has been tested on OSX 10.11 (El Capitan).  

Please send your email address to lizb@colorado.edu so that we can keep you informed of future updates and get any feedback you may have.

Windows executable is 32-bits, and can be run as a stand-alone executable, no installation is necessary.

Note that you will also need access to a running mongodb server.
After you have started up your local mongodb server, you should populate it with initial data by
using the mongorestore command (see [mongodb manual -- mongorestorre]( http://docs.mongodb.org/manual/reference/program/mongorestore/))
and the data stored in this repository at `database_dump/dump/repository`. This will give you a set
of initial (public) data to work from.

CSciBox contains a number of code modules that were written by others:

- Bacon http://chrono.qub.ac.uk/blaauw/bacon.html

If you want to use Bacon, you need the compiled version.  You may need
to run the appropriate makefile in the `src/plugins/bacon` directory of
this distribution to produce that file.  This will create a directory
in `src/plugins/bacon` called pluginfiles.  Move the contents of that directory
to `src/cscience/components/cfiles`.

- StratiCounter https://github.com/maiwinstrup/StratiCounter

If you want to use StratiCounter, you'll need to download the Matlab
2014b runtime available [here](http://www.mathworks.com/products/compiler/mcr/)

Although the installation instructions above focus on using a local mongodb server for data storage,
it is possible to use CScience with a remote mongodb installation or with hbase. To use a remote
mongodb server, edit the `db_location` and `db_port` variables in the `src/config.py` file to point to
your remote database. To run against an hbase server, you will also need to install the happybase
python package and change the `db_type` variable to `hbase`.

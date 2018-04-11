# CSciBox
CSciBox is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

The project webpage is here:  [**CSciBox Webpage**](http://www.cs.colorado.edu/~lizb/cscience.html), and includes more detailed information about the project and a simple tutorial.

To use CSciBox, you need to download it and install it using the
procedure below.  Then open a terminal window, start up a database
server, and finally type the command that starts the code.

Please send your email address to lizb@colorado.edu so that we can
keep you informed of future updates and get any feedback you may have.

## Downloading and installing the code

There are two ways to install CSciBox: grabbing the source code from
github, which involves downloading some supporting software packages,
or using a "one-stop shop" version that is available on the Docker
hub.  If you are running on a Mac or Linux machine, we recommend the
github route; if you're on a PC, or if you run into trouble with the
github route, we recommend Docker.

Here is the procedure for getting up and running from the github
repository:

First, download and install the software packages on which CSciBox
relies.  Installing them in the following order will likely reduce
your unhappiness:

1. [Python 2.7](https://www.python.org/downloads/) -- this is the
language in which CSciBox is implemented.

2. [wxPython](http://www.wxpython.org/download.php) -- used for the
GUI; currently tested against version 3.0.0.0.

3. [scipy/numpy/matplotlib](http://www.scipy.org/install.html) -- used
for calculations and plotting. 1.4.x is required; not all CSciBox
features will work with older versions.  Follow link above for
instructions on installation.

4. [pymongo
2.8](http://api.mongodb.org/python/current/installation.html) -- the
database for storage of all data.  Install using: `pip install
pymongo==2.8`

5. [quantities](https://pypi.python.org/pypi/quantities) -- used for
handling engineering units

6. [bagit](http://libraryofcongress.github.io/bagit-python/) -- used
for exporting data

## Database

Before running cscibox you need to start a database ("MongoDB")
server.   To do this, open a terminal window and type:

    mongod --dbpath="./"

If that doesn't work, you may need to be more insistent:

    sudo mongod --dbpath="./"

The database runs in the background, so it will occupy that terminal
window until you terminate it using ctrl-c.

When you start up your local mongodb server for the first time, you
should populate it with initial data by opening up another terminal
window, navigating to the cscibox directory, and typing

    mongorestore

(see [mongodb manual -- mongorestorre](
http://docs.mongodb.org/manual/reference/program/mongorestore/)) and
the data stored in this repository at
`database_dump/dump/repository`. This will give you a set of initial
(public) data to work from.

CSciBox contains a number of code modules that were written by others:

- Bacon http://chrono.qub.ac.uk/blaauw/bacon.html

If you want to use Bacon, you need the compiled version.  You may need
to run the appropriate makefile in the `src/plugins/bacon` directory of
this distribution to produce that file.  

    cd src/plugins/bacon/cpp/
    make -f makefileLinux sciboxplugin

- StratiCounter https://github.com/maiwinstrup/StratiCounter

If you want to use StratiCounter, you'll need to download the Matlab
2014b runtime available [here](http://www.mathworks.com/products/compiler/mcr/)

Although the installation instructions above focus on using a local mongodb server for data storage,
it is possible to use CScience with a remote mongodb installation or with hbase. To use a remote
mongodb server, edit the `db_location` and `db_port` variables in the `src/config.py` file to point to
your remote database. To run against an hbase server, you will also need to install the happybase
python package and change the `db_type` variable to `hbase`.

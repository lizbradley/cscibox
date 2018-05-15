# CSciBox
CSciBox is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

The project webpage is here:  [**CSciBox Webpage**](http://www.cs.colorado.edu/~lizb/cscience.html), and includes more detailed information about the project and a simple tutorial.

To use CSciBox, you need to download it and install it using the
procedure below.  Then open a terminal window and finally type the
command that starts the code.

Please send your email address to lizb@colorado.edu so that we can
keep you informed of future updates and get any feedback you may have.

## Downloading and installing the code

There are two ways to install CSciBox: grabbing the source code from
github, which involves downloading some supporting software packages,
or using a "one-stop shop" version that is available on the Docker
hub.  If you are running on a Mac or Linux machine, we recommend the
github route; if you're on a PC, or if you run into trouble with the
github route, we recommend Docker.

### From github:

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

7. Please download the zip file of the project by
[clicking here](https://github.com/lizbradley/cscibox/archive/master.zip).
Please make sure to unzip the file into a folder.

8. **Bacon is NOT required** for the basic functionalities
of CSciBox. This software plugin is only supported in MacOS and Linux.
If you want to use BACON
(http://chrono.qub.ac.uk/blaauw/bacon.html) through CSciBox, you need
the compiled version of the BACON code.  You may need to run the
appropriate makefile in the `src/plugins/bacon/cpp` directory of this
distribution to produce that file (please note that the installation
of the library gsl may be required).
	```shell
    cd src/plugins/bacon/cpp/
    make -f makefileLinux sciboxplugin
	```
  If the installation of bacon on Windows is absolutely necessary,
a tarball for cross-compiling BACON from Linux to Windows using minGW 
is provided at [this link](http://www.cs.colorado.edu/~lizb/cscience/crossbacon.tgz).
(If you don't know what that means, don't worry about it.)

The last step before running CSciBox is to start a database
("MongoDB") server.  To do this, open a terminal window and type:

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

### From docker:

Docker is a "container" system that wraps up all of the resources
necessary to run CSciBox.  Here is how you download the CSciBox
"image" - what Docker calls an instantiation:

- if you're on Linux:

```
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name cscibox lizbradley/cscibox
```
- if you're on MacOS:

Please follow this link to get your X-server set up: https://fredrikaverpil.github.io/2016/07/31/docker-for-mac-and-gui-applications/
```
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}') xhost + $ip
docker run -d --name cscibox -e DISPLAY=$ip:0 -v /tmp/.X11-unix:/tmp/.X11-unix lizbradley/cscibox
```
- if you're on Windows:

Windows is a bit more difficult.  Please follow the steps found at this link,
replacing the repository shown in the website example with this one:
https://manomarks.github.io/2015/12/03/docker-gui-windows.html

After the Docker download is complete, open a terminal window and type
```docker start cscibox```
x
## Running CSciBox:

Please go to [**CSciBox
Webpage**](http://www.cs.colorado.edu/~lizb/cscience.html) for
instructions and video tutorials.

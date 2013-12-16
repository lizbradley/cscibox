CScience
======

CScience is a project to aid geologists and other scientists working with ice and sediment cores in collating, manipulating, and interpreting data derived from those cores.

In development, this project depends on the following packages:

Python 2.7

wxPython -- version 2.9.5 or higher

numpy

scipy

matplotlib

happybase

quantities (available at https://pypi.python.org/pypi/quantities)

Temporarily, you will need a locally running instance of HBase (http://hbase.apache.org/) on its default port with the Thrift listener process running. These can be started from the command line with the commands "start-hbase.sh" and "hbase thrift -b 127.0.0.1 start"
If you have an older version of CScience and would like to convert your old data to the new storage format, you can run python dbconversion.py <path to your current repository> to save all your data. Then open CScience normally.


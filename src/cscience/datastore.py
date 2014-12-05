"""
datastore.py

* Copyright (c) 2012-2015, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This module holds and manages instances of the objects used to access
data storage for CScience.
"""

import os
import sys
import time
from os.path import expanduser
import logging

import importlib
import subprocess
import atexit


from cscience import framework
import cscience.components
import cscience.backends
import config

class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance


class Datastore(object):
    # Set this class as a singleton, this is an alternate solution to placing the Datastore() object in the sys.modules dictionary
    __metaclass__ = SingletonType

    data_modified = False
    data_source = ''

    models = {'sample_attributes':framework.Attributes,
              'cores':framework.Cores,
              'templates':framework.Templates,
              'milieus':framework.Milieus,
              #'selectors':framework.Selectors,
              'workflows':framework.Workflows,
              'computation_plans':framework.ComputationPlans,
              'filters':framework.Filters,
              'views':framework.Views}

    component_library = cscience.components.library

    def __init__(self):
        #load up the component library, which doesn't depend on the data source.
        path = os.path.dirname(cscience.components.__file__)

        for filename in os.listdir(path):
            if not filename.endswith('.py'):
                continue
            module = 'cscience.components.%s' % filename[:-len('.py')]
            try:
                importlib.import_module(module)
            except:
                print "problem importing module", module
                print sys.exc_info()
                import traceback
                print traceback.format_exc()

    def load_from_config(self):
        backend_name = config.db_type
        backend_loc = config.db_location
        backend_port = config.db_port

        if getattr(sys, 'frozen', False):
            # we are running in a |PyInstaller| bundle
            backend_port = config.installer_db_port
            backend_name = config.installer_db_type
            backend_loc = config.installer_db_location


        self.set_data_source(backend_name, backend_loc, backend_port)

    def set_data_source(self, backend_name, source, port):
        """
        Set the source for repository data and do any appropriate initialization.
        """

        backend = importlib.import_module('cscience.backends.%s' % backend_name)
        self.data_source = source
        self.database = backend.Database(source, port)

        for model_name, model_class in self.models.iteritems():
            setattr(self, model_name, model_class.load(self.database))
        self.data_modified = False

    def save_datastore(self):
        for model_name in self.models:
            getattr(self, model_name).save()
        self.data_modified = False

    class RepositoryException(Exception): pass

    def kill_database(self):
        db_port = config.installer_db_port
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
        executable_path = os.path.join(sys._MEIPASS, "database", "cscience_mongo")
        subprocess.Popen([executable_path, "localhost:{}".format(str(db_port)), "--eval", "db.getSiblingDB('admin').shutdownServer()"], **kwargs)


    def setup_database(self):

        self._logger = logging.getLogger()
        self._logger.debug("Setting up the database...")
        is_windows = sys.platform.startswith('win')
        db_port = config.installer_db_port

        # Check if the database folder has been created
        database_dir = os.path.join(expanduser("~"), 'cscibox', 'data')
        new_database = False
        if not (os.path.exists(database_dir) or os.path.isdir(database_dir)):
            self._logger.debug("'data' diretory does not exist, creating...")
            # Need to create the database files
            try:
                os.makedirs(database_dir)
                new_database = True
            except Exception as e:
                raise Exception("Error creating database directory({0}: {1}".format(database_dir, e.message))

        if os.path.isdir(database_dir):

            self._logger.debug("attempting to start mongodb...")

            # Start mongod and restore the database
            executable_path = os.path.join(sys._MEIPASS, "database", "cscience_mongod")
            mongo_process = -1
            try:
                kwargs = {}
                if subprocess.mswindows:
                    su = subprocess.STARTUPINFO()
                    su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    su.wShowWindow = subprocess.SW_HIDE
                    kwargs['startupinfo'] = su
                mongo_parameters = []
                if is_windows:
                    mongo_parameters = [executable_path, "--dbpath", database_dir, "--port", str(db_port)]
                else:
                    mongo_parameters = [executable_path, "--fork", "--logpath", os.path.join(database_dir, "mongo.db"), "--dbpath", database_dir, "--port", str(db_port)]

                mongo_process = subprocess.Popen(mongo_parameters, **kwargs)
                if not is_windows:
                    mongo_process.wait()
            except Exception as e:
                raise Exception("Error starting mongodb: {0}".format(e.message))

            atexit.register(self.kill_database)
            if not is_windows:
                if mongo_process.returncode == 0:
                    self._logger.debug("mongodb started on port {}...".format(str(db_port)))
                else:
                    self._logger.debug("mongodb failed to start on port {}...".format(str(db_port)))


        if new_database:
            self._logger.debug("this is a new installation, attempting to restore the database...")
            # Restore the database
            executable_path = os.path.join(sys._MEIPASS, "database", "cscience_mongorestore")
            data_files_path = os.path.join(sys._MEIPASS, "database_dump", "dump")

            self._logger.debug("executing {} {} {} {}...".format(executable_path, "-h", "localhost:{}".format(str(db_port)), data_files_path))

            subprocess.Popen([executable_path, "-h", "localhost:{}".format(str(db_port)), data_files_path]).wait()

            self._logger.debug("database restored successfully, starting the application now.")


#sys.modules[__name__] = Datastore()


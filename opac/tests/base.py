# coding:utf-8
import os
import time
import atexit
import shutil
import tempfile
import unittest
import subprocess

import pymongo
from opac_schema.v1 import models as schema_models
from flask import current_app
from flask.ext.testing import TestCase
from webapp import dbsql


class MongoInstance(object):
    """Singleton to manage a temporary MongoDB instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    http://blogs.skicelab.com/maurizio/python-unit-testing-and-mongodb.html

    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):

        self._tmpdir = tempfile.mkdtemp()
        self.mongo_settings = current_app.config['MONGODB_SETTINGS']
        self._process = subprocess.Popen(['mongod', '--bind_ip', 'localhost',
                                          '--port', str(self.mongo_settings['port']),
                                          '--dbpath', self._tmpdir,
                                          '--nojournal', '--nohttpinterface',
                                          '--noauth', '--smallfiles',
                                          '--syncdelay', '0',
                                          '--maxConns', '10',
                                          '--nssize', '1', ],
                                         stdout=open(os.devnull, 'wb'),
                                         stderr=subprocess.STDOUT)

        # XXX: wait for the instance to be ready
        #      Mongo is ready in a glance, we just wait to be able to open a
        #      Connection.
        for i in range(3):
            time.sleep(0.1)
            try:
                self._conn = pymongo.MongoClient('localhost', self.mongo_settings['port'])
            except pymongo.errors.ConnectionFailure:
                continue
            else:
                break
        else:
            self.shutdown()
            assert False, 'Cannot connect to the mongodb test instance'

    @property
    def conn(self):
        return self._conn

    @property
    def db(self):
        return self._conn[self.mongo_settings['db']]

    def shutdown(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
            shutil.rmtree(self._tmpdir, ignore_errors=True)


class BaseTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.instance = MongoInstance.get_instance()
        self.conn = self.instance.conn
        self.db = self.instance.db

    def create_app(self):
        return current_app

    def setUp(self):
        dbsql.create_all()
        super(TestCase, self).setUp()

    def tearDown(self):
        dbsql.session.remove()
        dbsql.drop_all()
        mongo_db_name = current_app.config['MONGODB_SETTINGS']['db']
        self.conn.drop_database(mongo_db_name)

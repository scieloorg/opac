#!/usr/bin/env python
import os
from app import create_app
from app.models import build_sample_db
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('OPAC_CONFIG'))
manager = Manager(app)


@manager.command
def build_db():
    if not os.path.exists(app.config['DATABASE_PATH']):
        build_sample_db()
        print 'done!'
    else:
        print 'database already exist'

if __name__ == '__main__':
    manager.run()

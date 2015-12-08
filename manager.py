#!/usr/bin/env python
import os
from app import create_app, dbsql, dbmongo, mail
from opac_schema.v1.models import Journal, Issue, Article
from app.models import build_sample_db
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('OPAC_CONFIG'))
manager = Manager(app)


def make_shell_context():
    return dict(app=app, dbsql=dbsql, dbmongo=dbmongo, mail=mail, Journal=Journal, Issue=Issue, Article=Article)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def build_db():
    if not os.path.exists(app.config['DATABASE_PATH']):
        build_sample_db()
        print 'done!'
    else:
        print 'database already exist'

if __name__ == '__main__':
    manager.run()

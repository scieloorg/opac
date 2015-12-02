# Default configuration

DEBUG = False
MAIL_FROM_EMAIL = "default@scielo.org"

# Secret
SECRET_KEY = '02ee54614563e5946b1497b0ba07c24a'

# Assets
ASSETS_DEBUG = False

# Mongo
MONGODB_SETTINGS = {
    'db': 'opac',
    # 'host': '127.0.0.1',
    # 'port': 27017
}

# SQL Alchemy
DATABASE_FILE = 'opac_admin.sqlite'
DATABASE_DIR = '/tmp'  # Absoulte path
DATABASE_PATH = '%s/%s' % (DATABASE_DIR, DATABASE_FILE)
SQLALCHEMY_DATABASE_URI = 'sqlite:////%s' % DATABASE_PATH
SQLALCHEMY_ECHO = DEBUG

# OPAC Collection
OPAC_COLLECTION = ''

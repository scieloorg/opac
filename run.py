#!flask/bin/python
from app import app


# Load the development configuration
app.config.from_pyfile('../config/default.py')
# app.config.from_pyfile('../config/development.py')

# Load the configuration from the instance folder
# app.config.from_pyfile('config.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
# app.config.from_envvar('APP_CONFIG_FILE')
# ... then from shell:
# APP_CONFIG_FILE=/var/www/yourapp/config/production.py
# python run.py

app.run()

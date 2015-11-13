from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static')

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'scielo'

toolbar = DebugToolbarExtension(app)

from app import views

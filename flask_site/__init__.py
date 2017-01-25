import os

from flask import Flask

from flask_socketio import SocketIO

from flask_site.helpers.config import read_config
from flask_site.helpers.env import read_env

# THE CONFIGURATION
CONFIG_FOLDER = os.path.abspath('flask_site/config')
MAIN_CONFIG_FILENAME = os.path.join(CONFIG_FOLDER, 'config.yml')
env = read_env()

config = read_config(MAIN_CONFIG_FILENAME, env)
flask_config = config.get('flask', {})

# THE FLASK INSTANCE
app = Flask(flask_config['name'])
app.config.update(flask_config)

# WEBSOCKETS SETUP
sock = SocketIO(app, async_mode=None)  # async_mode=threading, eventlet, gevent, or None to let application pick

# LOAD THE ROUTES
from flask_site.controllers import *

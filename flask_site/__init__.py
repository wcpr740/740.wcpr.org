import os
from datetime import datetime

from flask import Flask

from flask_socketio import SocketIO

from env_load.config import read_config
from env_load.env import read_env

# THE CONFIGURATION
CONFIG_FOLDER = os.path.abspath('flask_site/config')
MAIN_CONFIG_FILENAME = os.path.join(CONFIG_FOLDER, 'config.yml')
env = read_env()

config = read_config(MAIN_CONFIG_FILENAME, env)
config['start_time'] = datetime.now()
flask_config = config.get('flask', {})
DEBUG = flask_config.get('DEBUG', False)

# THE FLASK INSTANCE
app = Flask(flask_config['name'])
app.config.update(flask_config)

# WEBSOCKETS SETUP
sock = SocketIO(app, async_mode=None, logger=DEBUG)

# LOAD THE ROUTES
from flask_site.controllers import *

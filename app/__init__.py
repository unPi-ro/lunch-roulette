from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config
from redis import Redis
from datetime import timedelta
import rq

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Please log in to access this service.'
login.login_message_category = 'info'
app.permanent_session_lifetime = timedelta(minutes=app.config['SESSION_LIFETIME_MINUTES'])
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('roulette-tasks', connection=app.redis)

from app import routes, models, errors

import logging
from logging.handlers import RotatingFileHandler
import os

def cleanup(): pass

def startup():
    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'): os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/roulette.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Lunch Roulette startup')


startup()
cleanup()

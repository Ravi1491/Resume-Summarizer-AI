import os
from flask import Flask
from flask_session import Session
from config import DevelopmentConfig, ProductionConfig

from .models import init_db
from .routes.index import app as app_blueprint
from .routes.auth import auth as auth_blueprint
from .routes.dashboard import dashboard as dashboard_blueprint

def create_app():
    app = Flask(__name__)

    if os.getenv('CONFIG_MODE') == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

    app.secret_key = app.config['SECRET_KEY']

    Session(app)

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.register_blueprint(app_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)

    init_db()
    
    return app

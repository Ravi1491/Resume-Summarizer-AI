import os
from flask import Flask
from flask_session import Session
from config import DevelopmentConfig, ProductionConfig
from flask_migrate import Migrate, upgrade

from database import db
from .routes.index import app as app_blueprint
from .routes.auth import auth as auth_blueprint
from .routes.resume import resume as resume_blueprint
import database.models  

def create_app():
    app = Flask(__name__)

    if os.getenv('CONFIG_MODE') == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    migrate = Migrate(app, db, directory='database/migrations')
    with app.app_context():
        upgrade()

    Session(app)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.register_blueprint(app_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(resume_blueprint)
    
    return app

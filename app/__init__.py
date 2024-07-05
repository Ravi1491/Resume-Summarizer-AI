from flask import Flask
from flask_session import Session
from config import DevelopmentConfig, ProductionConfig
import os

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

    from .routes import app as routes_blueprint
    app.register_blueprint(routes_blueprint)

    from .models import init_db
    init_db()

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    #app = Flask(__name__)
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register the blueprint
    # from app.routes import bp as api_bp  # Import here to avoid circular import
    # app.register_blueprint(api_bp, url_prefix='/api')


    return app

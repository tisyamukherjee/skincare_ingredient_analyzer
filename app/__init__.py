from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object globally
db = SQLAlchemy()

def create_app():
    # Create the Flask app instance
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes import bp  # Import blueprint after app creation to avoid circular imports
    app.register_blueprint(bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

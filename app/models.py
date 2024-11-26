# Define your SQLAlchemy database models.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ScrapedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(500), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

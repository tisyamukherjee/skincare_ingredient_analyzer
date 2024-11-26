# Define your application routes (e.g., API endpoints).
from flask import Blueprint, jsonify
from .scrapers.cerave import scrape_website
from .models import ScrapedData

bp = Blueprint('main', __name__)

@bp.route('/scrape', methods=['GET'])
def scrape():
    scrape_website('https://example.com')
    return jsonify({'message': 'Scraping completed'})

@bp.route('/data', methods=['GET'])
def get_data():
    data = ScrapedData.query.all()
    return jsonify([{
        'id': d.id, 'title': d.title, 'price': d.price, 'url': d.url
    } for d in data])

from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import ScrapedData

bp = Blueprint('api', __name__)

def calculate_similarity(ingredients_1, ingredients_2):
    set_1 = set(ingredients_1.split(','))
    set_2 = set(ingredients_2.split(','))
    intersection = set_1.intersection(set_2)
    return len(intersection) / max(len(set_1), len(set_2)) if set_1 and set_2 else 0

@bp.route('/find_similar', methods=['POST'])
def find_similar():
    print("Request received")
    data = request.json
    user_ingredients = data.get('ingredients')
    print("Received ingredients:", user_ingredients)
    user_name = data.get('name')

    if not user_ingredients and not user_name:
        return jsonify({"error": "Provide either 'ingredients' or 'name' in the request"}), 400

    if user_name:
        product = ScrapedData.query.filter(ScrapedData.name.ilike(f"%{user_name}%")).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404
        user_ingredients = product.ingredients

    if not user_ingredients:
        return jsonify({"error": "No ingredients found for the given input"}), 400

    ingredients_set = set(user_ingredients.split(','))
    filtered_products = ScrapedData.query.filter(
        or_(
            ScrapedData.ingredients.ilike(f"%{ingredient.strip()}%")
            for ingredient in ingredients_set
        )
    ).all()

    similar_products = []
    for product in filtered_products:
        similarity_score = calculate_similarity(user_ingredients, product.ingredients)
        if similarity_score > 0.1:  # Adjust the threshold
            similar_products.append({
                "name": product.name,
                "brand": product.brand,
                "link": product.link,
                "ingredients": product.ingredients,
                "similarity_score": similarity_score
            })

    similar_products = sorted(similar_products, key=lambda x: x['similarity_score'], reverse=True)
    return jsonify(similar_products)

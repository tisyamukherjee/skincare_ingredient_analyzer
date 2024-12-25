from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import ScrapedData
import json

bp = Blueprint('api', __name__)

def calculate_similarity(ingredients_1, ingredients_2):
    """
    Calculate similarity between two ingredient lists.
    Considers both ingredient presence (partial match) and order (LCS).
    
    Args:
        ingredients_1 (str): Ingredient list for product 1 (comma-separated).
        ingredients_2 (str): Ingredient list for product 2 (comma-separated).
        
    Returns:
        float: Similarity score (0 to 1).
    """
    # Convert ingredients to lists (split by commas and strip spaces)
    list_1 = [ingredient.strip().upper() for ingredient in ingredients_1.split(',')]
    list_2 = [ingredient.strip().upper() for ingredient in ingredients_2.split(',')]

    # Step 1: Calculate set intersection (ingredient matching)
    set_1 = set(list_1)
    set_2 = set(list_2)

    # Count how many ingredients from list_1 are in list_2
    common_ingredients_count = len(set_1.intersection(set_2))

    # Step 2: Calculate longest common subsequence (LCS) for order matching
    def lcs(a, b):
        """ Helper function to calculate the Longest Common Subsequence (LCS) length. """
        m = len(a)
        n = len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m):
            for j in range(n):
                if a[i] == b[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
        return dp[m][n]

    # Calculate the LCS (Longest Common Subsequence)
    lcs_length = lcs(list_1, list_2)

    # Step 3: Calculate similarity based on ingredient presence and order matching
    # The proportion of ingredients from list_1 that are in list_2
    presence_similarity_score = common_ingredients_count / len(list_1) if len(list_1) > 0 else 0

    # Order-based similarity score (LCS similarity)
    order_similarity_score = lcs_length / len(list_1) if len(list_1) > 0 else 0

    # Combine both scores
    # We give equal weight to both ingredient presence and order similarity
    similarity_score = 0.5 * presence_similarity_score + 0.5 * order_similarity_score

    return similarity_score

@bp.route('/find_similar', methods=['POST'])

def find_similar():
    data = request.json
    user_ingredients = data.get('ingredients')
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
    
    # Ensure user ingredients are in the correct format
    ingredients_set = user_ingredients.split(',')
    # Strip whitespace and convert each ingredient to uppercase
    ingredients_set = {ingredient.strip().upper() for ingredient in ingredients_set}

    filtered_products = ScrapedData.query.filter(
        or_(
            ScrapedData.ingredients.ilike(f"%{ingredient.strip()}%")
            for ingredient in ingredients_set
        )
    ).all()

    similar_products = []
    for product in filtered_products:
        similarity_score = calculate_similarity(user_ingredients, product.ingredients)
        if similarity_score > 0.5:  # Adjust the threshold
            similar_products.append({
                "name": product.name,
                "brand": product.brand,
                "link": product.link,
                "ingredients": product.ingredients,
                "similarity_score": similarity_score
            })

    similar_products = sorted(similar_products, key=lambda x: x['similarity_score'], reverse=True)
    
    # Save to JSON file
    try:
        with open('similar_products.json', 'w') as json_file:
            json.dump(similar_products, json_file, indent=4)
        print("Successfully saved similar products to 'similar_products.json'.")
    except Exception as e:
        return jsonify({"error": f"Error saving JSON file: {str(e)}"}), 500

    # Return the result as a JSON response
    return jsonify(similar_products)



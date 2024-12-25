from flask import Flask, render_template, request, jsonify
from app.routes import bp as api_blueprint
from app import create_app
import requests

#app = Flask(__name__)
app = create_app()

# Register the API blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def results():
    user_ingredients = request.form.get('ingredients')

    if not user_ingredients:
        return render_template('home.html', error="Please provide ingredients.")
    
    import requests
    response = requests.post("http://127.0.0.1:5000/api/find_similar", json={"ingredients": user_ingredients})

    if response.status_code != 200:
        print(response.text)  # Log the error message
        return render_template('home.html', error="Error fetching similar products.")

    # Parse the API response
    results = response.json()
    return render_template('results.html', ingredients=user_ingredients, results=results)

    # Example data for results.html rendering
    # results = [{"name": "Product 1", "similarity": 0.8}, {"name": "Product 2", "similarity": 0.6}]
    # return render_template('results.html', ingredients=user_ingredients, results=results)


if __name__ == '__main__':
    app.run(debug=True)

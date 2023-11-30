from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os

from recommender import Recommender
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

# Homepage
recommender = Recommender()
@app.route('/')
def home():
    return render_template('home.html')

# Algorithm explanation page
@app.route('/algorithm')
def algorithm():
    return render_template('algorithm.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Recommendation page       
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        recommender.get_movieinfo()
        user_id = request.form.get('user_id')
        return render_template('recommendation.html', movies_info=recommender.movies_info, user_id=user_id)
    else:
        return redirect(url_for('home'))

# Generate user-based recommendation
@app.route('/recommend/user-based', methods=['POST'])
def recommend_user_based():
    input_data = request.json
    recommendations = recommender.recommender_user_based(input_data)
    return jsonify(recommendations)

# Generate item-based recommendation
@app.route('/recommend/item-based', methods=['POST'])
def recommend_item_based():
    input_data = request.json
    recommendations = recommender.recommender_item_based(input_data)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
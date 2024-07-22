from flask import render_template, request, redirect, url_for, jsonify
from app import app, db
from app.models import FoodItem

@app.route('/')
def index():
    return "Hello World!"
    #return render_template('index.html')

@app.route('/add_food', methods=['POST'])
def add_food():
    data = request.get_json()
    name = data.get('name')
    calories = data.get('calories')
    protein = data.get('protein')
    carbohydrates = data.get('carbohydrates')
    fats = data.get('fats')

    if not all([name, calories, protein, carbohydrates, fats]):
        return jsonify({'error': 'Missing data'}), 400

    food_item = FoodItem(name=name, calories=calories, protein=protein, carbohydrates=carbohydrates, fats=fats)
    db.session.add(food_item)
    db.session.commit()
    return jsonify({'message': f'Added food item {food_item.name}'}), 201

@app.route('/get_food', methods=['GET'])
def get_food():
    food_items = FoodItem.query.all()
    food_list = [{'id': item.id, 'name': item.name, 'calories': item.calories, 'protein': item.protein, 'carbohydrates': item.carbohydrates, 'fats': item.fats} for item in food_items]
    return jsonify(food_list), 200

@app.route('/update_food/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    food_item = FoodItem.query.get(food_id)
    if not food_item:
        return jsonify({'error': 'Food item not found'}), 404

    data = request.get_json()
    food_item.name = data.get('name', food_item.name)
    food_item.calories = data.get('calories', food_item.calories)
    food_item.protein = data.get('protein', food_item.protein)
    food_item.carbohydrates = data.get('carbohydrates', food_item.carbohydrates)
    food_item.fats = data.get('fats', food_item.fats)

    db.session.commit()
    return jsonify({'message': f'Food item {food_item.name} updated successfully'}), 200

@app.route('/delete_food/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    food_item = FoodItem.query.get(food_id)
    if not food_item:
        return jsonify({'error': 'Food item not found'}), 404

    db.session.delete(food_item)
    db.session.commit()
    return jsonify({'message': f'Food item {food_item.name} deleted successfully'}), 200

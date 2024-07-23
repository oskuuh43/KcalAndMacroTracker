from app import db  # Import the db instance from the app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    daily_calorie_goal = db.Column(db.Integer, nullable=False, default=2000)
    daily_protein_goal = db.Column(db.Integer, nullable=False, default=150)  # grams
    daily_fat_goal = db.Column(db.Integer, nullable=False, default=70)       # grams
    daily_carbs_goal = db.Column(db.Integer, nullable=False, default=250)

    # Relationship to log food entries
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)  # Fixed the default to use callable datetime.utcnow
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)

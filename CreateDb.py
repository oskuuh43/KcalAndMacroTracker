from app import app, db
from app.models import FoodItem

with app.app_context():
    db.create_all()
    print("Database tables created")
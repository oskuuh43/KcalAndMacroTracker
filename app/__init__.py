from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


# Initializes Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initializes the database and migration tools
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Initializes Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


from app import routes, models


# Defines the user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

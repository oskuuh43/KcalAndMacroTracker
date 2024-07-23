from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.models import User, FoodItem
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    food_items = FoodItem.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', food_items=food_items)

@app.route('/add_food', methods=['GET', 'POST'])
@login_required
def add_food():
    if request.method == 'POST':
        name = request.form.get('name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        carbohydrates = request.form.get('carbohydrates')
        fats = request.form.get('fats')

        new_food_item = FoodItem(name=name, calories=calories, protein=protein, carbohydrates=carbohydrates, fats=fats, user_id=current_user.id)
        db.session.add(new_food_item)
        db.session.commit()
        flash('Food item added successfully', 'success')
        return redirect(url_for('index'))
    return render_template('add_food.html')

@app.route('/delete_food/<int:id>', methods=['POST'])
@login_required
def delete_food(id):
    food_item = FoodItem.query.get(id)
    if food_item and food_item.user_id == current_user.id:
        db.session.delete(food_item)
        db.session.commit()
        flash('Food item deleted successfully', 'success')
    return redirect(url_for('index'))

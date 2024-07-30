from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from app import db
from app.models import User, FoodEntry
from app.forms import RegistrationForm, LoginForm
from app.data_utils import load_food_data, get_high_protein_options

# Define the Blueprint
bp = Blueprint('main', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)).first()
            if existing_user:
                flash('A user with this username or email already exists. Please choose another.', 'danger')
                return redirect(url_for('main.register'))

            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            print(f"Error: {e}")
    else:
        if form.errors:
            flash('Registration form contains errors. Please check your inputs.', 'danger')
            print(form.errors)
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/home')
@login_required
def home():
    today = datetime.utcnow().date()
    user = current_user

    food_entries_today = FoodEntry.query.filter_by(user_id=user.id, date=today).all()

    total_calories = sum(entry.calories for entry in food_entries_today)
    total_protein = sum(entry.protein for entry in food_entries_today)
    total_fat = sum(entry.fat for entry in food_entries_today)
    total_carbs = sum(entry.carbs for entry in food_entries_today)

    calories_left = user.daily_calorie_goal - total_calories
    protein_left = user.daily_protein_goal - total_protein
    fat_left = user.daily_fat_goal - total_fat
    carbs_left = user.daily_carbs_goal - total_carbs

    return render_template('home.html', today=today,
                           calorie_goal=user.daily_calorie_goal,
                           calories_left=calories_left,
                           protein_goal=user.daily_protein_goal,
                           protein_left=protein_left,
                           fat_goal=user.daily_fat_goal,
                           fat_left=fat_left,
                           carbs_goal=user.daily_carbs_goal,
                           carbs_left=carbs_left,
                           food_entries=food_entries_today)

@bp.route('/log_food', methods=['GET', 'POST'])
@login_required
def log_food():
    if request.method == 'POST':
        name = request.form.get('name')
        calories_per_100g = request.form.get('calories_per_100g')
        protein_per_100g = request.form.get('protein_per_100g')
        fat_per_100g = request.form.get('fat_per_100g')
        carbs_per_100g = request.form.get('carbs_per_100g')
        amount = request.form.get('amount')

        if not all([name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, amount]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.log_food'))

        try:
            # Convert to float for calculations
            calories_per_100g = float(calories_per_100g)
            protein_per_100g = float(protein_per_100g)
            fat_per_100g = float(fat_per_100g)
            carbs_per_100g = float(carbs_per_100g)
            amount = float(amount)

            # Calculate total calories and macros based on the amount of food
            total_calories = (calories_per_100g / 100) * amount
            total_protein = (protein_per_100g / 100) * amount
            total_fat = (fat_per_100g / 100) * amount
            total_carbs = (carbs_per_100g / 100) * amount

            entry = FoodEntry(
                user_id=current_user.id,
                name=name,
                calories=total_calories,
                protein=total_protein,
                fat=total_fat,
                carbs=total_carbs,
                date=datetime.utcnow().date()
            )
            db.session.add(entry)
            db.session.commit()
            flash('Food item logged successfully', 'success')

        except ValueError:
            flash('Please enter valid numbers for all fields.', 'danger')
            return redirect(url_for('main.log_food'))

    today = datetime.utcnow().date()
    food_entries_today = FoodEntry.query.filter_by(user_id=current_user.id, date=today).all()

    return render_template('log_food.html', food_entries=food_entries_today)


@bp.route('/set_goals', methods=['GET', 'POST'])
@login_required
def set_goals():
    if request.method == 'POST':
        try:
            current_user.daily_calorie_goal = int(request.form['calorie_goal'])
            current_user.daily_protein_goal = int(request.form['protein_goal'])
            current_user.daily_fat_goal = int(request.form['fat_goal'])
            current_user.daily_carbs_goal = int(request.form['carbs_goal'])

            db.session.commit()
            flash('Goals updated successfully', 'success')
        except ValueError:
            flash('Please enter valid numbers for all fields.', 'danger')
        return redirect(url_for('main.home'))

    return render_template('set_goals.html')


@bp.route('/high_protein', methods=['GET', 'POST'])
@login_required
def high_protein():
    df = load_food_data()
    high_protein_options = []

    if request.method == 'POST':
        try:
            min_protein_ratio = float(request.form.get('min_protein_ratio', 0.1))
            sort_by = request.form.get('sort_by', 'protein_to_calories')
            search_term = request.form.get('search_term', '').lower()

            # Get high protein options
            high_protein_options = get_high_protein_options(df, min_protein_ratio)

            # Filter by search term
            if search_term:
                high_protein_options = [item for item in high_protein_options if search_term in item['Name'].lower()]

            # Sort by selected criteria
            if sort_by == 'protein_to_calories':
                high_protein_options = sorted(high_protein_options, key=lambda x: x['Protein_to_Calories'],
                                              reverse=True)
            elif sort_by == 'name':
                high_protein_options = sorted(high_protein_options, key=lambda x: x['Name'])

        except ValueError:
            flash('Invalid input. Please check your values.', 'danger')

    return render_template('high_protein.html', high_protein_options=high_protein_options)



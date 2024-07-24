from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.models import User, FoodEntry
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime




@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)).first()
            if existing_user:
                flash('A user with this username or email already exists. Please choose another.', 'danger')
                return redirect(url_for('register'))

            # Create new user
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            print(f"Error: {e}")  # Log the error for debugging
    else:
        if form.errors:
            flash('Registration form contains errors. Please check your inputs.', 'danger')
            print(form.errors)  # Log form errors for debugging
    return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    today = datetime.utcnow().date()
    user = current_user

    # Get today's food entries
    food_entries_today = FoodEntry.query.filter_by(user_id=user.id, date=today).all()

    # Calculate total consumed
    total_calories = sum(entry.calories for entry in food_entries_today)
    total_protein = sum(entry.protein for entry in food_entries_today)
    total_fat = sum(entry.fat for entry in food_entries_today)
    total_carbs = sum(entry.carbs for entry in food_entries_today)

    # Calculate remaining values
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


@app.route('/log_food', methods=['GET', 'POST'])
@login_required
def log_food():
    if request.method == 'POST':
        name = request.form.get('name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        fat = request.form.get('fat')
        carbs = request.form.get('carbs')

        if not all([name, calories, protein, fat, carbs]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('log_food'))

        try:
            calories = int(calories)
            protein = int(protein)
            fat = int(fat)
            carbs = int(carbs)
        except ValueError:
            flash('Please enter valid numbers for calories and macronutrients.', 'danger')
            return redirect(url_for('log_food'))

        entry = FoodEntry(user_id=current_user.id, name=name, calories=calories, protein=protein, fat=fat, carbs=carbs,
                          date=datetime.utcnow().date())
        db.session.add(entry)
        db.session.commit()
        flash('Food item logged successfully', 'success')

    today = datetime.utcnow().date()
    food_entries_today = FoodEntry.query.filter_by(user_id=current_user.id, date=today).all()

    return render_template('log_food.html', food_entries=food_entries_today)



@app.route('/set_goals', methods=['GET', 'POST'])
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
        return redirect(url_for('home'))

    return render_template('set_goals.html')

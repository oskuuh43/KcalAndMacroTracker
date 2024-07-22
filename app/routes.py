from flask import render_template, request, redirect, url_for
from app import app#, db
#from app.models import User  # Assuming you have a User model

@app.route('/')
def index():
    return "Hello World!"
    #return render_template('index.html')

#@app.route('/login', methods=['GET', 'POST'])
#def login():
 #   if request.method == 'POST':
        # Handle login
  #      pass
 #   return render_template('login.html')
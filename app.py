# Import necessary modules
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'apfel123123'
# app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\Marcel\Documents\GitHub\py_photo-platform\database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///prod.db.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define Follolw model
class Follows(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer)
    followed_id = db.Column(db.Integer)

# Define User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    bio = db.Column(db.String(100))
    followers = db.Column(db.Integer)

# Photo model
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))
        
        # Create a new user
        new_user = User(username=username, password=password, bio="Add your Bio here!", followers="0")
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the newly created user
        login_user(new_user)
        return redirect(url_for('myAccount'))  # Redirect to myAccount route
    
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# my account route
@app.route('/myaccount')
@login_required
def myAccount():
    return render_template('account.html', username=current_user.username, bio=current_user.bio, followers=current_user.followers)

# Add new route to display user-specific page
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_page(user_id):
    if request.method == 'POST':
        follow = request.form['button__follow']
        
        # Check if the current user already follows the user
        existing_follow = Follows.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
        if existing_follow:
            flash('You already follow this user.')
        else:
            # Create a new follow relationship
            new_follow = Follows(follower_id=current_user.id, followed_id=user_id)
            db.session.add(new_follow)
            db.session.commit()
    user = User.query.get_or_404(user_id)
    return render_template('user_page.html', user=user, username=user.username, followers=user.followers, bio=user.bio)

@app.route('/usrset/edit', methods=['POST', 'GET'])
@login_required
def edit_bio():
    if request.method == 'POST':
        new_bio = request.form['new_bio']
        current_user.bio = new_bio
        db.session.commit()
        flash('Bio updated successfully!')
        return render_template('account.html', username=current_user.username, bio=current_user.bio, followers=current_user.followers)
    if request.method == 'GET':
        return render_template('user__edit.html', username=current_user.username, bio=current_user.bio, followers=current_user.followers)

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
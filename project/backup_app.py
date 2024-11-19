# -------------------- Importing Modules --------------------

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
# from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect(app)
# from flask_socketio import SocketIO


# -------------------- Initializing --------------------

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

# -------------------- Databases --------------------

# User db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('12345')
        )
        db.session.add(admin_user)
        db.session.commit()
        app.logger.info('Default admin user created.')

# Device db
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    device_name = db.Column(db.String(80), nullable=False)
    device_type = db.Column(db.String(80), nullable=False)
    light_level = db.Column(db.Integer)
    humidity_level = db.Column(db.Integer)
    temperature = db.Column(db.Integer)
    smoke_level = db.Column(db.Integer)

# Update the database
with app.app_context():
    db.create_all()

# socketio = SocketIO(app)


# -------------------- Routing --------------------

# Index / Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']

        # Check if login_id is an email or username
        user = None
        if '@' in login_id:
            user = User.query.filter_by(email=login_id).first()
        else:
            user = User.query.filter_by(username=login_id).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash('You were successfully logged in')
            app.logger.info(f'User {user.username} logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            app.logger.warning('Login unsuccessful: Incorrect username/email or password.')
            flash('Login Unsuccessful. Please check username/email and password')
            return redirect(url_for('login'))

    return render_template('login.html')

# Sign up / Sign in Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('signup'))

            if User.query.filter_by(email=email).first():
                flash('Email already exists. Please choose a different one.')
                return redirect(url_for('signup'))

            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email,
                            password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f'Error during signup: {e}')
            flash('An error occurred while creating your account. Please try again.')
            return redirect(url_for('signup'))

    return render_template('signup.html')


# Logout Page
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were successfully logged out')
    return redirect(url_for('index'))

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Logic for code to process the message, e.g., send an email

        flash('Your message has been sent successfully!')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Help Page
@app.route('/support')
def support():
    return render_template('support.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = User.query.filter_by(username=session.get('username')).first()
        return render_template('dashboard.html', user=user)
    else:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))

# Add device with in dashboard
@app.route('/add_device', methods=['POST'])
def add_device():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user_email = session['username']
    device_name = request.form['device_name']
    device_type = request.form['device_type']

    new_device = Device(user_email=user_email, device_name=device_name, device_type=device_type)
    db.session.add(new_device)
    db.session.commit()

    flash('Device added successfully!')
    return redirect(url_for('dashboard'))

# Modify device with in dashboard
@app.route('/modify_device', methods=['POST'])
def modify_device():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    device_id = request.form['device_id']
    device = Device.query.get(device_id)
    if not device:
        flash('Device not found.')
        return redirect(url_for('dashboard'))

    device.light_level = request.form.get('light_limit', device.light_level)
    device.humidity_level = request.form.get('humidity_limit', device.humidity_level)
    device.temperature = request.form.get('temperature_limit', device.temperature)
    device.smoke_level = request.form.get('smoke_limit', device.smoke_level)

    db.session.commit()
    flash('Device modified successfully!')
    return redirect(url_for('dashboard'))

# Remove device with in dashboard
@app.route('/remove_device', methods=['POST'])
def remove_device():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    device_id = request.form['device_id']
    device = Device.query.get(device_id)
    if not device:
        flash('Device not found.')
        return redirect(url_for('dashboard'))

    db.session.delete(device)
    db.session.commit()
    flash('Device removed successfully!')
    return redirect(url_for('dashboard'))


# Settings Page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        flash('Please log in to access the settings.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session.get('username')).first()

    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']
        new_password = request.form['password']
        new_theme = request.form['theme']  # Get the selected theme

        # Check for username and email uniqueness
        if User.query.filter_by(username=new_username).first() and new_username != user.username:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('settings'))

        if User.query.filter_by(email=new_email).first() and new_email != user.email:
            flash('Email already exists. Please choose a different one.')
            return redirect(url_for('settings'))

        # Update user info
        user.username = new_username
        user.email = new_email
        if new_password:
            user.password = generate_password_hash(
                new_password)
        user.theme = new_theme  # Save the selected theme

        db.session.commit()
        flash('Settings updated successfully')
        return redirect(url_for('dashboard'))

    return render_template('settings.html', user=user)

# -------------------- Error Handling --------------------

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Internal Server Error: {error}')
    return "500 Internal Server Error", 500


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Not Found: {error}')
    return "404 Not Found", 404


# -------------------- testing zone --------------------

# @app.route('/test-settings')
# def test_settings():
#     if 'username' not in session:
#         flash('Please log in to access the settings.')
#         return redirect(url_for('login'))

#     user = User.query.filter_by(username=session.get('username')).first()
#     return f"User found: {user.username}, Email: {user.email}"


# @app.route('/test-db')
# def test_db():
#     try:
#         users = User.query.all()
#         return f"Users in database: {[user.username for user in users]}"
#     except Exception as e:
#         app.logger.error(f'Error accessing database: {e}')
#         return "Error accessing database."



# -------------------------------------------

if __name__ == '__main__':
    app.run(app,debug=True)
    # Start the SocketIO server
    # socketio.run(app, debug=True)


# ------------------ END -------------------------
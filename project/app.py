from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_socketio import SocketIO, emit
import random
import time
import threading
import requests
from datetime import datetime
# from flask_cors import CORS

# -------------------- Initializing --------------------

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'  # For SocketIO

db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")


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
        devices = Device.query.filter_by(user_email=user.email).all()
        return render_template('dashboard.html', user=user, devices=devices)
    else:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))

# Add device
@app.route('/add_device', methods=['POST'])
def add_device():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'})

    try:
        user = User.query.filter_by(username=session['username']).first()
        device_name = request.form['device_name']
        device_type = request.form['device_type']

        new_device = Device(
            user_email=user.email,
            device_name=device_name,
            device_type=device_type
        )
        db.session.add(new_device)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Device added successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Modify device
@app.route('/modify_device', methods=['POST'])
def modify_device():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'})

    try:
        device_id = request.form['device_id']
        device = Device.query.get(device_id)
        
        if not device:
            return jsonify({'success': False, 'message': 'Device not found.'})

        if request.form.get('light_limit'):
            device.light_level = int(request.form['light_limit'])
        if request.form.get('humidity_limit'):
            device.humidity_level = int(request.form['humidity_limit'])
        if request.form.get('temperature_limit'):
            device.temperature = int(request.form['temperature_limit'])
        if request.form.get('smoke_limit'):
            device.smoke_level = int(request.form['smoke_limit'])

        db.session.commit()
        return jsonify({'success': True, 'message': 'Device modified successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_thresholds', methods=['GET'])
def get_thresholds():
    user_email = request.args.get('email')
    device = Device.query.filter_by(user_email=user_email).first()
    if device:
        return jsonify({
            'light': device.light_level,
            'humidity': device.humidity_level,
            'temperature': device.temperature,
            'smoke': device.smoke_level
        })
    return jsonify({'error': 'Device not found'}), 404

# Remove device
@app.route('/remove_device', methods=['POST'])
def remove_device():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'})

    try:
        device_id = request.form['device_id']
        device = Device.query.get(device_id)
        
        if not device:
            return jsonify({'success': False, 'message': 'Device not found.'})

        db.session.delete(device)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Device removed successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Get devices
@app.route('/get_devices')
def get_devices():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'})

    try:
        user = User.query.filter_by(username=session['username']).first()
        devices = Device.query.filter_by(user_email=user.email).all()
        devices_list = [{'id': d.id, 'name': d.device_name, 'type': d.device_type} for d in devices]
        return jsonify({'success': True, 'devices': devices_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@socketio.on('request_sensor_data')
def handle_sensor_request():
    """Handle initial sensor data request when analytics is opened"""
    # Get the latest sensor data
    try:
        response = requests.get('http://192.168.15.124/data') # URL on which ESP32 is hosting
        if response.status_code == 200:
            data = response.json()
            emit('sensor_data', {
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'light': data['lightLevel'],
                'smoke': data['coLevel'],
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        # Fallback to random data if ESP32 is not accessible
        emit('sensor_data', {
            'temperature': random.uniform(20, 30),
            'humidity': random.uniform(30, 70),
            'light': random.uniform(0, 100),
            'smoke': random.uniform(0, 50),
            'timestamp': datetime.now().isoformat()
        })


ESP32_URL_A = 'http://192.168.15.124/buzzer'
ESP32_URL_D = 'http://192.168.15.124/buzzer/deactivate'

@app.route('/activate_buzzer', methods=['POST'])
def activate_buzzer():
    try:
        response = requests.post(ESP32_URL_A)
        if response.status_code == 200:
            return jsonify({"status": "Buzzer activated"})
        else:
            return jsonify({"status": "Failed to activate buzzer"}), 500
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500


@app.route('/deactivate_buzzer', methods=['POST'])
def deactivate_buzzer():
    try:
        response = requests.post(ESP32_URL_D)
        if response.status_code == 200:
            return jsonify({"status": "Buzzer deactivated"})
        else:
            return jsonify({"status": "Failed to deactivate buzzer"}), 500
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500


# -------------------- Sensor Data Generation (WebSocket) --------------------

# WebSocket route for client connections

# Test
# @socketio.on('message')
# def handle_message(data):
#     print(f"Received message: {data}")
#     emit('response', {'message': 'Message received'})
# Track active connections

# WebSocket route for client connections
active_connections = 0

@socketio.on('connect')
def handle_connect():
    global active_connections
    active_connections += 1
    print(f"Client connected. Active connections: {active_connections}")

@socketio.on('disconnect')
def handle_disconnect():
    global active_connections
    active_connections = max(0, active_connections - 1)
    print(f"Client disconnected. Active connections: {active_connections}")
    

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
        user_theme = request.form['theme']  # Get the selected theme

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
            user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('Settings updated successfully.')
        return redirect(url_for('settings'))

    return render_template('settings.html', user=user)

@app.route('/update_theme', methods=['POST'])
def update_theme():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_theme = request.json.get('theme', 'dark')
    user = User.query.filter_by(username=session['username']).first()
    if user:
        user.theme = user_theme
        db.session.commit()
    
    return jsonify({'status': 'success'})


# -------------------- Running the App --------------------
if __name__ == '__main__':
    # Start the background thread for sensor data generation
    threading.Thread(target=handle_sensor_request, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

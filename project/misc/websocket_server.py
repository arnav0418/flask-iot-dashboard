from flask import Flask
from flask_socketio import SocketIO, emit
import random
import time
import threading

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")

# Background thread to simulate sensor data updates
def generate_sensor_data():
    while True:
        # Simulated sensor data
        sensor_data = {
            'light': random.randint(0, 100),
            'humidity': random.randint(0, 100),
            'temperature': random.randint(-50, 50),
            'smoke': random.randint(0, 100)
        }
        # Emit data to all connected clients
        socketio.emit('sensor_data', sensor_data)
        time.sleep(3)  # Adjust interval as needed

# WebSocket route for client connections
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Test message route
@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    emit('response', {'message': 'Message received'})

# HTTP route for testing purposes
@app.route('/')
def index():
    return "WebSocket server is running!"

if __name__ == '__main__':
    # Start the background thread for sensor data generation
    threading.Thread(target=generate_sensor_data, daemon=True).start()
    # Run the server
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

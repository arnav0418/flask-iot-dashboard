IoT Dashboard
A Flask‑based web application for managing IoT devices, viewing real‑time sensor data, and controlling peripherals such as buzzers. The backend persists user and device data with SQLAlchemy and broadcasts live updates via Socket.IO for an interactive dashboard experience

Features
User authentication – sign‑up, login, logout, and session management with password hashing

Device management – add, update, remove, and list devices with configurable thresholds for light, humidity, temperature, and smoke

Real‑time analytics – clients request sensor data over WebSocket and receive live readings from an ESP32 or randomized fallback values

Hardware control – REST endpoints toggle an ESP32‑connected buzzer on or off

User settings – update profile information and theme preference through a dedicated settings page and JSON endpoint

Optional simulator – a standalone Socket.IO server can generate synthetic sensor data for local testing

Project Structure
project/
  app.py                 # Main Flask application
  backup_app.py          # Legacy/backup version
  debug_mode_setup.txt   # Commands to enable Flask debug mode
  requirements.txt       # Python dependencies
  esp/                   # ESP32 firmware (combined.ino)
  instance/              # SQLite databases (users.db, iot_dashboard.db)
  misc/                  # Utility scripts (e.g., websocket_server.py)
  static/                # CSS, JS, and image assets
  templates/             # HTML templates for pages
Requirements
Install dependencies using pip:

pip install -r requirements.txt
Optional Development Setup
Enable debug mode for iterative development:

export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
Running the Application
Start the Flask server (with Socket.IO support) on port 5000:

python app.py
ESP32 Integration
Firmware in esp/combined.ino connects an ESP32 to Wi‑Fi, collects DHT temperature/humidity, MQ‑7 CO levels, and LDR light levels, then periodically sends readings to the Flask backend and exposes HTTP endpoints for buzzer control

API Overview
Endpoint	Method	Description
/login, /signup	GET/POST	User authentication
/dashboard	GET	Device overview for logged‑in users
/add_device	POST	Register a new device
/modify_device	POST	Update device thresholds
/remove_device	POST	Delete a device
/get_devices, /get_thresholds	GET	Retrieve device data
/activate_buzzer, /deactivate_buzzer	POST	Control ESP32 buzzer
/settings, /update_theme	GET/POST	Update profile and theme
Socket.IO event request_sensor_data	WS	Push latest sensor readings to clients
Notes
A default admin user (admin / 12345) is created on first run for bootstrap access

Databases are stored in the instance/ directory; remove users.db and iot_dashboard.db to reset the state.

Testing
No automated tests or scripts were executed; this repository was examined in a read‑only environment.

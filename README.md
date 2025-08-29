# IoT Dashboard

A Flask‑based web application for managing IoT devices, viewing real‑time sensor data, and controlling peripherals (e.g., a buzzer). The backend persists user and device data with SQLAlchemy and broadcasts live updates via Socket.IO for an interactive dashboard experience.

---

## Table of Contents

* [Features](#features)
* [Architecture](#architecture)
* [Project Structure](#project-structure)
* [Requirements](#requirements)
* [Getting Started](#getting-started)

  * [Installation](#installation)
  * [Optional: Development Mode](#optional-development-mode)
  * [Run the Application](#run-the-application)
* [ESP32 Integration](#esp32-integration)
* [API Overview](#api-overview)
* [WebSocket Events](#websocket-events)
* [Data & Storage](#data--storage)
* [Resetting the App State](#resetting-the-app-state)
* [Testing](#testing)
* [Security Notes](#security-notes)
* [Roadmap](#roadmap)
* [License](#license)

---

## Features

* **User authentication** – Sign‑up, login, logout, and session management with password hashing.
* **Device management** – Add, update, remove, and list devices with configurable thresholds for **light**, **humidity**, **temperature**, and **smoke**.
* **Real‑time analytics** – Clients request sensor data over WebSocket and receive live readings from an **ESP32** or randomized fallback values.
* **Hardware control** – REST endpoints toggle an ESP32‑connected **buzzer** on or off.
* **User settings** – Update profile information and theme preference through a dedicated settings page and JSON endpoint.
* **Optional simulator** – A standalone Socket.IO server can generate synthetic sensor data for local testing.

---

## Architecture

```
[ Browser / Dashboard ] ⇄ (HTTP REST & WebSocket) ⇄ [ Flask App + Socket.IO ]
                                          │
                                          ├── SQLAlchemy/SQLite (users & devices)
                                          └── ESP32 (HTTP endpoints + telemetry)
```

* **Flask (HTTP)** exposes authentication, device CRUD, settings, and hardware control.
* **Socket.IO (WS)** streams sensor readings to connected clients on demand.
* **SQLAlchemy + SQLite** store users and device metadata under `instance/`.
* **ESP32 firmware** posts telemetry and responds to buzzer control.

---

## Project Structure

```
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
```

---

## Requirements

* **Python** (version as required by your `requirements.txt`)
* **Pip** for dependency installation
* (Optional) **ESP32** with the provided firmware for live data and buzzer control

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Getting Started

### Installation

1. Clone this repository and navigate to the project folder.
2. Install dependencies via `pip install -r requirements.txt`.

### Optional: Development Mode

Enable Flask debug mode for iterative development:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

> See `debug_mode_setup.txt` for additional notes.

### Run the Application

Start the Flask server (with Socket.IO support) on port **5000**:

```bash
python app.py
```

Access the dashboard at: `http://localhost:5000`.

---

## ESP32 Integration

* Firmware in `esp/combined.ino` connects an ESP32 to Wi‑Fi, collects **DHT** temperature/humidity, **MQ‑7** CO levels, and **LDR** light levels.
* The ESP32 periodically sends readings to the Flask backend and exposes HTTP endpoints for **buzzer** control (see API below).
* Ensure the device is configured with the correct backend host/port.

---

## API Overview

| Endpoint                                 | Method   | Description                                                     |
| ---------------------------------------- | -------- | --------------------------------------------------------------- |
| `/login`, `/signup`                      | GET/POST | User authentication (login, registration).                      |
| `/dashboard`                             | GET      | Device overview for logged‑in users.                            |
| `/add_device`                            | POST     | Register a new device with thresholds.                          |
| `/modify_device`                         | POST     | Update device thresholds (light, humidity, temperature, smoke). |
| `/remove_device`                         | POST     | Delete a device.                                                |
| `/get_devices`, `/get_thresholds`        | GET      | Retrieve device metadata and thresholds.                        |
| `/activate_buzzer`, `/deactivate_buzzer` | POST     | Control the ESP32‑attached buzzer.                              |
| `/settings`, `/update_theme`             | GET/POST | Update profile and theme preference.                            |

> Authentication may be required for certain endpoints; see application code/templates for access control specifics.

---

## WebSocket Events

* **Client → Server**: `request_sensor_data`

  * Triggers the backend to push the most recent sensor readings.
* **Server → Client**: *(implementation‑dependent)* event(s) that deliver readings and updates to subscribed clients.

> A local simulator (`misc/websocket_server.py`) can be used to generate synthetic data when hardware is unavailable.

---

## Data & Storage

* SQLite databases are stored under `instance/`:

  * `users.db` – authentication & profile data
  * `iot_dashboard.db` – devices and thresholds

### Resetting the App State

To reset the application to a clean state, stop the server and remove the databases:

```bash
rm -f instance/users.db instance/iot_dashboard.db
```

---

## Testing

* No automated tests or scripts were executed during the initial review.
* Recommended next steps:

  * Add unit tests for authentication, device CRUD, and Socket.IO handlers.
  * Include an integration test for ESP32 endpoints (buzzer control and telemetry ingest).

---

## Security Notes

* A default admin user (**admin / 12345**) is created on first run for bootstrap access.

  * **Change these credentials immediately** in any non‑local environment.
* Review session management, CSRF protection, and input validation before deploying externally.

---

## Roadmap

* Add automated tests (unit + integration).
* Add role‑based access control (RBAC) for multi‑tenant scenarios.
* Implement alerts when sensor readings cross thresholds.
* Containerize with Docker; add CI/CD workflow.
* Optional: Add OCR for image‑only sensor screenshots/logs.

---


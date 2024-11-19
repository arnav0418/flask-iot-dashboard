#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

// Wi-Fi Credentials
const char* ssid = "Hirdy";
const char* password = "pygx3165";
const char* FLASK_SERVER = "http://127.0.0.1:5000/dashboard";

// Sensor Pin Configuration
#define DHT_PIN 4       // GPIO pin for DHT sensor
#define DHT_TYPE DHT11  // Sensor type: DHT11 or DHT22
#define MQ7_PIN 32      // GPIO pin for MQ-7 sensor (ADC)
#define LDR_PIN 33      // GPIO pin for LDR (ADC)
#define BUZZ_PIN 15     // GPIO pin for buzzer

// Update interval (milliseconds)
const unsigned long UPDATE_INTERVAL = 5000;
unsigned long lastUpdate = 0;

// DHT Sensor
DHT dht(DHT_PIN, DHT_TYPE);

// MQ-7 Calibration Constants
#define RL_VALUE 10.0             // Load resistance in kilo-ohms
#define RO_CLEAN_AIR_FACTOR 9.83  // Sensor resistance in clean air
float Ro = 10.0;                  // Initial sensor resistance

// Sensor data structure
struct SensorData {
  float temperature;
  float humidity;
  int lightLevel;
  float coLevel;
  bool isValid;
};
SensorData currentData;

// Wi-Fi Web Server
WebServer server(80);

void setup() {
  Serial.begin(115200);

  // Initialize sensors
  dht.begin();
  pinMode(LDR_PIN, INPUT);
  pinMode(MQ7_PIN, INPUT);
  pinMode(BUZZ_PIN, OUTPUT);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Setup server routes
  setupRoutes();
  server.begin();
}

void loop() {
  server.handleClient();

  // Update sensor readings every UPDATE_INTERVAL
  if (millis() - lastUpdate >= UPDATE_INTERVAL) {
    updateSensorData();
    sendDataToFlask();
    lastUpdate = millis();
  }
}

void setupRoutes() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/data", HTTP_GET, handleData);
  server.on("/buzzer", HTTP_POST, handleBuzzer);
  server.on("/buzzer/deactivate", HTTP_POST, handleDeactivateBuzzer);

    server.on("/style.css", HTTP_GET, []() {
      server.send(200, "text/css", getStyleSheet());
    });
  server.on("/script.js", HTTP_GET, []() {
    server.send(200, "text/javascript", getJavaScript());
  });
}

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Sensor Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <h1>ESP32 Sensor Monitor</h1>
        <div class="grid">
            <div class="card" id="temperature">
                <h2>Temperature</h2>
                <p class="value">-- °C</p>
            </div>
            <div class="card" id="humidity">
                <h2>Humidity</h2>
                <p class="value">-- %</p>
            </div>
            <div class="card" id="light">
                <h2>Light Level</h2>
                <p class="value">--</p>
            </div>
            <div class="card" id="co">
                <h2>CO Level</h2>
                <p class="value">--</p>
            </div>
        </div>
        <button id="buzzerButton" class="buzzer-button">Activate Buzzer</button>
        <button id="buzzerDeactivateButton" class="buzzer-button">Deactivate Buzzer</button>
        <p id="buzzerStatus">Buzzer is inactive</p>
        <div class="status">
            <p>Last updated: <span id="lastUpdate">Never</span></p>
        </div>
    </div>
    <script src="/script.js"></script>
</body>
</html>
  )";
  server.send(200, "text/html", html);
}

void handleData() {
  StaticJsonDocument<200> doc;
  doc["temperature"] = currentData.temperature;
  doc["humidity"] = currentData.humidity;
  doc["lightLevel"] = currentData.lightLevel;
  doc["coLevel"] = currentData.coLevel;
  doc["isValid"] = currentData.isValid;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleBuzzer() {
  digitalWrite(BUZZ_PIN, HIGH);  // Activate buzzer
  // delay(5000);                   // Keep it on for 5 seconds
  // digitalWrite(BUZZ_PIN, LOW);   // Deactivate buzzer
  server.send(200, "application/json", "{\"status\": \"Buzzer Activated\"}");
}

void handleDeactivateBuzzer() {
  digitalWrite(BUZZ_PIN, LOW);  // Ensure the buzzer is off
  server.send(200, "application/json", "{\"status\": \"Buzzer Deactivated\"}");
}


void updateSensorData() {
  currentData.temperature = dht.readTemperature();
  currentData.humidity = dht.readHumidity();

  // Read LDR value
  int rawLDRValue = analogRead(LDR_PIN);
  int minLDRValue = 100;
  int maxLDRValue = 3060;
  currentData.lightLevel = map(rawLDRValue, minLDRValue, maxLDRValue, 0, 100);
  currentData.lightLevel = constrain(currentData.lightLevel, 0, 100);

  // MQ-7 sensor logic for CO level
  float mq7Value = analogRead(MQ7_PIN);
  float voltage = (mq7Value / 4095.0) * 3.3;
  float rs = (3.3 - voltage) * RL_VALUE / voltage;
  currentData.coLevel = rs / Ro;

  currentData.isValid = !isnan(currentData.temperature) && !isnan(currentData.humidity);
}

void sendDataToFlask() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(FLASK_SERVER);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["temperature"] = currentData.temperature;
    doc["humidity"] = currentData.humidity;
    doc["lightLevel"] = currentData.lightLevel;
    doc["coLevel"] = currentData.coLevel;

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully");
    } else {
      Serial.print("Error sending data: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
}

String getStyleSheet() {
  return R"(
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background-color: #f0f2f5;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    text-align: center;
    color: #1a1a1a;
    margin-bottom: 30px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card h2 {
    color: #666;
    font-size: 1.1em;
    margin-bottom: 10px;
}

.value {
    font-size: 2em;
    font-weight: bold;
    color: #2196F3;
}

.status {
    text-align: center;
    color: #666;
}

.buzzer-button {
    display: block;
    margin: 20px auto;
    padding: 10px 20px;
    background-color: #ff5722;
    color: white;
    font-size: 1em;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.buzzer-button:hover {
    background-color: #e64a19;
}

@media (max-width: 600px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
  )";
}

String getJavaScript() {
  return R"(
function updateSensorData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            if (data.isValid) {
                document.querySelector('#temperature .value').textContent = 
                    `${data.temperature.toFixed(1)} °C`;
                document.querySelector('#humidity .value').textContent = 
                    `${data.humidity.toFixed(1)} %`;
                document.querySelector('#light .value').textContent = 
                    `${data.lightLevel.toFixed(1)}`;
                document.querySelector('#co .value').textContent = 
                    `${data.coLevel.toFixed(2)}`;
                document.getElementById('lastUpdate').textContent = 
                    new Date().toLocaleTimeString();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Activate buzzer when button is clicked
document.getElementById('buzzerButton').addEventListener('click', () => {
    fetch('/buzzer', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('buzzerStatus').textContent = "Buzzer is active";
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('buzzerStatus').textContent = "Error activating the buzzer";
        });
});

document.getElementById('buzzerDeactivateButton').addEventListener('click', () => {
    fetch('/buzzer/deactivate', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('buzzerStatus').textContent = "Buzzer is inactive";
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('buzzerStatus').textContent = "Error deactivating the buzzer";
        });
});

// Update every 5 seconds
setInterval(updateSensorData, 5000);
updateSensorData(); // Initial update
  )";
}

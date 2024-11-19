// Initialize Socket.IO connection
const socket = io();
let isAnalyticsActive = false;
let refreshInterval = null; // For automatic data refresh
let deviceThresholds = {}; // Store thresholds for the device

// Fetch thresholds from the server
function fetchThresholds(userEmail) {
  return fetch(`/get_thresholds?email=${userEmail}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error(data.error);
      } else {
        deviceThresholds = data;
        console.log("Thresholds loaded:", deviceThresholds);
      }
    })
    .catch((error) => console.error("Error fetching thresholds:", error));
}

// Activate the buzzer
function activateBuzzer() {
  fetch("/activate_buzzer", { method: "POST" })
    .then((response) => response.json())
    .then((data) => console.log(data.status))
    .catch((error) => console.error("Error activating buzzer:", error));
}

document.getElementById("buzzerButton").addEventListener("click", () => {
  fetch("/activate_buzzer", { method: "POST" })
    .then((response) => response.json())
    .catch((error) => console.error("Error:", error));
});

document
  .getElementById("buzzerDeactivateButton")
  .addEventListener("click", () => {
    fetch("/deactivate_buzzer", { method: "POST" })
      .then((response) => response.json())
      .catch((error) => console.error("Error:", error));
  });

// Socket.IO event handlers
socket.on("connect", () => {
  console.log("Connected to WebSocket server");
});

socket.on("disconnect", () => {
  console.log("Disconnected from WebSocket server");
  if (isAnalyticsActive) {
    updateSensorDisplays("--");
  }
});

socket.on("sensor_data", (data) => {
  if (isAnalyticsActive) {
    updateSensorData(data);

    // Check thresholds and activate buzzer if needed
    const thresholds = [
      {
        type: "temperature",
        value: data.temperature,
        threshold: deviceThresholds.temperature,
      },
      {
        type: "humidity",
        value: data.humidity,
        threshold: deviceThresholds.humidity,
      },
      { type: "light", value: data.light, threshold: deviceThresholds.light },
      { type: "smoke", value: data.smoke, threshold: deviceThresholds.smoke },
    ];

    thresholds.forEach((item) => {
      if (item.value >= item.threshold) {
        console.warn(
          `Buzzer triggered: ${item.type} exceeds ${item.threshold}`
        );
        activateBuzzer();
      }
    });
  }
});

// Update all sensor data and UI elements
function updateSensorData(data) {
  const stats = [
    { id: "temperature-stat", value: data.temperature },
    { id: "humidity-stat", value: data.humidity },
    { id: "light-stat", value: data.light },
    { id: "smoke-stat", value: data.smoke },
  ];

  stats.forEach((stat) => {
    const display = document.querySelector(`#${stat.id} .value`);
    let unit = "";

    // Determine the unit based on the stat id
    if (stat.id === "temperature-stat") {
      unit = "°C";
    } else if (stat.id === "humidity-stat") {
      unit = "%";
    } else if (stat.id === "light-stat") {
      unit = " %";
    } else if (stat.id === "smoke-stat") {
      unit = " ppm";
    }

    // Update the display with the value and unit
    display.textContent = `${stat.value.toFixed(2)} ${unit}`;
  });

  updateTimestamp(data.timestamp);
}

// Reset sensor display values
function updateSensorDisplays(value) {
  const displays = document.querySelectorAll(".stat-card .value");
  displays.forEach((display) => {
    display.textContent = value;
  });
}

// Update timestamp on all cards
function updateTimestamp(timestamp) {
  const timeDisplays = document.querySelectorAll(".stat-card .timestamp");
  const timeString = new Date(timestamp).toLocaleTimeString();
  timeDisplays.forEach((display) => {
    display.textContent = `Last updated: ${timeString}`;
  });
}

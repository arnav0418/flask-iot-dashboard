const socket = io.connect("ws://127.0.0.1:5001");

// Handle connection
socket.on("connect", () => {
  console.log("Connected to the WebSocket server");
});

// Handle disconnection
socket.on("disconnect", () => {
  console.log("Disconnected from the WebSocket server");
});

// Receive and update sensor data
socket.on("sensor_data", (data) => {
  console.log("Received sensor data:", data);

  // Update the dashboard with real-time data
  document.querySelector(
    ".stat-card:nth-child(1) h2"
  ).textContent = `${data.light}%`;
  document.querySelector(
    ".stat-card:nth-child(2) h2"
  ).textContent = `${data.humidity}%`;
  document.querySelector(
    ".stat-card:nth-child(3) h2"
  ).textContent = `${data.temperature}°C`;
  document.querySelector(
    ".stat-card:nth-child(4) h2"
  ).textContent = `${data.smoke} ppm`;
});

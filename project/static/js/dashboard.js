// Utility: Hide all sections initially
function hideAllSections() {
  const sections = [
    "analytics-section",
    "devices-section",
    "add-device-section",
    "modify-device-section",
    "remove-device-section",
  ];
  sections.forEach((sectionId) => {
    document.getElementById(sectionId).style.display = "none";
  });
}

// Utility: Toggle visibility of a specific section
function toggleSection(sectionId, show) {
  const section = document.getElementById(sectionId);
  section.style.display = show ? "block" : "none";
}

// Show analytics section and hide devices section
function showAnalyticsSection() {
  toggleSection("analytics-section", true);
  toggleSection("devices-section", false);
  isAnalyticsActive = true;
}

// Show devices section and hide analytics section
function showDevicesSection() {
  toggleSection("analytics-section", false);
  toggleSection("devices-section", true);
  isAnalyticsActive = false;
}

// Toggle visibility of device management sections
function toggleDeviceSection(sectionId) {
  const sections = [
    "add-device-section",
    "modify-device-section",
    "remove-device-section",
  ];
  sections.forEach((id) => {
    toggleSection(id, id === sectionId);
  });
}

// Event: Handle DOM content loaded
document.addEventListener("DOMContentLoaded", function () {
  const userEmail = "user@example.com"; // Replace with dynamic user email
  fetchThresholds(userEmail).then(() => {
    hideAllSections(); // Ensure all sections are hidden initially
  });

  // Analytics button click
  document
    .getElementById("analytics-button")
    .addEventListener("click", function () {
      showAnalyticsSection();

      // Request sensor data and start auto-refresh
      if (!refreshInterval) {
        socket.emit("request_sensor_data"); // Initial request
        refreshInterval = setInterval(() => {
          socket.emit("request_sensor_data");
        }, 5000); // Refresh every 5 seconds
      }
    });

  // Devices button click
  document
    .getElementById("devices-button")
    .addEventListener("click", function () {
      showDevicesSection();

      // Stop auto-refresh
      if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
      }
    });

  // Device management buttons
  document
    .getElementById("add-device-button")
    .addEventListener("click", () => toggleDeviceSection("add-device-section"));

  document
    .getElementById("modify-device-button")
    .addEventListener("click", () =>
      toggleDeviceSection("modify-device-section")
    );

  document
    .getElementById("remove-device-button")
    .addEventListener("click", () =>
      toggleDeviceSection("remove-device-section")
    );
});

document.addEventListener("DOMContentLoaded", () => {
  const devicesButton = document.getElementById("devices-button");
  const devicesSection = document.getElementById("devices-section");

  // Device Management Sub-Buttons
  const addDeviceButton = document.getElementById("add-device-button");
  const modifyDeviceButton = document.getElementById("modify-device-button");
  const removeDeviceButton = document.getElementById("remove-device-button");

  // Device Management Sections
  const addDeviceSection = document.getElementById("add-device-section");
  const modifyDeviceSection = document.getElementById("modify-device-section");
  const removeDeviceSection = document.getElementById("remove-device-section");

  // Form Elements
  const addDeviceForm = document.getElementById("add-device-form");
  const modifyDeviceForm = document.getElementById("modify-device-form");
  const removeDeviceForm = document.getElementById("remove-device-form");

  // Device Selects
  const modifyDeviceSelect = document.getElementById("modify_device_id");
  const removeDeviceSelect = document.getElementById("remove_device_id");
  const deviceList = document.getElementById("device-list");

  // Toggle device management subsections
  function toggleDeviceSection(sectionToShow) {
    [addDeviceSection, modifyDeviceSection, removeDeviceSection].forEach(
      (section) => section.classList.add("hidden-section")
    );
    sectionToShow.classList.remove("hidden-section");
  }

  // Event listeners for device management buttons
  addDeviceButton.addEventListener("click", () =>
    toggleDeviceSection(addDeviceSection)
  );
  modifyDeviceButton.addEventListener("click", () => {
    toggleDeviceSection(modifyDeviceSection);
    fetchDevices(modifyDeviceSelect);
  });
  removeDeviceButton.addEventListener("click", () => {
    toggleDeviceSection(removeDeviceSection);
    fetchDevices(removeDeviceSelect);
  });

  // Fetch devices for dropdown
  function fetchDevices(selectElement) {
    fetch("/get_devices")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Clear existing options
          selectElement.innerHTML = '<option value="">Select a device</option>';

          // Populate dropdown
          data.devices.forEach((device) => {
            const option = document.createElement("option");
            option.value = device.id;
            option.textContent = `${device.name} (${device.type})`;
            selectElement.appendChild(option);
          });

          // Update device list display
          updateDeviceListDisplay(data.devices);
        } else {
          window.showToast(data.message, "error");
        }
      })
      .catch((error) => {
        console.error("Error fetching devices:", error);
        window.showToast("Failed to fetch devices", "error");
      });
  }

  // Update device list display
  function updateDeviceListDisplay(devices) {
    deviceList.innerHTML = ""; // Clear existing devices

    devices.forEach((device) => {
      const deviceCard = document.createElement("div");
      deviceCard.classList.add("device-card");
      deviceCard.innerHTML = `
                <h3>${device.name}</h3>
                <p>Type: ${device.type}</p>
            `;
      deviceList.appendChild(deviceCard);
    });
  }

  // Add device form submission
  addDeviceForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(addDeviceForm);

    const success = await fetch("/add_device", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.showToast(data.message, "success");
          addDeviceForm.reset();
          fetchDevices(modifyDeviceSelect);
          fetchDevices(removeDeviceSelect);
          return true;
        } else {
          window.showToast(data.message, "error");
          return false;
        }
      })
      .catch((error) => {
        console.error("Error adding device:", error);
        window.showToast("Failed to add device", "error");
        return false;
      });
  });

  // Modify device form submission
  modifyDeviceForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(modifyDeviceForm);

    await fetch("/modify_device", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.showToast(data.message, "success");
          modifyDeviceForm.reset();
        } else {
          window.showToast(data.message, "error");
        }
      })
      .catch((error) => {
        console.error("Error modifying device:", error);
        window.showToast("Failed to modify device", "error");
      });
  });

  // Remove device form submission
  removeDeviceForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(removeDeviceForm);

    await fetch("/remove_device", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.showToast(data.message, "success");
          removeDeviceForm.reset();
          fetchDevices(modifyDeviceSelect);
          fetchDevices(removeDeviceSelect);
        } else {
          window.showToast(data.message, "error");
        }
      })
      .catch((error) => {
        console.error("Error removing device:", error);
        window.showToast("Failed to remove device", "error");
      });
  });

  // Initial device fetch when page loads
  fetchDevices(modifyDeviceSelect);
  fetchDevices(removeDeviceSelect);
});

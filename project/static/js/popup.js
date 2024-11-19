document.addEventListener("DOMContentLoaded", () => {
  // Create toast container
  const toastContainer = document.createElement("div");
  toastContainer.id = "toast-container";
  toastContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    `;
  document.body.appendChild(toastContainer);

  // Toast function
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.style.cssText = `
            background-color: ${
              type === "success"
                ? "#4CAF50"
                : type === "error"
                ? "#F44336"
                : "#2196F3"
            };
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
        `;

    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Trigger reflow for animation
    toast.offsetHeight;

    // Fade in
    toast.style.opacity = "1";
    toast.style.transform = "translateX(0)";

    // Fade out and remove after 3 seconds
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";

      // Remove from DOM after transition
      setTimeout(() => {
        toastContainer.removeChild(toast);
      }, 300);
    }, 3000);
  }

  // Modify device management functions to use showToast
  function ajaxRequest(url, formData, successMessage) {
    return fetch(url, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast(successMessage, "success");
          return true;
        } else {
          showToast(data.message, "error");
          return false;
        }
      })
      .catch((error) => {
        console.error(`Error: ${url}`, error);
        showToast("Operation failed", "error");
        return false;
      });
  }

  // Attach showToast to window for global access
  window.showToast = showToast;
});

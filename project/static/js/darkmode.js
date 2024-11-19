// DarkMode

document.addEventListener("DOMContentLoaded", () => {
  const themeSelect = document.getElementById("theme");

  const savedTheme = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);

  themeSelect.value = savedTheme;
  themeSelect.addEventListener("change", (e) => {
    const selectedTheme = e.target.value;
    document.documentElement.setAttribute("data-theme", selectedTheme);
    localStorage.setItem("theme", selectedTheme);

    fetch("/update_theme", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ theme: selectedTheme }),
    });
  });
});

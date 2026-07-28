const root = document.documentElement;
const savedTheme = localStorage.getItem("dashboard-theme");

if (savedTheme) {
  root.dataset.theme = savedTheme;
}

document.getElementById("themeToggle")?.addEventListener("click", () => {
  const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
  root.dataset.theme = nextTheme;
  localStorage.setItem("dashboard-theme", nextTheme);
});

document.querySelectorAll("[data-width]").forEach((element) => {
  const width = Number.parseFloat(element.dataset.width || "0");
  const safeWidth = Number.isFinite(width) ? Math.max(0, Math.min(width, 100)) : 0;
  element.style.width = `${safeWidth}%`;
});

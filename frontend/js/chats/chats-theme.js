const themeToggle = document.querySelector(".chats-theme-toggle");

const savedTheme = localStorage.getItem("chats-theme") || "light";

document.documentElement.dataset.theme = savedTheme;
themeToggle.textContent = savedTheme === "dark" ? "☀️" : "🌙";

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.dataset.theme;
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.dataset.theme = newTheme;
    localStorage.setItem("chats-theme", newTheme);

    themeToggle.textContent = newTheme === "dark" ? "☀️" : "🌙";
});
import dom from "./dom.js";

const savedTheme = localStorage.getItem("theme");

if (savedTheme !== null) {
    document.documentElement.dataset.theme = savedTheme;
}

dom.themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.dataset.theme;

    if (currentTheme === "dark") {
        document.documentElement.dataset.theme = "light";
    } else {
        document.documentElement.dataset.theme = "dark";
    }

    localStorage.setItem(
        "theme",
        document.documentElement.dataset.theme
    );
});
// ======================== Theme Toggle ========================
const themeToggle = document.querySelector(".theme-toggle");

const savedTheme = localStorage.getItem("theme");

if (savedTheme !== null) {
    document.documentElement.dataset.theme = savedTheme;
}

// ======================== Refresh Token auth ========================
async function refreshAccessToken() {
    const response = await fetch("/auth/refresh", {
        "method": "POST"
    });

    if (response.status === 200) {
        return response;
    }
    if (response.status === 401) {
        window.location.href = "/welcome/";
        return;
    }

    console.log(`Unexpected Error: ${response.status}`);
}

async function apiFetch(url, options={}) {
    const response = await fetch(url, options);

    if (response.status === 401) {
        const refreshResponse = await refreshAccessToken();
        
        if (refreshResponse.status == 200) {
            return await fetch(url, options);
        } else {
            window.location.href = "/welcome/";
            return;
        }
    }

    if (response.ok) {
        return response;
    }
}

export {
    apiFetch
};
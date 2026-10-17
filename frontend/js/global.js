// ======================== Theme Toggle ========================
const themeToggle = document.querySelector(".theme-toggle");

const savedTheme = localStorage.getItem("theme");

if (savedTheme !== null) {
    document.documentElement.dataset.theme = savedTheme;
}

// ======================== Refresh Token auth ========================
async function refreshAccessToken() {
    const response = await fetch("/auth/refresh/", {
        "method": "POST"
    });

    return response;
}

async function apiFetch(url, options={}) {
    const response = await fetch(url, options);

    if (response.status !== 401) {
        return response;
    }

    const refreshResponse = await refreshAccessToken();

    if (refreshResponse.status === 200) {
        return await fetch(url, options);
    }
    if (refreshResponse.status === 401) {
        window.location.href = "/welcome/";
        return refreshResponse;
    }

    return refreshResponse;
}


let currentUserId = null;

async function getCurrentUserId() {
    const response = await apiFetch("/api/users/me/");
    const user = await response.json();

    currentUserId = user.user_id;
}

export {
    apiFetch,
    getCurrentUserId,
    currentUserId
};

import dom from "./dom.js";
import { loginTimer, showMessage, hideMessage } from "./forms.js";

function getLoginFormData() {
    const formData = new FormData(dom.loginForm);

    return {
        "email": formData.get("email"),
        "password": formData.get("password")
    }
}

async function loginUser(user) {
    const response = await fetch("/login/", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(user)
    })

    return response;
}

async function handleLoginResponse(response) {
    const data = await response.json();

    if (response.status === 200) {
        window.location.href = "/chats/";
        return
    }

    if (response.status === 401) {
        hideMessage(dom.loginMessage, loginTimer);

        dom.loginMessageText.textContent = data.detail.message;
        showMessage(dom.loginMessage, 4000, loginTimer);
        return;
    }

    hideMessage(dom.loginMessage, loginTimer);
    dom.loginMessageText.textContent = "Unexpected Error. Please Try again later";
    showMessage(dom.loginMessage, 4000, loginTimer);
}

let isLoginSubmitting = false;

async function submitLoginUser(event) {
    event.preventDefault();

    if (isLoginSubmitting) {
        return;
    }

    isLoginSubmitting = true;

    try {
        const user = getLoginFormData();
        const response = await loginUser(user);
    
        await handleLoginResponse(response);
    } finally {
        isLoginSubmitting = false;
    }
}

dom.loginForm.addEventListener("submit", submitLoginUser);
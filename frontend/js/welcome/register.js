import dom from "./dom.js";
import { showLogin, showMessage, hideMessage, loginTimer, registerTimer } from "./forms.js";

function getRegisterFormData() {
    const formData = new FormData(dom.registerForm);

    return {
        "username": formData.get("username"),
        "email": formData.get("email"),
        "password": formData.get("password")
    };
}

async function registerUser(user) {
    const response = await fetch("/register/", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(user)
    });

    return response;
}

async function handleRegisterResponse(response, event) {
    const data = await response.json();

    if (response.status === 200) {
        showLogin(event=event);
        hideMessage(dom.loginMessage, loginTimer);

        dom.loginMessageText.textContent = "Account registered successfully. Please Log in";
        showMessage(dom.loginMessage, 4000, loginTimer);
        return;
    }
    
    if (response.status === 409) {
        hideMessage(dom.registerMessage, registerTimer);

        dom.registerMessageText.textContent = data.detail.message;
        showMessage(dom.registerMessage, 4000, registerTimer);
        return;
    }

    hideMessage(dom.registerMessage, registerTimer);

    dom.registerMessageText.textContent = "Unexpected Error. Please try again later."
    showMessage(dom.registerMessage, 4000, registerTimer);
}

let isRegisterSubmitting = false;

async function submitRegisterUser(event) {
    event.preventDefault();

    if (isRegisterSubmitting) {
        return;
    }

    isRegisterSubmitting = true;

    try {
        const user = getRegisterFormData();
        const response = await registerUser(user);
    
        await handleRegisterResponse(response, event);
    } finally {
        isRegisterSubmitting = false;
    }
}

dom.registerForm.addEventListener("submit", submitRegisterUser);
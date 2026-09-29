import dom from "./dom.js";

const loginTimer = {id: null};
const registerTimer = {id: null};

// =========================== Toggle Forms ===========================
function showRegister(event) {
    event.preventDefault();

    dom.loginForm.hidden = true;
    dom.registerForm.hidden = false;

    dom.loginForm.reset();

    hideMessage(dom.loginMessage, loginTimer);
    hideMessage(dom.registerMessage, registerTimer);
}

function showLogin(event) {
    event.preventDefault();

    dom.loginForm.hidden = false;
    dom.registerForm.hidden = true;

    dom.registerForm.reset();

    hideMessage(dom.loginMessage, loginTimer);
    hideMessage(dom.registerMessage, registerTimer);
}

dom.signInLink.addEventListener("click", showLogin);
dom.signUpLink.addEventListener("click", showRegister);

function hideMessage(messageElement, timer) {
    if (timer.id !== null) {
        clearTimeout(timer.id);
        timer.id = null;
    }

    messageElement.classList.remove("is-visible");
}

function showMessage(messageElement, duration, timer) {
    if (timer.id !== null) {
        clearTimeout(timer.id);
    }

    messageElement.classList.add("is-visible");

    timer.id = setTimeout(() => {
        messageElement.classList.remove("is-visible");
        timer.id = null;
    }, duration);
}


export {
    showLogin,
    showMessage,
    hideMessage,
    loginTimer,
    registerTimer
};
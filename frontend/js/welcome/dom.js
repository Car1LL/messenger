const dom = {
    loginForm: document.querySelector(".login-form"),
    registerForm: document.querySelector(".register-form"),
    signInLink: document.querySelector(".register-form a"),
    signUpLink: document.querySelector(".login-form a"),
    registerPasswordInput: document.querySelector("#register-password"),
    passwordHints: document.querySelector(".password-hints"),
    requirementLength: document.querySelector(".requirement-length"),
    requirementUppercase: document.querySelector(".requirement-uppercase"),
    requirementLowercase: document.querySelector(".requirement-lowercase"),
    requirementDigit: document.querySelector(".requirement-digit"),
    registerInputs: document.querySelectorAll(".register-form input"),
    registerPasswordConfirmInput: document.querySelector("#confirm-register-password"),
    passwordInputs: document.querySelectorAll(".password-wrapper > input"),
    registerUsername: document.querySelector("#register-username"),
    usernameHints: document.querySelector(".username-hints"),
    requirementUsernameLength: document.querySelector(".username-requirement-length"),
    requirementUsernameCharacters: document.querySelector(".username-requirement-characters"),
    requirementUsernameLetters: document.querySelector(".username-requirement-letters"),
    usernameAvailability: document.querySelector(".username-availability"),
    loginMessage: document.querySelector(".login-message"),
    loginMessageText: document.querySelector(".login-message-content p"),
    registerMessage: document.querySelector(".register-message"),
    registerMessageText: document.querySelector(".register-message-content p"),
    themeToggle: document.querySelector(".theme-toggle")
};

export default dom;
import dom from "./dom.js"


// ==================================== Password Hints ====================================
function updateRequirement(element, isValid) {
    if (isValid) {
        element.textContent = element.textContent.replace("❌", "✅");
        element.classList.add("valid");
        element.classList.remove("invalid");
    } else {
        element.textContent = element.textContent.replace("✅", "❌");
        element.classList.add("invalid");
        element.classList.remove("valid");
    }
}

function updatePasswordHint(event) {
    const value = event.target.value;

    const isLengthValid = value.length >= 8 && value.length <= 32;
    const hasUppercase = /[A-Z]/.test(value);
    const hasLowercase = /[a-z]/.test(value);
    const hasDigit = /\d/.test(value);

    updateRequirement(dom.requirementLength, isLengthValid);
    updateRequirement(dom.requirementUppercase, hasUppercase);
    updateRequirement(dom.requirementLowercase, hasLowercase);
    updateRequirement(dom.requirementDigit, hasDigit);

    const isValidPassword =
        isLengthValid &&
        hasUppercase &&
        hasLowercase &&
        hasDigit;

    if (isValidPassword) {
        dom.passwordHints.classList.remove("is-visible");
    } else {
        dom.passwordHints.classList.add("is-visible");
    }
}

dom.registerPasswordInput.addEventListener("focus", (event) => {
    updatePasswordHint(event);
    dom.passwordHints.classList.add("is-visible");
});

dom.registerPasswordInput.addEventListener("input", updatePasswordHint);

dom.registerInputs.forEach((input) => {
    input.addEventListener("focus", (event) => {
        if (event.target !== dom.registerPasswordInput) {
            dom.passwordHints.classList.remove("is-visible");   
        }
    });
});

// ======================== Password match (Confirm passwords) =================

function checkPassword() {
    dom.registerPasswordInput.classList.remove(
        "password-match",
        "password-mismatch"
    );

    dom.registerPasswordConfirmInput.classList.remove(
        "password-match",
        "password-mismatch"
    );

    if (!dom.registerPasswordConfirmInput.value) {
        dom.registerPasswordConfirmInput.setCustomValidity(""); 
        return;
    };

    if (dom.registerPasswordConfirmInput.value === dom.registerPasswordInput.value) {
        dom.registerPasswordInput.classList.add("password-match");
        dom.registerPasswordConfirmInput.classList.add("password-match");

        dom.registerPasswordConfirmInput.setCustomValidity("");
    } else {
        dom.registerPasswordInput.classList.add("password-mismatch");
        dom.registerPasswordConfirmInput.classList.add("password-mismatch");

        dom.registerPasswordConfirmInput.setCustomValidity("Passwords do not match");
    }
}

dom.registerPasswordInput.addEventListener("input", checkPassword);
dom.registerPasswordConfirmInput.addEventListener("input", checkPassword);

// ======================== Password Toggle (Password show) ========================
dom.passwordInputs.forEach((input) => {
    const button = input.parentElement.querySelector("button");

    button.addEventListener("pointerdown", () => {
        input.type = "text";
    });

    button.addEventListener("pointerup", () => {
        input.type = "password";
    });

    button.addEventListener("pointerleave", () => {
        input.type = "password";
    });
});

// dom.passwordInputs.forEach((input) => {
//     const checkBox = input.parentElement.querySelector('input[type="checkbox"]');

//     checkBox.addEventListener("change", () => {
//         input.type = checkBox.checked ? "text": "password";
//     });
// })
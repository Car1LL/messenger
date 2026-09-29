import dom from "./dom.js"

// ========================= Validate Username =========================
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


function validateUsername(value) {
    const isValidLength = value.length >= 3 && value.length <= 20;
    const hasValidCharacters = /^[a-zA-Z0-9_]+$/.test(value);
    const hasMinimumLetters = (value.match(/[a-zA-Z]/g) || []).length >= 3;

    return {
        isValidLength,
        hasValidCharacters,
        hasMinimumLetters,
        isValid: 
            isValidLength &&
            hasValidCharacters &&
            hasMinimumLetters
    };
}

function updateUsernameHint(event) {
    const value = event.target.value;
    const result = validateUsername(value);

    updateRequirement(dom.requirementUsernameLength, result.isValidLength);
    updateRequirement(dom.requirementUsernameCharacters, result.hasValidCharacters);
    updateRequirement(dom.requirementUsernameLetters, result.hasMinimumLetters);
    
    if (result.isValid) {
        dom.usernameHints.classList.remove("is-visible")
    } else {
        dom.usernameHints.classList.add("is-visible")
    }
}

dom.registerUsername.addEventListener("focus", (event) => {
    updateUsernameHint(event);
    dom.usernameHints.classList.add("is-visible");
});

dom.registerUsername.addEventListener("input", updateUsernameHint);

dom.registerInputs.forEach((input) => {
    input.addEventListener("focus", (event) => {
        if (event.target !== dom.registerUsername) {
            dom.usernameHints.classList.remove("is-visible");
        }
    });
}); 

// ====================== Username Availability (fetch) ======================
function setUsernameState(state) {
    dom.registerUsername.classList.remove(
        "checking",
        "available",
        "taken"
    );

    if (state) {
        dom.registerUsername.classList.add(state);
    }
}

async function checkUsernameAvailability(username) {
    const response = await fetch(
        `/check-username/?username=${username}`
    );

    const data = await response.json();
    return data;
}

let usernameTimeout;

function debounceUsernameCheck(username) {
    clearTimeout(usernameTimeout);

    setUsernameState("checking");

    usernameTimeout = setTimeout(async () => {
        const data = await checkUsernameAvailability(username);

        if (data.available) {
            setUsernameState("available");
            dom.usernameAvailability.classList.remove("is-visible");
        } else {
            setUsernameState("taken");
            dom.usernameAvailability.classList.add("is-visible");
        }
    }, 500);
}

dom.registerUsername.addEventListener("input", (event) => {
    const username = event.target.value;
    const result = validateUsername(username);

    if (!result.isValid) {
        clearTimeout(usernameTimeout);
        setUsernameState(null);
        return;
    }

    debounceUsernameCheck(username);
});
import { apiFetch } from "../global.js";
import dom from "./dom.js";
import { openChat } from "./chat-navigation.js";

function createSearchElement(user) {
    const searchElement = document.createElement("div");
    const username = document.createElement("span");
    const userAvatar = document.createElement("img");

    userAvatar.src = user.avatar_path;
    username.textContent = user.username;

    searchElement.classList.add("search-element");
    username.classList.add("search-results-username");
    userAvatar.classList.add("search-results-avatar");

    searchElement.append(userAvatar, username);
    dom.searchResults.append(searchElement);

    searchElement.addEventListener("click", () => handleSearchClick(user));
}

async function handleSearchClick(user) {
    try {
        const response = await apiFetch(`/api/chats/?target_user_id=${user.user_id}`, {
            method: "POST"
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.message || "Failed to open chat");
        }

        const data = await response.json();

        const chat = {
            chat_id: data.chat_id,
            recipient_avatar_path: user.avatar_path,
            recipient_username: user.username
        };

        openChat(chat);

    } catch (error) {
        console.error("Failed to open chat:", error);
    }
}

// 

let searchTimeout;

function handleSearchInput(event) {
    dom.searchResults.replaceChildren();
    clearTimeout(searchTimeout);

    const username = event.target.value.trim();

    if (!username) {
        dom.searchResults.hidden = true;
        dom.chatList.hidden = false;
        return;
    }

    dom.searchResults.hidden = false;
    dom.chatList.hidden = true;


    searchTimeout = setTimeout(async () => {
        const userData = await searchUser(username);
        const currentUsername = dom.sidebarSearch.value.trim();

        if (username !== currentUsername) {
            return;
        }

        if (userData === null) {
            return;
        }
        createSearchElement(userData);
    }, 500)

    return;
}   

async function searchUser(username) {
    const encodedUsername = encodeURIComponent(username);
    const response = await apiFetch(`/api/users/search/?username=${encodedUsername}`);

    if (response.status !== 200) {
        return null;
    }

    return await response.json();   
}

dom.sidebarSearch.addEventListener("input", handleSearchInput);

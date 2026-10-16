import { apiFetch } from "../global.js";
import dom from "./dom.js";

// dom.sidebarSearch.addEventListener("input", async (event) => {
//     dom.searchResults.replaceChildren();

//     const username = encodeURIComponent(event.target.value.trim());

//     if (!username) {
//         dom.searchResults.hidden = true;
//         dom.chatList.hidden = false;
//         dom.searchResults.replaceChildren();
//         return;
//     }

//     dom.chatList.hidden = true;
//     dom.searchResults.hidden = false;
//     dom.searchResults.replaceChildren();

//     const response = await apiFetch(`/api/users/search/?username=${username}`);

//     if (response.status !== 200) {
//         return response;
//     }
//     const user = await response.json();
//     createSearchElement(user);

//     console.log(response);
// });

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

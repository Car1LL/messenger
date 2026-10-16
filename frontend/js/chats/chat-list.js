import dom from "./dom.js";
import { apiFetch } from "../global.js";


async function getChats() {
    const response = await apiFetch("/api/chats/");
    const chats = await response.json();

    if (chats.length === 0) {
        // Message for empty chats array
        dom.chatList.classList.add("empty");

        const emptyMessage = document.createElement("span");
        emptyMessage.classList.add("empty-chats");
        emptyMessage.textContent = "No Chats yet";

        dom.chatList.append(emptyMessage);
        return;
    }

    for (const chat of chats) {
        const chatElement = createChatElement(chat);
        dom.chatList.append(chatElement);
    }
}

function createChatElement(chat) {

    // Create main div container where chat info will be stored
    const chatElement = document.createElement("div");
    const chatInfo = document.createElement("div");
    const chatHeader = document.createElement("div");
    
    const recipientAvatarPath = document.createElement("img");
    recipientAvatarPath.draggable = false;

    const recipientUsername = document.createElement("span");
    const latestMessageAt = document.createElement("div");
    const latestMessageContent = document.createElement("div");

    // Create DOM
    chatElement.append(recipientAvatarPath);
    chatElement.append(chatInfo);

    chatInfo.append(chatHeader);
    chatInfo.append(latestMessageContent);

    chatHeader.append(recipientUsername);
    chatHeader.append(latestMessageAt);

    // Add class names for each element
    chatElement.classList.add("chat-element");
    chatInfo.classList.add("chat-info");
    chatHeader.classList.add("chat-header");
    recipientAvatarPath.classList.add("recipient-avatar-path");
    recipientUsername.classList.add("recipient-username");
    latestMessageAt.classList.add("latest-message-at");
    latestMessageContent.classList.add("latest-message-content");

    // Fill elements with chat data
    recipientAvatarPath.src = chat.recipient_avatar_path;
    recipientUsername.textContent = chat.recipient_username;
    latestMessageContent.textContent = chat.latest_message_content;
    latestMessageAt.textContent = formatChatDate(chat.latest_message_at);

    return chatElement;
}

function formatChatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();

    const todayStart = new Date(now);
    todayStart.setHours(0, 0, 0, 0);
    
    const weekStart = new Date(todayStart);
    weekStart.setDate(weekStart.getDate() - 7);

    if (date >= todayStart) {
        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    if (date >= weekStart) {
        return date.toLocaleDateString([], {
            weekday: "short"
        });
    }

    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString([], {
            day: "2-digit",
            month: "short"
        });
    }

    return date.toLocaleDateString([], {
        year: "numeric",
        month: "short"
    });
}

await getChats();


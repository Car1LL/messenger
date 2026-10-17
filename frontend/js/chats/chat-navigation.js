import dom from "./dom.js";
import { apiFetch, currentUserId } from "../global.js";

let oldestMessageId = null;
let hasMoreMessages = true;
let isLoadingMessages = false;
let loadedMessages = [];
let activeChatId = null;


// Open chat
export function openChat(chat) {
    activeChatId = chat.chat_id;

    dom.chatPlaceholder.hidden = true;
    dom.chatInterface.hidden = false;

    dom.chatAvatar.src = chat.recipient_avatar_path;
    dom.chatUsername.textContent = chat.recipient_username;

    loadMessages(chat.chat_id);
}


// Load the latest 50 messages
async function loadMessages(chatId) {
    oldestMessageId = null;
    hasMoreMessages = true;
    isLoadingMessages = false;
    loadedMessages = [];

    dom.messagesList.replaceChildren();

    try {
        const response = await apiFetch(
            `/api/chats/${chatId}/messages`
        );

        if (!response.ok) {
            throw new Error("Failed to load messages");
        }

        const messages = await response.json();

        // Ignore the response if another chat was opened
        if (chatId !== activeChatId) {
            return;
        }

        loadedMessages = messages;

        if (messages.length > 0) {
            oldestMessageId = messages[0].message_id;
        }

        hasMoreMessages = messages.length === 50;

        renderAllMessages();

        // Scroll to the latest message
        dom.messagesContainer.scrollTop =
            dom.messagesContainer.scrollHeight;

    } catch (error) {
        console.error(error);
    }
}


// Load older messages when scrolling up
async function loadOlderMessages(chatId) {
    if (
        isLoadingMessages ||
        !hasMoreMessages ||
        oldestMessageId === null ||
        chatId !== activeChatId
    ) {
        return;
    }

    isLoadingMessages = true;

    const previousScrollHeight =
        dom.messagesContainer.scrollHeight;

    const previousScrollTop =
        dom.messagesContainer.scrollTop;

    try {
        const response = await apiFetch(
            `/api/chats/${chatId}/messages?before_id=${oldestMessageId}`
        );

        if (!response.ok) {
            throw new Error("Failed to load older messages");
        }

        const messages = await response.json();

        // Ignore the response if another chat was opened
        if (chatId !== activeChatId) {
            return;
        }

        if (messages.length === 0) {
            hasMoreMessages = false;
            return;
        }

        // Add older messages before the currently loaded messages
        loadedMessages = [
            ...messages,
            ...loadedMessages
        ];

        oldestMessageId = messages[0].message_id;
        hasMoreMessages = messages.length === 50;

        renderAllMessages();

        // Preserve the user's scroll position
        const newScrollHeight =
            dom.messagesContainer.scrollHeight;

        dom.messagesContainer.scrollTop =
            previousScrollTop +
            newScrollHeight -
            previousScrollHeight;

    } catch (error) {
        console.error(error);
    } finally {
        // Don't modify the loading state of another chat
        if (chatId === activeChatId) {
            isLoadingMessages = false;
        }
    }
}


// Render a single message
function renderMessage(message) {
    const messageElement = document.createElement("div");
    const messageContent = document.createElement("div");
    const messageTime = document.createElement("span");

    messageElement.classList.add("message");
    messageContent.classList.add("message-content");
    messageTime.classList.add("message-time");

    if (message.sender_id === currentUserId) {
        messageElement.classList.add("sent");
    } else {
        messageElement.classList.add("received");
    }

    messageContent.textContent = message.content;
    messageTime.textContent = formatMessageTime(message.created_at);

    messageElement.append(
        messageContent,
        messageTime
    );

    return messageElement;
}


// Render all loaded messages with date separators
function renderAllMessages() {
    dom.messagesList.replaceChildren();

    let previousDate = null;

    for (const message of loadedMessages) {
        const messageDate =
            new Date(message.created_at).toDateString();

        if (messageDate !== previousDate) {
            const dateElement = document.createElement("div");

            dateElement.classList.add("message-date");
            dateElement.textContent =
                formatMessageDate(message.created_at);

            dom.messagesList.append(dateElement);

            previousDate = messageDate;
        }

        dom.messagesList.append(
            renderMessage(message)
        );
    }
}


// Format message time
function formatMessageTime(timestamp) {
    const date = new Date(timestamp);

    return date.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit"
    });
}


// Format message date
function formatMessageDate(timestamp) {
    const date = new Date(timestamp);

    const today = new Date();
    const yesterday = new Date();

    today.setHours(0, 0, 0, 0);
    yesterday.setHours(0, 0, 0, 0);

    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
        return "Today";
    }

    if (date.toDateString() === yesterday.toDateString()) {
        return "Yesterday";
    }

    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = String(date.getFullYear()).slice(-2);

    return `${day}.${month}.${year}`;
}


// Load older messages when the user scrolls to the top
dom.messagesContainer.addEventListener("scroll", () => {
    console.log("Scroll position:", dom.messagesContainer.scrollTop);

    if (
        dom.messagesContainer.scrollTop <= 100 &&
        activeChatId !== null
    ) {
        console.log("Loading older messages...");
        loadOlderMessages(activeChatId);
    }
});
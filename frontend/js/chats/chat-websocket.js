const socket = new WebSocket("ws://127.0.0.1:8000/chats/ws/");

let messageHandler = null;

socket.addEventListener("open", () => {
    console.log("WebSocket connected!");
});

socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);

    if (data.error) {
        console.error("WebSocket server error:", data);
        return;
    }

    if (data.type === "message" && messageHandler) {
        messageHandler(data);
    }
});

socket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
});

socket.addEventListener("close", (event) => {
    console.log("WebSocket disconnected:", event.code);
});

export function sendMessage(chatId, content) {
    if (socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not connected");
        return false;
    }

    socket.send(JSON.stringify({
        chat_id: chatId,
        content: content
    }));

    return true;
}

export function setMessageHandler(handler) {
    messageHandler = handler;
}
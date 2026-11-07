import { apiFetch, getCurrentUserId, currentUserId } from "../global.js";

await getCurrentUserId();

import "./chat-list.js";
import "./search-username.js";
import "./chat-navigation.js";
import "./chat-websocket.js";
import "./chats-theme.js";


const response = await apiFetch("/api/chats/");

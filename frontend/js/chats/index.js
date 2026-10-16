import { apiFetch } from "../global.js";

import "./chat-list.js";
import "./search-username.js";

const response = await apiFetch("/api/chats/");
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = dict()

    async def connect(self, user_id: int, websocket: WebSocket):
        self.connections.setdefault(user_id, set()).add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)

            if not self.connections[user_id]:
                self.connections.pop(user_id)

    async def send_to_user(self, user_id: int, message: str):
        for ws in self.connections[user_id]:
            await ws.send_text(message)

connection_manager = ConnectionManager()
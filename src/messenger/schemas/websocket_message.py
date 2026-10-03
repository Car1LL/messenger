from pydantic import BaseModel, Field

class WebsocketMessage(BaseModel):
    chat_id: int
    content: str = Field(max_length=512)
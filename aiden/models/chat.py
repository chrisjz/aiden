from typing import Literal
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["system", "user", "agent"]
    content: str


class ChatMessage(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = True

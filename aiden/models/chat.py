from typing import Literal, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class Options(BaseModel):
    frequency_penalty: float = 1.0
    penalize_newline: bool = True
    presence_penalty: float = 1.5
    repeat_last_n: int = 64
    repeat_penalty: float = 1.1
    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.9


class ChatMessage(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = True
    options: Optional[Options] = {}

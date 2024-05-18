import json

from pydantic import parse_obj_as

from aiden.app.redis_client import redis_client
from aiden.models.chat import Message


def save_memory(session_id: str, messages: list[Message]):
    """
    Save chat history representing short-term memory to Redis.

    Args:
        session_id (str): Unique identifier for the chat session.
        messages (List[Message]): List of Message models to save.
    """
    key = f"memory:{session_id}"
    messages_json = json.dumps([message.model_dump() for message in messages])
    redis_client.set(key, messages_json)
    redis_client.expire(key, 86400)  # Expires in 1 day


def get_memory(session_id: str) -> list[Message]:
    """
    Retrieve chat history representing short-term memory from Redis.

    Args:
        session_id (str): Unique identifier for the chat session.

    Returns:
        List[Message]: A list of Message models.
    """
    key = f"memory:{session_id}"
    history_json = redis_client.get(key)
    if history_json:
        history_data = json.loads(history_json)
        # TODO: Create a ListMessage model then replace `parse_obj_as` with MessageList.validate_python
        return parse_obj_as(list[Message], history_data)
    else:
        return []

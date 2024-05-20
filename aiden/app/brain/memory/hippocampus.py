import json

from pydantic import parse_obj_as

from aiden.app.redis_client import redis_client
from aiden.models.chat import Message


def _get_memory_key(agent_id: str) -> str:
    """Fixed memory key"""
    key = f"agent:{agent_id}:memory"
    return key


def update_memory(agent_id: str, messages: list[Message]):
    """
    Save chat history representing short-term memory to Redis.

    Args:
        agent_id (str): Unique identifier for the AI agent.
        messages (List[Message]): List of Message models to save.
    """
    key = _get_memory_key(agent_id)
    messages_json = json.dumps([message.model_dump() for message in messages])
    redis_client.set(key, messages_json)
    redis_client.expire(key, 86400)  # Expires in 1 day


def read_memory(agent_id: str) -> list[Message]:
    """
    Retrieve chat history representing short-term memory from Redis.

    Args:
        agent_id (str): Unique identifier for the AI agent.

    Returns:
        List[Message]: A list of Message models.
    """
    key = _get_memory_key(agent_id)
    history_json = redis_client.get(key)
    if history_json:
        history_data = json.loads(history_json)
        # TODO: Create a ListMessage model then replace `parse_obj_as` with MessageList.validate_python
        return parse_obj_as(list[Message], history_data)
    else:
        return []


def wipe_memory(agent_id: str) -> None:
    """
    Delete the agent's entire short-term memory in Redis

    Args:
        agent_id (str): Unique identifier for the AI agent.
    """
    key = _get_memory_key(agent_id)
    redis_client.delete(key)

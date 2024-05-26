from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_CHAT
from aiden.models.chat import ChatMessage


import httpx


import json


async def process_subconscious(chat_message: ChatMessage) -> str:
    """
    Process the thoughts from the subconscious areas of the AI model and return them as a string.

    Args:
        chat_message (ChatMessage): The message to be processed.

    Returns:
        str: The processed thoughts as a string. If processing fails, returns an empty string.
    """
    logger.info(
        f"Subconcious chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL_CHAT, json=chat_message.model_dump(), timeout=60.0
        )
        if response.status_code == 200:
            thoughts = response.json().get("message", {}).get("content", "").strip()
            logger.info(f"Thoughts: {thoughts}")
            return thoughts
        else:
            logger.error(
                f"Failed thoughts processing with status: {response.status_code}"
            )
            return ""

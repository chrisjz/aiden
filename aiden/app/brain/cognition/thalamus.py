from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL
from aiden.models.brain import BrainConfig
from aiden.models.chat import ChatMessage, Message, Options


import httpx


import json
import os


async def process_thalamus(sensory_input: str, brain_config: BrainConfig) -> str:
    """
    Simulates the thalamic process of restructuring sensory input.

    Args:
        sensory_input (str): The initial sensory data.
        brain_config (BrainConfig): Configuration of the brain.

    Returns:
        str: The rewritten sensory prompt or the original if the request fails.
    """
    instruction = "\n".join(brain_config.regions.thalamus.instruction)
    messages = [
        Message(role="system", content=instruction),
        Message(role="user", content=sensory_input),
    ]
    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(
            frequency_penalty=1.2,
            penalize_newline=False,
            presence_penalty=1.0,
            repeat_last_n=32,
            repeat_penalty=1.0,
            temperature=0.7,
            top_k=40,
            top_p=0.9,
        ),
    )

    logger.info(
        f"Thalamus chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            integrated_sensory_input = (
                response.json().get("message", {}).get("content", sensory_input)
            )
            logger.info(f"Restructured sensory input: {integrated_sensory_input}")
            return integrated_sensory_input
        else:
            logger.error(
                f"Failed restructuring sensory input with status: {response.status_code}"
            )
            return sensory_input

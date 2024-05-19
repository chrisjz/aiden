from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL
from aiden.models.brain import BrainConfig, SimpleAction
from aiden.models.chat import ChatMessage, Message, Options


import httpx


import json
import os


async def _map_decision_to_action(decision: str) -> str:
    """
    Maps a textual decision into a defined action based on predefined actions in SimpleAction.

    Args:
        decision (str): The decision text to map.

    Returns:
        str: The corresponding action from SimpleAction.
    """
    decision_formatted = decision.lower().replace(" ", "_").replace("-", "_")
    for action in SimpleAction:
        if action.value in decision_formatted or decision_formatted in action.value:
            return action.value
    return SimpleAction.NONE.value


async def process_prefrontal(sensory_input: str, brain_config: BrainConfig) -> str:
    """
    Simulates the prefrontal cortex decision-making based on sensory input.

    Args:
        sensory_input (str): Processed sensory input.
        brain_config (BrainConfig): Configuration of the brain.

    Returns:
        str: The decision on the next action.
    """
    instruction = "\n".join(brain_config.regions.prefrontal.instruction)
    decision_prompt = f"{sensory_input}\nYour action decision:"
    messages = [
        Message(role="system", content=instruction),
        Message(role="user", content=decision_prompt),
    ]
    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(
            frequency_penalty=1.0,
            presence_penalty=0.6,
            temperature=0.6,
            top_p=0.95,
            max_tokens=80,
        ),
    )

    logger.info(
        f"Prefrontal chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            decision = (
                response.json()
                .get("message", {})
                .get("content", SimpleAction.NONE.value)
                .strip()
            )
            logger.info(f"Prefrontal decision: {decision}")
            mapped_action = await _map_decision_to_action(decision)
            logger.info(f"Mapped action: {mapped_action}")
            return mapped_action
        else:
            logger.error(f"Failed decision-making with status: {response.status_code}")
            return SimpleAction.NONE.value

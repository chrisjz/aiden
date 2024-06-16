import os

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import BrainConfig, SimpleAction


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
        SystemMessage(content=instruction),
        HumanMessage(content=decision_prompt),
    ]

    llm = ChatOllama(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        timeout=30.0,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        temperature=0.6,
        top_p=0.95,
        max_tokens=80,
    )

    logger.info(f"Prefrontal chat message: {messages}")

    response: AIMessage = llm.invoke(messages)
    try:
        logger.info(f"Prefrontal decision: {response.content}")

        mapped_action = await _map_decision_to_action(response.content)
        logger.info(f"Mapped action: {mapped_action}")
        return mapped_action
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return SimpleAction.NONE.value

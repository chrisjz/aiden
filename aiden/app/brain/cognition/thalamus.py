import os

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import BrainConfig


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

    messages = [SystemMessage(content=instruction), HumanMessage(content=sensory_input)]

    llm = ChatOllama(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "mistral"),
        timeout=30.0,
        frequency_penalty=1.2,
        penalize_newline=False,
        presence_penalty=1.0,
        repeat_last_n=32,
        repeat_penalty=1.0,
        temperature=0.7,
        top_k=40,
        top_p=0.9,
    )

    logger.info(f"Thalamus chat message: {messages}")

    response: AIMessage = llm.invoke(messages)
    try:
        logger.info(f"Restructured sensory input: {response.content}")
        return response.content
    except Exception as exc:
        logger.error(f"Failed restructuring sensory input with error: {exc}")
        return sensory_input

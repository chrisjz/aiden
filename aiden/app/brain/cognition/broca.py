import os

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import BrainConfig


async def process_broca(
    sensory_input: str, brain_config: BrainConfig, language_input: str
) -> str:
    """
    Simulates broca's area by processing the integrated sensory input and auditory
    language input to produce a directly spoken response from the AI.

    Args:
        sensory_input (str): Processed sensory input that includes all sensory data.
        brain_config (BrainConfig): Configuration for the brain, used to guide the response.
        language_input (str): The spoken language input that the AI needs to respond to.

    Returns:
        str: The AI's spoken response.
    """
    instruction = "\n".join(brain_config.regions.broca.instruction)

    # Combine the sensory input and language input
    combined_input = f"{sensory_input}\n\nSpoken Input: {language_input}"

    messages = [
        SystemMessage(content=instruction),
        HumanMessage(content=combined_input),
    ]

    llm = ChatOllama(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "mistral"),
        timeout=30.0,
        frequency_penalty=1.2,
        presence_penalty=0.6,
        temperature=0.4,
        top_p=0.85,
        max_tokens=150,
    )

    logger.info(f"Broca's area chat message: {messages}")

    response: AIMessage = llm.invoke(messages)
    logger.info(f"Broca's decision: {response.content}")
    return response.content

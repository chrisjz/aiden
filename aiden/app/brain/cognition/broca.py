import os
import re

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import BrainConfig


async def process_broca(sensory_input: str, brain_config: BrainConfig) -> str:
    """
    Process the integrated sensory input dynamically using instructions to decide
    if the AI needs to say something based on its understanding.

    Args:
        integrated_sensory_input (str): Processed sensory input.
        brain_config (BrainConfig): Configuration for the brain, used to guide the response.

    Returns:
        str: The AI's spoken response or an empty string if there is nothing to say.
    """
    instruction = "\n".join(brain_config.regions.broca.instruction)

    messages = [SystemMessage(content=instruction), HumanMessage(content=sensory_input)]

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
    try:
        logger.info(f"Broca's raw decision: {response.content}")

        # Extract the response within double quotes
        match = re.search(r'"([^"]*)"', response.content)
        if match:
            final_response = match.group(1)
            logger.info(f"Extracted verbal response: {final_response}")
            return final_response
        else:
            return ""
    except Exception as exc:
        logger.error(f"Failed speech production with error: {exc}")
        return ""

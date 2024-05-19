from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL
from aiden.models.brain import BrainConfig
from aiden.models.chat import ChatMessage, Message, Options


import httpx


import json
import os
import re


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
            presence_penalty=0.6,
            temperature=0.4,
            top_p=0.85,
            max_tokens=150,
        ),
    )

    logger.info(
        f"Broca's area chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            speech_output = (
                response.json().get("message", {}).get("content", "").strip()
            )
            logger.info(f"Broca's raw decision: {speech_output}")

            # Extract the response within double quotes
            match = re.search(r'"([^"]*)"', speech_output)
            if match:
                final_response = match.group(1)
                logger.info(f"Extracted verbal response: {final_response}")
                return final_response
            else:
                return ""
        else:
            logger.error(
                f"Failed speech production with status: {response.status_code}"
            )
            return ""

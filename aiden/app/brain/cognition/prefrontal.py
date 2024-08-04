import json
import os
import re

from langchain_core.messages import AIMessage, HumanMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions, parse_response

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
    decision_formatted = decision.lower().replace("_", " ").replace("-", " ")
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
        HumanMessage(content=decision_prompt),
    ]

    llm = OllamaFunctions(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "mistral"),
        format="json",
        timeout=30.0,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        temperature=0.6,
        top_p=0.95,
        max_tokens=80,
    )

    llm = llm.bind_tools(
        tools=[
            {
                "name": "_map_decision_to_action",
                "description": instruction,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "move forward",
                                "move backward",
                                "turn left",
                                "turn right",
                                "none",
                            ],
                        },
                    },
                    "required": ["action"],
                },
            }
        ],
        function_call={"name": "_map_decision_to_action"},
    )

    logger.info(f"Prefrontal chat message: {messages}")

    try:
        response: AIMessage = llm.invoke(messages)
        response_parsed = parse_response(response)
        logger.info(f"Prefrontal parsed response: {response_parsed}")
        decision = json.loads(response_parsed).get("action", SimpleAction.NONE.value)
        logger.info(f"Prefrontal decision: {decision}")
    except ValueError as exc:
        # Workaround for models that do not fully handle functions e.g. bakllava
        cleaned_exc_message = str(exc).strip()
        match = re.search(r'"action":\s*"([^"]*)"', cleaned_exc_message)
        if match:
            decision = match.group(1)
            logger.info(f"Inferred action from failed function call: {decision}")
        else:
            logger.info("No action found.")
            return SimpleAction.NONE.value
    except Exception as exc:
        logger.warning(
            f"Could not infer action from failed function call with error: {exc}"
        )
        return SimpleAction.NONE.value

    try:
        mapped_action = await _map_decision_to_action(decision)
        logger.info(f"Mapped action: {mapped_action}")
        return mapped_action
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return SimpleAction.NONE.value

import json
import os
import re

from langchain_core.messages import AIMessage, HumanMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions, parse_response

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import BrainConfig, BaseAction


async def _map_decision_to_action(decision: str) -> str:
    """
    Maps a textual decision into a defined action based on predefined actions in SimpleAction.

    Args:
        decision (str): The decision text to map.

    Returns:
        str: The corresponding action from SimpleAction.
    """
    decision_formatted = decision.lower().replace("_", " ").replace("-", " ")
    for action in BaseAction:
        if action.value in decision_formatted or decision_formatted in action.value:
            return action.value
    return BaseAction.NONE.value


async def _extract_interactions(interaction_string: str) -> list[str]:
    """
    Extract a list of interactions from the given interaction string.

    Args:
        interaction_string (str): The interaction string to extract from.

    Returns:
        List[str]: A list of interaction strings.
    """
    static_text = "You can additionally perform the following interactions: "
    start_index = interaction_string.find(static_text)

    if start_index == -1:
        return []

    interactions_part = interaction_string[start_index + len(static_text) :]
    end_index = interactions_part.find(" | ")

    if end_index != -1:
        interactions_part = interactions_part[:end_index].strip()

    if not interactions_part or not (
        "'" in interactions_part and "''" not in interactions_part
    ):
        return []

    interactions = interactions_part.strip(" '").split("', '")
    return interactions


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

    actions_available = [e.value for e in BaseAction]
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
                            "enum": actions_available,
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
        decision = json.loads(response_parsed).get("action", BaseAction.NONE.value)
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
            return BaseAction.NONE.value
    except Exception as exc:
        logger.warning(
            f"Could not infer action from failed function call with error: {exc}"
        )
        return BaseAction.NONE.value

    try:
        mapped_action = await _map_decision_to_action(decision)
        logger.info(f"Mapped action: {mapped_action}")
        return mapped_action
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return BaseAction.NONE.value

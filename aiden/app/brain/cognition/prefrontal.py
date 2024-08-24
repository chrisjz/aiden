import json
import os
import re

from langchain_core.messages import AIMessage, HumanMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions, parse_response

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import ACTION_NONE, Action, BrainConfig


async def _map_decision_to_action(decision: str, actions: list[str] = []) -> str:
    """
    Maps a textual decision into a defined action based on predefined actions.

    Args:
        decision (str): The decision text to map.
        actions: List of actions available to decide upon. Defaults to no action.

    Returns:
        str: The corresponding action.
    """
    decision_formatted = decision.lower().replace("_", " ").replace("-", " ")
    for action in actions:
        if action in decision_formatted or decision_formatted in action:
            return action
    return ACTION_NONE


async def process_prefrontal(
    sensory_input: str,
    brain_config: BrainConfig,
    actions: list[Action] = [],
) -> str | None:
    """
    Simulates the prefrontal cortex decision-making based on sensory input.

    Args:
        sensory_input (str): Processed sensory input.
        brain_config (BrainConfig): Configuration of the brain.
        actions (list[Action]): List of actions available to decide upon. Defaults to no actions.

    Returns:
        str | None: The decision on the next action, or None if no action decided.
    """
    # Skip decision-making if no actions available
    if actions == []:
        return None

    action_names = [action.name for action in actions]

    # Ensure an action to do nothing is available
    if ACTION_NONE not in action_names:
        action_names.append(ACTION_NONE)

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
                            "enum": action_names,
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
        decision = json.loads(response_parsed).get("action", ACTION_NONE)
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
            return None
    except Exception as exc:
        logger.warning(
            f"Could not infer action from failed function call with error: {exc}"
        )
        return None

    try:
        mapped_action = await _map_decision_to_action(decision, action_names)

        if mapped_action == ACTION_NONE:
            mapped_action = None

        logger.info(f"Mapped action: {mapped_action}")
        return mapped_action
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return None

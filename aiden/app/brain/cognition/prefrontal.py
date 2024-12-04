from enum import StrEnum
import os

from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE
from aiden.models.brain import ACTION_NONE, Action, BrainConfig


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
    decision_prompt = f"{sensory_input}\n{instruction}"

    messages = [
        HumanMessage(content=decision_prompt),
    ]

    Actions = StrEnum("Actions", action_names)

    @tool
    def map_decision_to_action(action: Actions) -> str:
        """
        Based on the sensory inputs provided, decide which action to take.
        """
        if action in action_names:
            return action
        return ACTION_NONE

    llm = ChatOllama(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "mistral"),
        format="json",
        timeout=30.0,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        temperature=0.6,
        top_p=0.95,
        max_tokens=80,
    ).bind_tools([map_decision_to_action])

    logger.info(f"Prefrontal chat message: {messages}")
    logger.debug(
        f"Prefrontal tool schema: {map_decision_to_action.args_schema.model_json_schema()}"
    )

    try:
        response: AIMessage = llm.invoke(decision_prompt)
        logger.debug(f"Prefrontal response: {response}")
        args = (
            response.tool_calls[0]["args"]
            if response.tool_calls and "args" in response.tool_calls[0]
            else {"actions": ACTION_NONE}
        )
        logger.info(f"Prefrontal tool arguments: {args}")
        action = map_decision_to_action.invoke(args)
    except ValueError as exc:
        logger.error(
            f"The current model does not support tool/function calling. Error: {exc}"
        )
        return None
    except Exception as exc:
        logger.error(
            f"An unknown error occured when generating prefrontal response: {exc}"
        )
        return None

    try:
        if action == ACTION_NONE:
            action = None

        logger.info(f"Mapped action: {action}")
        return action
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return None

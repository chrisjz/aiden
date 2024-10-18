import json
import os
import re

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
    decision_prompt = f"{sensory_input}\nYour action decision:"

    messages = [
        HumanMessage(content=decision_prompt),
    ]

    def map_decision_to_action(action: str) -> dict[str, str]:
        """
        Custom function for mapping decision to action.
        """
        if action in action_names:
            return {"action": action}
        return {"action": ACTION_NONE}

    # # Create a Tool for this function
    # decision_tool = Tool.from_function(
    #     name="_map_decision_to_action",
    #     func=map_decision_to_action,
    #     description=instruction,
    #     return_direct=True
    # )

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

    try:
        response: AIMessage = llm.invoke(messages)
        logger.info(f"Prefrontal response: {response.content}")
        decision = json.loads(response.content).get("action", ACTION_NONE)
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
        if decision == ACTION_NONE:
            decision = None

        logger.info(f"Mapped action: {decision}")
        return decision
    except Exception as exc:
        logger.error(f"Failed prefrontal decision-making with error: {exc}")
        return None

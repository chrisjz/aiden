import json
import logging
import os
import re
import httpx
from aiden.app.brain.memory.hippocampus import get_memory, save_memory
from aiden.app.utils import (
    generate_session_id,
    load_brain_config,
    build_sensory_input_prompt_template,
)
from aiden.models.brain import BrainConfig, SimpleAction
from aiden.models.chat import ChatMessage, Message, Options

logger = logging.getLogger("uvicorn")

COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'


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


async def process_cortical(request) -> str:
    """
    Processes a cortical request to determine the AI's actions and thoughts based on sensory input.

    Args:
        request (CorticalRequest): The request containing sensory data and configuration.

    Returns:
        Generator: A generator yielding the AI's responses as a stream.
    """
    brain_config = load_brain_config(request.config)
    cortical_config = brain_config.regions.cortical
    personality = cortical_config.personality

    # Check if session_id is provided in request or generate a new one
    session_id = getattr(request, "session_id", generate_session_id())

    # Prepare the system prompt
    system_input = cortical_config.about + "\n"
    if brain_config.settings.feature_toggles.personality:
        system_input += f"Personality Profile:\n- Traits: {', '.join(personality.traits)}\n- Preferences: {', '.join(personality.preferences)}\n- Boundaries: {', '.join(personality.boundaries)}\n\n"
    system_input += "\n".join(cortical_config.description)

    # Prepare the user prompt based on available sensory data
    raw_sensory_input = build_sensory_input_prompt_template(request.sensory)
    logger.info(f"Raw sensory: {raw_sensory_input}")

    # Sensory integration through thalamus function
    sensory_input = await process_thalamus(raw_sensory_input, brain_config)

    # Decision-making through prefrontal function
    action_output = await process_prefrontal(sensory_input, brain_config)

    # Verbal output through broca function
    speech_output = await process_broca(sensory_input, brain_config)

    # Format final thoughts prompt
    final_thoughts_input = (
        f"\n{cortical_config.instruction}\nYour sensory data: {sensory_input}"
    )
    if action_output != SimpleAction.NONE.value:
        action_output_formatted = action_output.replace("_", " ")
        final_thoughts_input += (
            f"\nYou decide to perform the action: {action_output_formatted}."
        )

    # Retrieve short-term memory
    history = get_memory(session_id)

    logger.info(f"History from redis: {history}")

    # Prepare the chat message for the Cognitive API
    messages = [Message(role="system", content=system_input)]
    if history:
        messages.extend(history)

    messages.append(Message(role="user", content=final_thoughts_input))

    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(
            frequency_penalty=1.2,
            penalize_newline=False,
            presence_penalty=1.7,
            repeat_last_n=48,
            repeat_penalty=1.3,
            temperature=0.9,
            top_k=16,
            top_p=0.9,
        ),
    )

    # Thoughts output through subconcious function
    thoughts_output = await process_subconscious(chat_message)

    # Combine action, thoughts, and speech into one message
    combined_message_content = ""
    if action_output != SimpleAction.NONE.value:
        combined_message_content += f"<action>{action_output}</action>\n"
    combined_message_content += f"<thoughts>{thoughts_output}</thoughts>\n"
    if speech_output:
        combined_message_content += f"<speech>{speech_output}</speech>\n"

    # Append formatted combined message to messages
    combined_message_content_formatted = f"My thoughts:\n{thoughts_output}\nMy speech:\n{speech_output}\nMy actions performed: {action_output}"
    messages.append(
        Message(role="assistant", content=combined_message_content_formatted)
    )

    # TODO: Stream all of these separately
    async def stream_response():
        # Stream the combined message
        yield json.dumps({"message": {"content": combined_message_content}}) + "\n"

        # Store the updated history in Redis
        save_memory(session_id, messages)

    return stream_response()


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
        Message(role="system", content=instruction),
        Message(role="user", content=decision_prompt),
    ]
    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(
            frequency_penalty=1.0,
            presence_penalty=0.6,
            temperature=0.6,
            top_p=0.95,
            max_tokens=80,
        ),
    )

    logger.info(
        f"Prefrontal chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            decision = (
                response.json()
                .get("message", {})
                .get("content", SimpleAction.NONE.value)
                .strip()
            )
            logger.info(f"Prefrontal decision: {decision}")
            mapped_action = await _map_decision_to_action(decision)
            logger.info(f"Mapped action: {mapped_action}")
            return mapped_action
        else:
            logger.error(f"Failed decision-making with status: {response.status_code}")
            return SimpleAction.NONE.value


async def process_subconscious(chat_message: ChatMessage) -> str:
    """
    Process the thoughts from the subconscious areas of the AI model and return them as a string.

    Args:
        chat_message (ChatMessage): The message to be processed.

    Returns:
        str: The processed thoughts as a string. If processing fails, returns an empty string.
    """
    logger.info(
        f"Subconcious chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=45.0
        )
        if response.status_code == 200:
            thoughts = response.json().get("message", {}).get("content", "").strip()
            logger.info(f"Thoughts: {thoughts}")
            return thoughts
        else:
            logger.error(
                f"Failed thoughts processing with status: {response.status_code}"
            )
            return ""


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
            penalize_newline=False,
            presence_penalty=1.0,
            repeat_last_n=32,
            repeat_penalty=1.0,
            temperature=0.7,
            top_k=40,
            top_p=0.9,
        ),
    )

    logger.info(
        f"Thalamus chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            integrated_sensory_input = (
                response.json().get("message", {}).get("content", sensory_input)
            )
            logger.info(f"Restructured sensory input: {integrated_sensory_input}")
            return integrated_sensory_input
        else:
            logger.error(
                f"Failed restructuring sensory input with status: {response.status_code}"
            )
            return sensory_input

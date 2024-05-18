import json
import logging
import os
import httpx
from aiden.app.utils import load_brain_config, build_sensory_input_prompt_template
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


async def process_broca(auditory_input: str, brain_config: BrainConfig) -> str:
    """
    Simulate the Broca's area process of deciding what to speak in response to auditory input.

    TODO: Handle input other than auditory e.g. responding to a text message.

    Args:
        auditory_input (str): The auditory sensory input processed by the thalamus.
        brain_config (BrainConfig): The configuration settings of the brain.

    Returns:
        str: The speech to be spoken out loud by the AI, or an empty string if no response is needed.
    """
    # TODO: Automatically detect if AI should respond based on if they are engaged in a conversation.
    if not auditory_input or "someone say" not in auditory_input.lower():
        logger.info("No one is speaking to the AI or relevant auditory input missing.")
        return ""

    instruction = "\n".join(brain_config.regions.broca.instruction)
    decision_prompt = f"Auditory input: {auditory_input}\nYour response:"

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
            temperature=0.5,
            top_p=0.9,
            max_tokens=60,
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
            logger.info(f"Broca's decision: {speech_output}")
            return speech_output
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
    logger.info(f"Integrated sensory from thalamus: {sensory_input}")

    # Decision-making through prefrontal function
    action_decision = await process_prefrontal(sensory_input, brain_config)
    logger.info(f"Action decision from prefrontal: {action_decision}")

    # Format final thoughts output for streaming
    final_thoughts = f"\n{cortical_config.instruction}\n{sensory_input}"
    if action_decision != SimpleAction.NONE.value:
        action_decision_formatted = action_decision.replace("_", " ")
        final_thoughts += (
            f"\nYou decide to perform the action: {action_decision_formatted}."
        )

    # Prepare the chat message for the Cognitive API
    messages = [Message(role="system", content=system_input)]
    if request.history:
        messages.extend(request.history)
    messages.append(Message(role="user", content=final_thoughts))

    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=True,
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

    logger.info(
        f"Cortical chat message: {json.dumps(chat_message.model_dump(), indent=2)}"
    )

    async def stream_response():
        # Stream action
        if action_decision != SimpleAction.NONE.value:
            yield (
                json.dumps(
                    {"message": {"content": f"<action>{action_decision}</action>\n"}}
                )
                + "\n"
            )

        # Stream thoughts
        yield json.dumps({"message": {"content": "<thoughts>\n"}}) + "\n"
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
            ) as response:
                async for chunk in response.aiter_raw():
                    if chunk:
                        yield chunk
        yield json.dumps({"message": {"content": "\n</thoughts>"}}) + "\n"

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


async def process_thalamus(
    integrated_sensory_data: str, brain_config: BrainConfig
) -> str:
    """
    Simulates the thalamic process of restructuring sensory input.

    Args:
        integrated_sensory_data (str): The initial sensory data.
        brain_config (BrainConfig): Configuration of the brain.

    Returns:
        str: The rewritten sensory prompt or the original if the request fails.
    """
    instruction = "\n".join(brain_config.regions.thalamus.instruction)
    messages = [
        Message(role="system", content=instruction),
        Message(role="user", content=integrated_sensory_data),
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
            rewritten_prompt = (
                response.json()
                .get("message", {})
                .get("content", integrated_sensory_data)
            )
            return rewritten_prompt
        else:
            return integrated_sensory_data

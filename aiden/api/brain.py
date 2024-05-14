import logging
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
import httpx

from aiden.app.utils import load_brain_config
from aiden.app.utils import build_sensory_input_prompt_template
from aiden.models.brain import BrainConfig, Personality, SimpleAction
from aiden.models.brain import CorticalRequest
from aiden.models.chat import ChatMessage, Message, Options

app = FastAPI()

logger = logging.getLogger("uvicorn")

# Cognitive API URL
COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'


async def _map_decision_to_action(decision: str) -> str:
    """
    Maps a textual decision into a defined action.

    This function analyzes the given decision string to determine which of the
    predefined actions it corresponds to. It uses a simple substring match after
    normalizing the input text, which makes the function robust against variations
    in case or underscores versus spaces.

    Args:
        decision (str): The raw decision text from which to infer the action.

    Returns:
        str: The matched action as a string. If no action matches, returns "none".

    Example:
        >>> await _map_decision_to_action("Move forward quickly")
        'forward'

        >>> await _map_decision_to_action("turn_Left")
        'left'

        >>> await _map_decision_to_action("stop here")
        'none'
    """

    # Format the decision text to improve match robustness
    decision_formatted = decision.lower().replace(" ", "_")

    # Check against all possible actions
    for action in SimpleAction:
        if action.value in decision_formatted or decision_formatted in action.value:
            return action.value

    # Default action if no matches found
    return SimpleAction.NONE.value


async def prefrontal(sensory_input: str, brain_config: BrainConfig) -> str:
    """
    Simulate the prefrontal cortex process of deciding the next action based on sensory input. It sends a request to the Cognitive API and handles the response.

    TODO: Consider adding internal state and preferences as deciding factors.

    Args:
        sensory_input (str): The sensory input after processing by the thalamus.
        brain_config (BrainConfig): The brain configuration.

    Returns:
        str: The decision on what action to take next, or no action if the request fails.
    """
    instruction = "\n".join(brain_config.regions.prefrontal.instruction)

    decision_prompt = f"Sensory input:\n{sensory_input}\nYour action:"

    messages = [
        Message(
            role="system",
            content=instruction,
        ),
        Message(role="user", content=decision_prompt),
    ]

    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(
            frequency_penalty=2.0,  # Strongly discourage repetition
            presence_penalty=1.0,  # Moderately discourage new tokens
            temperature=0.3,  # Lower temperature for more deterministic output
            top_p=1.0,
            max_tokens=60,  # Limit the length of the completion
        ),
    )

    logger.info(f"Prefrontal chat message: {chat_message.model_dump()}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            COGNITIVE_API_URL, json=chat_message.model_dump(), timeout=30.0
        )
        if response.status_code == 200:
            decision = response.json().get("message", {}).get("content", sensory_input)
            logger.info(f"Prefrontal decision: {decision}")
            return await _map_decision_to_action(decision)
        else:
            return SimpleAction.NONE.value


async def thalamus(integrated_sensory_data: str, brain_config: BrainConfig) -> str:
    """
    Simulate the thalamic process of rewriting the received prompt to ensure it
    matches a specific narrative structure. It requests a rewriting from the
    Cognitive API and handles the response.

    Args:
        integrated_sensory_data (str): The initial sensory data and narrative content.
        brain_config (BrainConfig): The brain configuration.

    Returns:
        str: The rewritten sensory prompt or the original if the request fails.
    """
    messages = [
        Message(
            role="system",
            content=brain_config.regions.thalamus.instruction,
        ),
        Message(role="user", content=integrated_sensory_data),
    ]

    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
        options=Options(),
    )

    logger.info(f"Thalamus chat message: {chat_message.model_dump()}")

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


@app.post("/cortical/")
async def cortical(request: CorticalRequest) -> StreamingResponse:
    """
    Handle requests to process sensory data through the cognitive API to simulate
    brain cortical activity. It constructs the narrative framework and sends it
    for cognitive processing, streaming the response back to the client.

    Args:
        request (CorticalRequest): The incoming request with sensory data and configuration.

    Returns:
        StreamingResponse: The continuous response stream from the cognitive model.

    Raises:
        HTTPException: Raises an exception for any internal processing errors.
    """
    logger.info(f"Cognitive API URL: {COGNITIVE_API_URL}")
    brain_config: BrainConfig = load_brain_config(request.config)
    cortical_config = brain_config.regions.cortical
    personality: Personality = cortical_config.personality
    try:
        system_input = cortical_config.about + "\n"
        if brain_config.settings.feature_toggles.personality:
            system_input += f"""
Here is your personality profile:
- Traits: {', '.join(personality.traits)}
- Preferences: {', '.join(personality.preferences)}
- Boundaries: {', '.join(personality.boundaries)}

"""
        system_input += "\n".join(cortical_config.description)

        # Prepare the user prompt template based on available sensory data
        raw_sensory_input = build_sensory_input_prompt_template(request.sensory)

        # Sensory integration through thalamus function
        logger.info(f"Raw sensory: {raw_sensory_input}")
        sensory_input = await thalamus(raw_sensory_input, brain_config)
        logger.info(f"Integrated sensory from thalamus: {sensory_input}")

        # Decision-making through prefrontal function
        action_decision = await prefrontal(sensory_input, brain_config)
        logger.info(f"Action decision from prefrontal: {action_decision}")
        if action_decision != SimpleAction.NONE.value:
            action_decision_formatted = action_decision.replace("_", " ")
            sensory_input += f"\nYou are performing the following action: {action_decision_formatted}"

        sensory_input += f"\n{cortical_config.instruction}"

        # Prepare the chat message for the Cognitive API
        messages = [Message(role="system", content=system_input)]
        if request.history:
            messages.extend(request.history)
        messages.append(Message(role="user", content=sensory_input))

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

        logger.info(f"Cortical chat message: {chat_message.model_dump()}")

        async def stream_response():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    COGNITIVE_API_URL,
                    json=chat_message.model_dump(),
                    timeout=30.0,
                ) as response:
                    async for chunk in response.aiter_raw():
                        if chunk:
                            yield chunk

        # TODO: Return <action>
        return StreamingResponse(stream_response(), media_type="application/json")

    except Exception as e:
        logger.error(f"Error in cortical endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

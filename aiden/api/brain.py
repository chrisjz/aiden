import logging
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
import httpx

from aiden.app.utils import load_brain_config
from aiden.app.utils import build_sensory_input_prompt_template
from aiden.models.brain import BrainConfig, Personality
from aiden.models.brain import CorticalRequest
from aiden.models.chat import ChatMessage, Message, Options

app = FastAPI()

logger = logging.getLogger("uvicorn")

# Cognitive API URL
COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'


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

        logger.info(f"Raw sensory input prompt template: {raw_sensory_input}")
        sensory_input = await thalamus(raw_sensory_input, brain_config)
        sensory_input += f"\n{cortical_config.instruction}"
        logger.info(f"Sensory input prompt template: {sensory_input}")

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

        return StreamingResponse(stream_response(), media_type="application/json")

    except Exception as e:
        logger.error(f"Error in cortical endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import logging
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
import httpx

from aiden.app.utils import load_brain_config
from aiden.app.utils import build_user_prompt_template
from aiden.models.brain import Personality
from aiden.models.brain import CorticalRequest
from aiden.models.chat import ChatMessage, Message, Options

app = FastAPI()

logger = logging.getLogger("uvicorn")

# Cognitive API URL
COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'


async def rewrite_user_prompt(initial_prompt: str):
    messages = [
        Message(
            role="system",
            content="Rewrite the prompt you receive from a first-person perspective.",
        ),
        Message(role="user", content=initial_prompt),
    ]

    chat_message = ChatMessage(
        model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
        messages=messages,
        stream=False,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(COGNITIVE_API_URL, json=chat_message.model_dump())
        if response.status_code == 200:
            logger.info(f"Rewritten response json: {response.json()}")
            rewritten_prompt = (
                response.json().get("message", {}).get("content", initial_prompt)
            )
            return rewritten_prompt
        else:
            return initial_prompt


@app.post("/cortical/")
async def cortical(request: CorticalRequest):
    logger.info(f"Cognitive API URL: {COGNITIVE_API_URL}")
    brain_config = load_brain_config(request.config)
    personality: Personality = brain_config.personality
    try:
        system_prompt_template = brain_config.description + "\n"
        if brain_config.feature_toggles.personality:
            system_prompt_template += f"""
Here is your personality profile:
- Traits: {', '.join(personality.traits)}
- Preferences: {', '.join(personality.preferences)}
- Boundaries: {', '.join(personality.boundaries)}

"""
        system_prompt_template += "\n".join(brain_config.instructions)

        # Prepare the user prompt template based on available sensory data
        user_prompt_template = build_user_prompt_template(request.sensory, brain_config)

        logger.info(f"Original user prompt template: {user_prompt_template}")
        user_prompt_template = await rewrite_user_prompt(user_prompt_template)
        logger.info(f"Rewritten user prompt template: {user_prompt_template}")

        # Prepare the chat message for the Cognitive API
        messages = [Message(role="system", content=system_prompt_template)]
        if request.history:
            messages.extend(request.history)
        messages.append(Message(role="user", content=user_prompt_template))

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

        logger.info(f"Chat message: {chat_message.model_dump()}")

        async def stream_response():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", COGNITIVE_API_URL, json=chat_message.model_dump()
                ) as response:
                    async for chunk in response.aiter_raw():
                        if chunk:
                            yield chunk

        return StreamingResponse(stream_response(), media_type="application/json")

    except Exception as e:
        logger.error(f"Error in cortical endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

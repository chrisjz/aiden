import json
import logging
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
import httpx

from aiden.models.brain import BrainConfig, Personality, Sensory
from aiden.models.chat import ChatMessage, Message

app = FastAPI()

logger = logging.getLogger("uvicorn")

# Cognitive API URL
COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'


def load_brain_config(config_file: str) -> BrainConfig:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Cannot find the brain configuration file")
    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return BrainConfig(**data)


@app.post("/cortical/")
async def cortical(sensory: Sensory, config: str = "./config/brain/default.json"):
    logger.info(f"Cognitive API URL: {COGNITIVE_API_URL}")
    brain_config = load_brain_config(config)
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
        user_prompt_template = f"""
My visual input: {sensory.vision}
My auditory input: {sensory.auditory}
My tactile input: {sensory.tactile}
My olfactory input: {sensory.olfactory}
My gustatory input: {sensory.gustatory}
{brain_config.action}
"""

        logger.info(f"System prompt formatted: {system_prompt_template.strip()}")
        logger.info(f"Sensory data formatted: {user_prompt_template.strip()}")

        # Prepare the chat message for the Cognitive API
        chat_message = ChatMessage(
            model=os.environ.get("COGNITIVE_MODEL", "bakllava"),
            messages=[
                Message(role="system", content=system_prompt_template),
                Message(role="user", content=user_prompt_template),
            ],
            stream=True,
        )

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

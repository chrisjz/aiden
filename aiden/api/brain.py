import logging
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
import httpx

from aiden.models.brain import SensoryData

app = FastAPI()


# Cognitive API URL
COGNITIVE_API_URL = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "8000")}/api/chat'

# System prompt template
SYSTEM_PROMPT = {
    "personality": {
        "traits": ["curious", "friendly", "respectful"],
        "preferences": ["prefers concise responses", "enjoys learning new things"],
        "boundaries": ["avoids controversial topics", "respects user privacy"],
    },
    "action": "What am I currently experiencing and thinking?",
}

logger = logging.getLogger("uvicorn")


@app.post("/cortical/")
async def cortical(sensory_data: SensoryData):
    logger.info(f"Cognitive API URL: {COGNITIVE_API_URL}")
    try:
        # Convert the system prompt to compatible template
        system_prompt_template = f"""
You are an AI with a virtual body in a simulation.
Your personality has the following traits: {', '.join(SYSTEM_PROMPT['personality']['traits'])}.
You prefer {', '.join(SYSTEM_PROMPT['personality']['preferences'])}.
Your boundaries include: {', '.join(SYSTEM_PROMPT['personality']['boundaries'])}.
Your task is to observe your surroundings and report what you perceive.
Please respond in the first person, as if you are experiencing the environment directly.
""".strip()

        # Prepare the user prompt template based on available sensory data
        user_prompt_template = f"""
My visual input: {sensory_data.vision}
My auditory input: {sensory_data.auditory}
My tactile input: {sensory_data.tactile}
My olfactory input: {sensory_data.smell}
My gustatory input: {sensory_data.taste}
{SYSTEM_PROMPT['action']}
""".strip()

        logger.info(f"System prompt formatted: {system_prompt_template}")
        logger.info(f"Sensory data formatted: {user_prompt_template}")

        # Prepare the chat message for the Cognitive API
        chat_message = {
            "model": os.environ.get("COGNITIVE_MODEL", "bakllava"),
            "messages": [
                {"role": "system", "content": system_prompt_template},
                {"role": "user", "content": user_prompt_template},
            ],
            "stream": True,  # Enable streaming
        }

        async def stream_response():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", COGNITIVE_API_URL, json=chat_message
                ) as response:
                    async for chunk in response.aiter_raw():
                        if chunk:
                            yield chunk

        return StreamingResponse(stream_response(), media_type="application/json")

    except Exception as e:
        logger.error(f"Error in cortical endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse

from aiden import logger
from aiden.app.brain.cortical import process_cortical
from aiden.models.brain import CorticalRequest

app = FastAPI()


@app.post("/cortical/")
async def read_cortical(request: CorticalRequest) -> StreamingResponse:
    """
    Endpoint to process cortical requests and return the AI's action and thoughts.

    Args:
        request (CorticalRequest): The request payload containing sensory data and configuration.

    Returns:
        StreamingResponse: The continuous response stream from the cognitive model.
    """
    try:
        stream = await process_cortical(request)
        return StreamingResponse(stream, media_type="application/json")
    except Exception as e:
        logger.error(f"Error in cortical endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

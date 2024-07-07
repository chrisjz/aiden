from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse

from aiden import logger
from aiden.app.brain.cortical import process_cortical
from aiden.app.brain.occipital import process_occipital
from aiden.models.brain import CorticalRequest, OccipitalRequest

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


@app.post("/occipital/")
async def read_occipital(request: OccipitalRequest) -> StreamingResponse:
    """
    Endpoint to process occipital requests and stream the AI's visual recognition output.

    Args:
        request (OccipitalRequest): The request payload containing image data and configuration.

    Returns:
        StreamingResponse: The continuous response stream from the cognitive model.
    """
    try:
        stream = process_occipital(request)
        return StreamingResponse(stream, media_type="application/json")
    except Exception as e:
        logger.error(f"Error in occipital endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

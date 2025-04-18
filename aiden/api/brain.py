from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from aiden import logger
from aiden.app.brain.auditory import process_auditory
from aiden.app.brain.cortical import process_cortical
from aiden.app.brain.memory.hippocampus import process_wipe_memory
from aiden.app.brain.occipital import process_occipital
from aiden.app.clients.redis_client import redis_client
from aiden.models.brain import (
    AuditoryRequest,
    CorticalRequest,
    NeuralyzerRequest,
    OccipitalRequest,
)

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
        StreamingResponse: The continuous response stream from the occipital model.
    """
    try:
        stream = process_occipital(request)
        return StreamingResponse(stream, media_type="application/json")
    except Exception as e:
        logger.error(f"Error in occipital endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auditory/")
async def read_auditory(request: AuditoryRequest) -> StreamingResponse:
    """
    Endpoint to process auditory requests for ambient noise and stream the AI's auditory recognition output.

    Args:
        request (AuditoryRequest): The request payload containing audio data and configuration.

    Returns:
        StreamingResponse: The continuous response stream from the auditory model.
    """
    try:
        stream = process_auditory(request)
        return StreamingResponse(stream, media_type="application/json")
    except Exception as e:
        logger.error(f"Error in auditory endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/neuralyzer/")
async def wipe_short_term_memory(request: NeuralyzerRequest) -> JSONResponse:
    """
    Endpoint to wipe an agent's short term memory.

    Args:
        request (NeuralyzerRequest): The request payload containing the agent ID.

    Returns:
        JSONResponse: The result of the memory wipe operation.
    """
    response_json = await process_wipe_memory(
        request=request, redis_client=redis_client
    )
    return JSONResponse(content=response_json, media_type="application/json")

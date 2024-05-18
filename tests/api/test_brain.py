import json
import pytest
from httpx import AsyncClient, Response

from aiden.api.brain import app

# Sample sensory data for testing
sensory_data = {
    "vision": "I see a tree and a car.",
    "auditory": "I hear a bird chirping.",
}


@pytest.mark.asyncio
async def test_cortical_endpoint(mocker):
    # Create a mock response object
    mock_response = Response(
        status_code=200,
        json={
            "model": "mistral",
            "message": {"role": "assistant", "content": "It's a sunny day."},
            "done": True,
        },
    )

    # Mock the post method to return the mock response
    mocker.patch.object(AsyncClient, "post", return_value=mock_response)

    # Test the Brain API's cortical endpoint asynchronously
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/cortical/", json=sensory_data)
        assert response.status_code == 200
        assert "It's a sunny day." in response.text


# Integration test with a mock Ollama API
@pytest.mark.asyncio
async def test_integration_with_mock_ollama(mocker):
    mock_response_content = {
        "model": "mistral",
        "message": {"role": "assistant", "content": "I think it's a sunny day."},
        "done": True,
    }
    mock_response = Response(status_code=200, json=mock_response_content)

    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/cortical/", json=sensory_data)
        assert response.status_code == 200
        response_json = json.loads(response.text)
        assert (
            mock_response_content["message"]["content"]
            in response_json["message"]["content"]
        )

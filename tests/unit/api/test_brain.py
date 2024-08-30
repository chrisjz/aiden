import json
import pytest
from httpx import AsyncClient, Response

from aiden.api.brain import app

# Sample sensory data for testing
sensory_data = {
    "vision": "I see a tree and a car.",
    "auditory": "I hear a bird chirping.",
}

# Simulated base64 image string for testing
base64_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."


@pytest.mark.asyncio
async def test_auditory_endpoint(mocker):
    # Create a mock response object to simulate the response from the auditory classification service
    mock_response = Response(
        status_code=200,
        json=[
            {"class": "Bird", "score": 0.478},
            {"class": "Animal", "score": 0.4669},
            {"class": "Wild animals", "score": 0.4655},
        ],
    )

    # Mock the post method of AsyncClient to return the mock response
    mocker.patch.object(AsyncClient, "post", return_value=mock_response)

    # Test the Brain API's auditory endpoint asynchronously
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auditory/", json={"audio": "base64_encoded_audio_data"}
        )
        assert response.status_code == 200
        assert '"class": "Bird"' in response.text
        assert '"class": "Animal"' in response.text


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


@pytest.mark.asyncio
async def test_occipital_endpoint(mocker):
    # Create a mock response object to simulate the response from an LLM or image processing service
    mock_response = Response(
        status_code=200,
        json={
            "model": "bakllava",
            "message": {
                "role": "assistant",
                "content": "I see a park with children playing.",
            },
            "done": True,
        },
    )

    # Mock the post method of AsyncClient to return the mock response
    mocker.patch.object(AsyncClient, "post", return_value=mock_response)

    # Test the Brain API's occipital endpoint asynchronously
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/occipital/", json={"image": base64_image})
        assert response.status_code == 200
        assert "I see a park with children playing." in response.text


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

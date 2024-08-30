import pytest
from aiohttp import ClientSession

from aiden.app.brain.auditory import process_auditory
from aiden.models.brain import AuditoryRequest


@pytest.mark.asyncio
async def test_process_auditory(mocker):
    # Mock base64 decoding to return a valid MP3 or WAV magic bytes
    mocker.patch(
        "base64.b64decode", return_value=b"\xff\xf3\x50\x80"
    )  # Mock as MP3 format

    # Create a mock response for the classification service
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.json = mocker.AsyncMock(
        return_value=[
            {"class": "Bird", "score": 0.478},
            {"class": "Animal", "score": 0.4669},
            {"class": "Wild animals", "score": 0.4655},
        ]
    )

    # Mock the aiohttp ClientSession itself
    mock_post = mocker.patch.object(ClientSession, "post", return_value=mock_response)

    # Mock the context manager methods
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = None

    # Prepare an AuditoryRequest object
    request = AuditoryRequest(audio="base64_encoded_audio_data")

    # Simulate the process_auditory function call and collect results
    recognized_input = ""
    async for chunk in process_auditory(request):
        recognized_input += chunk

    # Assert the recognized input contains the expected classifications
    assert '"class_name":"Bird"' in recognized_input
    assert '"class_name":"Animal"' in recognized_input

    # Check that the session post method was called correctly
    mock_response.json.assert_called_once()
    mock_post.assert_called_once()

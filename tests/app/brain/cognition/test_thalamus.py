from aiden.app.brain.cognition.thalamus import process_thalamus


import httpx
import pytest


from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_process_thalamus_rewrite(mocker, brain_config):
    # Mock the response from the cognitive API
    mock_response = {
        "message": {"content": "Rewritten sensory input based on narrative structure."}
    }

    with httpx.Client() as client:
        client.post = AsyncMock(
            return_value=httpx.Response(status_code=200, json=mock_response)
        )

        mocker.patch(
            "httpx.AsyncClient.post",
            return_value=httpx.Response(status_code=200, json=mock_response),
        )

        # Simulate the thalamus function call
        rewritten_input = await process_thalamus("Initial sensory data", brain_config)

        # Assert the rewritten input is as expected
        assert (
            rewritten_input == "Rewritten sensory input based on narrative structure."
        )

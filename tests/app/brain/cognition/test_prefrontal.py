from aiden.app.brain.cognition.prefrontal import (
    _map_decision_to_action,
    process_prefrontal,
)


import httpx
import pytest


from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_process_prefrontal_decision(mocker, brain_config):
    # Mock the response from the cognitive API
    mock_response = {"message": {"content": "move_forward"}}

    # Use pytest-mock to create an async mock for the httpx.AsyncClient
    with httpx.Client() as client:
        client.post = AsyncMock(
            return_value=httpx.Response(status_code=200, json=mock_response)
        )

        mocker.patch(
            "httpx.AsyncClient.post",
            return_value=httpx.Response(status_code=200, json=mock_response),
        )

        # Simulate the prefrontal function call
        decision = await process_prefrontal(
            "Sensory input leads to a clear path", brain_config
        )

        # Assert the decision is as expected
        assert decision == "move_forward"


@pytest.mark.asyncio
async def test_map_decision_to_action():
    assert await _map_decision_to_action("Move forward") == "move_forward"
    assert await _map_decision_to_action("turn_left") == "turn_left"
    assert await _map_decision_to_action("Backward") == "move_backward"
    assert await _map_decision_to_action("right") == "turn_right"
    assert await _map_decision_to_action("0199393921") == "none"

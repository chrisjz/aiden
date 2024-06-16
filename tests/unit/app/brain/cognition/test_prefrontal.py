import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.prefrontal import (
    _map_decision_to_action,
    process_prefrontal,
)


@pytest.mark.asyncio
async def test_process_prefrontal_decision(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(content="move_forward")

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.prefrontal.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the function call
    response = await process_prefrontal(
        "Sensory input leads to a clear path", brain_config
    )

    # Check if the response matches the expected action
    assert response == "move_forward"

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_map_decision_to_action():
    assert await _map_decision_to_action("Move forward") == "move_forward"
    assert await _map_decision_to_action("turn_left") == "turn_left"
    assert await _map_decision_to_action("Backward") == "move_backward"
    assert await _map_decision_to_action("right") == "turn_right"
    assert await _map_decision_to_action("0199393921") == "none"

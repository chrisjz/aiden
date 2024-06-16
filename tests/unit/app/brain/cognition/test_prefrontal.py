import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.prefrontal import (
    _map_decision_to_action,
    process_prefrontal,
)


@pytest.mark.asyncio
async def test_process_prefrontal_decision(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(
        content="",
        id="some_id",
        tool_calls=[
            {
                "name": "_map_decision_to_action",
                "args": {"action": "move_forward"},
                "id": "some_id",
            }
        ],
    )

    # Mock OllamaFunctions class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.prefrontal.OllamaFunctions.bind_tools", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Mock response parser
    mocker.patch(
        "aiden.app.brain.cognition.prefrontal.parse_response",
        return_value='{"action": "move_forward"}',
    )

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

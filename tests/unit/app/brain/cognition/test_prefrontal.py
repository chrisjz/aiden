import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.prefrontal import (
    _map_decision_to_action,
    process_prefrontal,
)
from aiden.models.brain import BaseAction


@pytest.mark.asyncio
async def test_process_prefrontal_decision(mocker, brain_config):
    # Prepare actions available
    actions = ["enter room"] + [e.value for e in BaseAction]

    # Create a mock response for the ChatOllama
    mock_response = AIMessage(
        content="",
        id="some_id",
        tool_calls=[
            {
                "name": "_map_decision_to_action",
                "args": {"action": "move forward"},
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
        return_value='{"action": "move forward"}',
    )

    # Simulate the function call
    response = await process_prefrontal(
        "Sensory input leads to a clear path", brain_config, actions
    )

    # Check if the response matches the expected action
    assert response == "move forward"

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_map_decision_to_action():
    actions = ["enter room"] + [e.value for e in BaseAction]
    assert await _map_decision_to_action("Move forward", actions) == "move forward"
    assert await _map_decision_to_action("move forward", actions) == "move forward"
    assert await _map_decision_to_action("turn_left", actions) == "turn left"
    assert await _map_decision_to_action("Backward", actions) == "move backward"
    assert await _map_decision_to_action("right", actions) == "turn right"
    assert await _map_decision_to_action("0199393921", actions) == "none"
    assert await _map_decision_to_action("enter room", actions) == "enter room"

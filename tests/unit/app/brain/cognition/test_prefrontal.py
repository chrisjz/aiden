import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.prefrontal import (
    _map_decision_to_action,
    process_prefrontal,
)
from aiden.models.brain import Action


@pytest.mark.parametrize(
    "actions, expected_decision, expected_response",
    [
        # Test with multiple actions
        (
            [
                Action(name="enter room", description=None),
                Action(name="move backward", description=None),
                Action(name="move forward", description=None),
                Action(name="turn left", description=None),
                Action(name="turn right", description=None),
            ],
            "move forward",
            "move forward",
        ),
        # Test with only action to do nothing
        ([[Action(name="none", description=None)], "none", None]),
    ],
)
@pytest.mark.asyncio
async def test_process_prefrontal_decision_with_actions(
    mocker, brain_config, actions, expected_decision, expected_response
):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(
        content="",
        id="some_id",
        tool_calls=[
            {
                "name": "_map_decision_to_action",
                "args": {"action": expected_decision},
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
    return_value = f'{{"action": "{expected_decision}"}}'
    mocker.patch(
        "aiden.app.brain.cognition.prefrontal.parse_response", return_value=return_value
    )

    # Simulate the function call
    response = await process_prefrontal(
        "Sensory input leads to a clear path", brain_config, actions
    )

    # Check if the response matches the expected action
    assert response == expected_response

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_process_prefrontal_decision_without_actions(brain_config):
    # Pass empty list of actions
    actions = []

    # Simulate the function call
    response = await process_prefrontal(
        "Sensory input leads to a clear path", brain_config, actions
    )

    # Check if the response matches the expected action
    assert response is None


@pytest.mark.asyncio
async def test_map_decision_to_action():
    actions = [
        "enter room",
        "move backward",
        "move forward",
        "none",
        "turn left",
        "turn right",
    ]
    assert await _map_decision_to_action("Move forward", actions) == "move forward"
    assert await _map_decision_to_action("move forward", actions) == "move forward"
    assert await _map_decision_to_action("turn_left", actions) == "turn left"
    assert await _map_decision_to_action("Backward", actions) == "move backward"
    assert await _map_decision_to_action("right", actions) == "turn right"
    assert await _map_decision_to_action("0199393921", actions) == "none"
    assert await _map_decision_to_action("enter room", actions) == "enter room"

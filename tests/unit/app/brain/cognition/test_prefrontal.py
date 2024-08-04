import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.prefrontal import (
    _extract_interactions,
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
        "Sensory input leads to a clear path", brain_config
    )

    # Check if the response matches the expected action
    assert response == "move forward"

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_map_decision_to_action():
    assert await _map_decision_to_action("Move forward") == "move forward"
    assert await _map_decision_to_action("move forward") == "move forward"
    assert await _map_decision_to_action("turn_left") == "turn left"
    assert await _map_decision_to_action("Backward") == "move backward"
    assert await _map_decision_to_action("right") == "turn right"
    assert await _map_decision_to_action("0199393921") == "none"


@pytest.mark.parametrize(
    "interaction_string, expected_result",
    [
        (
            "You can additionally perform the following interactions: 'enter room', 'turn on tv'",
            ["enter room", "turn on tv"],
        ),
        (
            "You can additionally perform the following interactions: 'sit down', 'stand up', 'open door'",
            ["sit down", "stand up", "open door"],
        ),
        (
            "You can additionally perform the following interactions: 'read book'",
            ["read book"],
        ),
        (
            "You can additionally perform the following interactions: 'read book', 'watch tv' | You feel something warm touching your head.",
            ["read book", "watch tv"],
        ),
        (
            "A warm wind blows across your body. | You can additionally perform the following interactions: 'sit down', 'stand up' | You feel something warm touching your head.",
            ["sit down", "stand up"],
        ),
        ("You can additionally perform the following interactions: ", []),
        ("You can additionally perform the following interactions: ''", []),
        ("You can additionally perform the following interactions: enter room", []),
    ],
)
@pytest.mark.asyncio
async def test_extract_interactions(interaction_string, expected_result):
    assert await _extract_interactions(interaction_string) == expected_result

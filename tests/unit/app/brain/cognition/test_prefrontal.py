import pytest
from langchain_core.messages import AIMessage
from aiden.app.brain.cognition.prefrontal import process_prefrontal
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
        ([Action(name="none", description=None)], "none", None),
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
                "name": "map_decision_to_action",
                "args": {"action": expected_decision},
                "id": "some_id",
            }
        ],
    )

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.prefrontal.ChatOllama.bind_tools", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

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

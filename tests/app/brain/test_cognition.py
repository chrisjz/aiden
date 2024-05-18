from unittest.mock import AsyncMock
import httpx
import pytest

from aiden.app.brain.cognition import (
    _map_decision_to_action,
    process_broca,
    process_cortical,
    process_prefrontal,
    process_subconscious,
    process_thalamus,
)
from aiden.models.brain import BrainConfig
from aiden.models.chat import ChatMessage, Message, Options


@pytest.fixture
def brain_config():
    return BrainConfig(
        regions={
            "broca": {
                "instruction": [
                    "Based on the auditory input, decide what to say in response."
                ],
            },
            "cortical": {
                "about": "You are an AI...",
                "description": ["Respond using the sensory data."],
                "instruction": "Please describe any thoughts based on the sensory data.",
                "personality": {
                    "traits": ["curious", "observant"],
                    "preferences": ["prefers concise responses"],
                    "boundaries": [],
                },
            },
            "prefrontal": {
                "instruction": [
                    "Decide the next action based on the sensory input.",
                    "- move_forward if the path is clear.",
                    "- move_backward if there's a hazard.",
                    "- turn_left or turn_right based on other inputs.",
                    "- none if no action is needed.",
                ]
            },
            "thalamus": {
                "instruction": [
                    "Rewrite the sensory input to match a narrative structure."
                ]
            },
        },
        settings={"feature_toggles": {"personality": True}},
    )


class MockStreamResponse:
    def __init__(self, data):
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def aiter_raw(self):
        async for item in self.data:
            yield item.encode("utf-8")


@pytest.mark.asyncio
async def test_map_decision_to_action():
    assert await _map_decision_to_action("Move forward") == "move_forward"
    assert await _map_decision_to_action("turn_left") == "turn_left"
    assert await _map_decision_to_action("Backward") == "move_backward"
    assert await _map_decision_to_action("right") == "turn_right"
    assert await _map_decision_to_action("0199393921") == "none"


@pytest.mark.asyncio
async def test_process_broca_direct_address(mocker, brain_config):
    # Mock the response from the cognitive API
    mock_response = {"message": {"content": '"I am well, thank you."'}}

    # Use mocker to patch the HTTP client used in process_broca
    mocker.patch.object(
        httpx.AsyncClient,
        "post",
        return_value=httpx.Response(status_code=200, json=mock_response),
    )

    # Simulate the function call
    response = await process_broca('Someone asks: "How are you today?"', brain_config)

    # Check if the response matches the expected verbal response within quotes
    assert (
        response == "I am well, thank you."
    ), f"Expected: 'I am well, thank you.', but got: {response}"


@pytest.mark.asyncio
async def test_process_broca_silence_when_unnecessary(mocker, brain_config):
    # Test that the AI remains silent when no direct interaction or notable event occurs
    mock_response = {"message": {"content": ""}}

    # Patch the HTTP client
    mocker.patch.object(
        httpx.AsyncClient,
        "post",
        return_value=httpx.Response(status_code=200, json=mock_response),
    )

    # Simulate the function call
    response = await process_broca(
        "You notice a small bird flying in the distance.", brain_config
    )

    # Check if the AI correctly remains silent
    assert response == "", "Expected silence, but got some verbal output."


@pytest.mark.asyncio
async def test_process_cortical_request(mocker, brain_config):
    # Mock the CorticalRequest
    cortical_request = mocker.Mock()
    cortical_request.config = "path to brain config"
    cortical_request.history = []
    cortical_request.sensory = {"vision": "Clear path ahead", "auditory": "No sounds"}

    # Mock loading the brain configuration
    mocker.patch(
        "aiden.app.brain.cognition.load_brain_config", return_value=brain_config
    )

    # Mock the sensory input template
    mocker.patch(
        "aiden.app.brain.cognition.build_sensory_input_prompt_template",
        return_value="Your sensory inputs",
    )

    # Use pytest-mock to mock the various brain region functions
    mocker.patch(
        "aiden.app.brain.cognition.process_thalamus",
        return_value="Processed by thalamus",
    )
    mocker.patch(
        "aiden.app.brain.cognition.process_prefrontal", return_value="move_forward"
    )
    mocker.patch(
        "aiden.app.brain.cognition.process_broca", return_value="I am doing well."
    )
    mocker.patch(
        "aiden.app.brain.cognition.process_subconscious",
        return_value="I wonder where I should go next.",
    )

    # Mock the save_memory and get_memory functions from the hippocampus script
    mocker.patch("aiden.app.brain.memory.hippocampus.save_memory", return_value=None)
    mocker.patch("aiden.app.brain.memory.hippocampus.get_memory", return_value=[])

    # Call the function
    response_stream = await process_cortical(cortical_request)

    # Collect the response from the stream
    response_text = ""
    async for chunk in response_stream:
        response_text += chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk

    # Check that the action and thoughts are in the response
    assert "<action>move_forward</action>" in response_text
    assert "<speech>I am doing well.</speech>" in response_text
    assert "<thoughts>I wonder where I should go next.</thoughts>" in response_text


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
async def test_process_subconscious_thoughts(mocker):
    # Mock the chat message
    chat_message = ChatMessage(
        model="my model",
        messages=[Message(role="user", content="What are you thinking?")],
        stream=False,
        options=Options(),
    )
    # Mock the response from the cognitive API
    mock_response = {"message": {"content": "I am having a wonderful day."}}

    with httpx.Client() as client:
        client.post = AsyncMock(
            return_value=httpx.Response(status_code=200, json=mock_response)
        )

        mocker.patch(
            "httpx.AsyncClient.post",
            return_value=httpx.Response(status_code=200, json=mock_response),
        )

        # Simulate the subconscious function call
        thoughts = await process_subconscious(chat_message)

        # Assert the thoughts are as expected
        assert thoughts == "I am having a wonderful day."


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

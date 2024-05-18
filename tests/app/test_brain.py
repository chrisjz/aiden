import json
from unittest.mock import AsyncMock
import httpx
import pytest

from aiden.app.brain import (
    _map_decision_to_action,
    process_broca,
    process_cortical,
    process_prefrontal,
    process_thalamus,
)
from aiden.models.brain import BrainConfig


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
async def test_process_broca_decision(mocker, brain_config):
    # Mock the response from the cognitive API
    mock_response = {"message": {"content": "I am good, thank you!"}}

    with httpx.Client() as client:
        client.post = AsyncMock(
            return_value=httpx.Response(status_code=200, json=mock_response)
        )

        mocker.patch(
            "httpx.AsyncClient.post",
            return_value=httpx.Response(status_code=200, json=mock_response),
        )

        # Simulate the thalamus function call
        rewritten_input = await process_broca(
            "Someone says: How are you today?", brain_config
        )

        # Assert the rewritten input is as expected
        assert rewritten_input == "I am good, thank you!"


@pytest.mark.asyncio
async def test_process_cortical_request(mocker, brain_config):
    # Mock the CorticalRequest
    cortical_request = mocker.Mock()
    cortical_request.config = "path to brain config"
    cortical_request.history = []
    cortical_request.sensory = {"vision": "Clear path ahead", "auditory": "No sounds"}

    # Mock loading the brain configuration
    mocker.patch("aiden.app.brain.load_brain_config", return_value=brain_config)

    # Mock the sensory input template
    mocker.patch(
        "aiden.app.brain.build_sensory_input_prompt_template",
        return_value="Your sensory inputs",
    )

    # Use pytest-mock to mock the thalamus and prefrontal functions
    mocker.patch(
        "aiden.app.brain.process_thalamus", return_value="Processed by thalamus"
    )
    mocker.patch("aiden.app.brain.process_prefrontal", return_value="move_forward")

    # Prepare the mocked data for the stream response
    mock_response_data = [
        json.dumps({"message": {"content": "<action>move_forward</action>\n"}}),
        json.dumps({"message": {"content": "<thoughts>\n"}}),
        json.dumps({"message": {"content": "Processed by thalamus\n</thoughts>\n"}}),
    ]

    # Mock the httpx client used in your actual function to simulate LLM responses
    async def mock_stream():
        for item in mock_response_data:
            yield item

    mocker.patch(
        "httpx.AsyncClient.stream", return_value=MockStreamResponse(mock_stream())
    )

    # Call the function
    response_stream = await process_cortical(cortical_request)

    # Collect the response from the stream
    response_text = ""
    async for chunk in response_stream:
        response_text += chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk

    # Check that the action and thoughts are in the response
    assert "<action>move_forward</action>" in response_text
    assert "<thoughts>" in response_text
    assert "Processed by thalamus" in response_text


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

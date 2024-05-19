from aiden.app.brain.cognition.broca import process_broca


import httpx
import pytest


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

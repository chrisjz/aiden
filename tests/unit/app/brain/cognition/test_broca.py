import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.broca import process_broca


@pytest.mark.asyncio
async def test_process_broca_direct_address(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(content='"I am well, thank you."')

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.broca.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the function call
    response = await process_broca('Someone asks: "How are you today?"', brain_config)

    # Assert the rewritten input is as expected
    assert (
        response == "I am well, thank you."
    ), f"Expected: 'I am well, thank you.', but got: {response}"

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_process_broca_silence_when_unnecessary(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(content="I am well, thank you.")

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.broca.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the function call
    response = await process_broca(
        "You notice a small bird flying in the distance.", brain_config
    )

    # Check if the AI correctly remains silent
    assert response == "", "Expected silence, but got some verbal output."

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()

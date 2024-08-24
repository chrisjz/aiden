import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.broca import process_broca


@pytest.mark.asyncio
async def test_process_broca(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(content="I am well, thank you.")

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.broca.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the function call with both sensory input and language input
    sensory_input = "You see a friendly face."
    language_input = "How are you today?"

    response = await process_broca(sensory_input, brain_config, language_input)

    # Check if the response matches the expected verbal response
    assert (
        response == "I am well, thank you."
    ), f"Expected: 'I am well, thank you.', but got: {response}"

    # Check that the invoke method was called with the correct combined input
    instance.invoke.assert_called_once()

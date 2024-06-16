import pytest

from langchain_core.messages import AIMessage

from aiden.app.brain.cognition.thalamus import process_thalamus


@pytest.mark.asyncio
async def test_process_thalamus_rewrite(mocker, brain_config):
    # Create a mock response for the ChatOllama
    mock_response = AIMessage(
        content="Rewritten sensory input based on narrative structure."
    )

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.thalamus.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the thalamus function call
    rewritten_input = await process_thalamus("Initial sensory data", brain_config)

    # Assert the rewritten input is as expected
    assert rewritten_input == "Rewritten sensory input based on narrative structure."

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()

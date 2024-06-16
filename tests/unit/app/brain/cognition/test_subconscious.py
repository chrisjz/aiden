import pytest

from langchain_core.messages import AIMessage, HumanMessage

from aiden.app.brain.cognition.subconscious import process_subconscious


@pytest.mark.asyncio
async def test_process_subconscious_thoughts(mocker):
    # Actual input
    messages = [HumanMessage(content="What are you thinking?")]

    # Create a mock response for the ChatOllama
    mock_response = AIMessage(content="I am having a wonderful day.")

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch(
        "aiden.app.brain.cognition.subconscious.ChatOllama", autospec=True
    )
    instance = mock_ollama.return_value
    instance.invoke.return_value = mock_response

    # Simulate the thalamus function call
    rewritten_input = await process_subconscious(messages)

    # Assert the response is as expected
    assert rewritten_input == "I am having a wonderful day."

    # Check that the invoke method was called correctly
    instance.invoke.assert_called_once()

from aiden.app.brain.cognition.subconscious import process_subconscious
from aiden.models.chat import ChatMessage, Message, Options


import httpx
import pytest


from unittest.mock import AsyncMock


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

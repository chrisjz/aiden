import pytest
from langchain_core.messages import AIMessage, HumanMessage

from aiden.app.brain.occipital import process_occipital
from aiden.models.brain import OccipitalRequest


@pytest.mark.asyncio
async def test_process_occipital_visual_recognition(mocker, brain_config):
    # Mock loading the brain configuration
    mocker.patch(
        "aiden.app.brain.occipital.load_brain_config", return_value=brain_config
    )

    # Create a mock response for the ChatOllama
    mock_responses = [
        AIMessage(content="Recognized visual input as a park with children playing."),
        AIMessage(content="", done=True),  # Indicating the end of the stream
    ]

    # Mock ChatOllama class to return a predefined response
    mock_ollama = mocker.patch("aiden.app.brain.occipital.ChatOllama", autospec=True)
    instance = mock_ollama.return_value
    instance.stream.return_value = mock_responses

    # Prepare an OccipitalRequest object
    request = OccipitalRequest(image="base64_encoded_image_data")

    # Simulate the occipital function call and collect results
    recognized_input = ""
    async for chunk in process_occipital(request):
        recognized_input += chunk

    # Assert the recognized input is as expected
    assert (
        "Recognized visual input as a park with children playing." in recognized_input
    )

    # Check that the invoke method was called correctly
    human_message = HumanMessage(
        content="\n".join(brain_config.regions.occipital.instruction),
        image=request.image,
    )
    instance.stream.assert_called_once_with([human_message])

from aiden.app.brain.cortical import process_cortical


import pytest


@pytest.mark.asyncio
async def test_process_cortical_request(mocker, brain_config):
    # Mock the CorticalRequest
    cortical_request = mocker.Mock()
    cortical_request.config = "path to brain config"
    cortical_request.history = []
    cortical_request.sensory = {"vision": "Clear path ahead", "auditory": "No sounds"}

    # Mock loading the brain configuration
    mocker.patch(
        "aiden.app.brain.cortical.load_brain_config", return_value=brain_config
    )

    # Mock the sensory input template
    mocker.patch(
        "aiden.app.brain.cortical.build_sensory_input_prompt_template",
        return_value="Your sensory inputs",
    )

    # Use pytest-mock to mock the various brain region functions
    mocker.patch(
        "aiden.app.brain.cortical.process_thalamus",
        return_value="Processed by thalamus",
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_prefrontal", return_value="move_forward"
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_broca", return_value="I am doing well."
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_subconscious",
        return_value="I wonder where I should go next.",
    )

    # Mock the update_memory and read_memory functions from the hippocampus script
    mocker.patch("aiden.app.brain.cortical.update_memory", return_value=None)
    mocker.patch("aiden.app.brain.cortical.read_memory", return_value=[])

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

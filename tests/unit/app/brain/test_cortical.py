from aiden.app.brain.cortical import _extract_interactions, process_cortical


import pytest

from aiden.models.brain import (
    AuditoryInput,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    VisionInput,
)


@pytest.mark.asyncio
async def test_process_cortical_request(mocker, brain_config):
    # Mock the CorticalRequest
    cortical_request = mocker.Mock()
    cortical_request.config = "path to brain config"
    cortical_request.history = []
    cortical_request.sensory = Sensory(
        vision=[VisionInput(content="Clear path ahead")],
        auditory=[AuditoryInput(content="No sounds")],
        tactile=[TactileInput(content="No tactile input")],
        olfactory=[OlfactoryInput(content="No olfactory input")],
        gustatory=[GustatoryInput(content="No gustatory input")],
    )

    # Mock loading the brain configuration
    mocker.patch(
        "aiden.app.brain.cortical.load_brain_config", return_value=brain_config
    )

    # Mock the sensory input template
    mocker.patch(
        "aiden.app.brain.cortical.build_sensory_input_prompt_template",
        return_value="Your sensory inputs",
    )

    # Mock the action extractor
    mocker.patch(
        "aiden.app.brain.cortical._extract_interactions",
        return_value=[],
    )

    # Use pytest-mock to mock the various brain region functions
    mocker.patch(
        "aiden.app.brain.cortical.process_thalamus",
        return_value="Processed by thalamus",
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_prefrontal", return_value="move forward"
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_broca", return_value="I am doing well."
    )
    mocker.patch(
        "aiden.app.brain.cortical.process_subconscious",
        return_value="I wonder where I should go next.",
    )

    # Mock the update_memory and read_memory functions from the hippocampus script
    mocker.patch(
        "aiden.app.brain.cortical.MemoryManager.update_memory", return_value=None
    )
    mocker.patch("aiden.app.brain.cortical.MemoryManager.read_memory", return_value=[])

    # Call the function
    response_stream = await process_cortical(cortical_request)

    # Collect the response from the stream
    response_text = ""
    async for chunk in response_stream:
        response_text += chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk

    # Check that the action and thoughts are in the response
    assert "<action>move forward</action>" in response_text
    assert "<speech>I am doing well.</speech>" in response_text
    assert "<thoughts>I wonder where I should go next.</thoughts>" in response_text


@pytest.mark.parametrize(
    "interaction_string, expected_result",
    [
        (
            "You can additionally perform the following interactions: 'enter room', 'turn on tv'",
            ["enter room", "turn on tv"],
        ),
        (
            "You can additionally perform the following interactions: 'sit down', 'stand up', 'open door'",
            ["sit down", "stand up", "open door"],
        ),
        (
            "You can additionally perform the following interactions: 'read book'",
            ["read book"],
        ),
        (
            "You can additionally perform the following interactions: 'read book', 'watch tv' | You feel something warm touching your head.",
            ["read book", "watch tv"],
        ),
        (
            "A warm wind blows across your body. | You can additionally perform the following interactions: 'sit down', 'stand up' | You feel something warm touching your head.",
            ["sit down", "stand up"],
        ),
        ("You can additionally perform the following interactions: ", []),
        ("You can additionally perform the following interactions: ''", []),
        ("You can additionally perform the following interactions: enter room", []),
    ],
)
@pytest.mark.asyncio
async def test_extract_interactions(interaction_string, expected_result):
    assert await _extract_interactions(interaction_string) == expected_result

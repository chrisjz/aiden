from aiden.app.brain.cortical import (
    _extract_actions_from_tactile_inputs,
    process_cortical,
)


import pytest

from aiden.models.brain import (
    Action,
    AuditoryInput,
    AuditoryType,
    CorticalResponse,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    TactileType,
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
        auditory=[
            AuditoryInput(content="No sounds"),
            AuditoryInput(type=AuditoryType.LANGUAGE, content="Hello world"),
        ],
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
        "aiden.app.brain.cortical._extract_actions_from_tactile_inputs",
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
    response_json = ""
    async for chunk in response_stream:
        response_json += chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk

    content = CorticalResponse().model_validate_json(response_json)

    # Check that the action, speech and thoughts are in the response
    assert content.action == "move forward"
    assert content.speech == "I am doing well."
    assert content.thoughts == "I wonder where I should go next."


@pytest.mark.parametrize(
    "tactile_inputs, expected_actions",
    [
        # Test with multiple actions and a general tactile input
        (
            [
                TactileInput(type=TactileType.GENERAL, content="Smooth surface."),
                TactileInput(type=TactileType.ACTION, command=Action(name="jump")),
                TactileInput(type=TactileType.ACTION, command=Action(name="crouch")),
            ],
            [
                Action(name="jump", description=None),
                Action(name="crouch", description=None),
            ],
        ),
        # Test with actions containing descriptions
        (
            [
                TactileInput(
                    type=TactileType.ACTION,
                    command=Action(name="jump", description="Jump in the air."),
                ),
                TactileInput(
                    type=TactileType.ACTION,
                    command=Action(name="crouch", description="Crouch to the floor."),
                ),
            ],
            [
                Action(name="jump", description="Jump in the air."),
                Action(name="crouch", description="Crouch to the floor."),
            ],
        ),
        # Test with only general tactile input
        ([TactileInput(type=TactileType.GENERAL, content="Rough surface.")], []),
        # Test with no inputs
        ([], []),
    ],
)
@pytest.mark.asyncio
async def test_extract_actions_from_tactile_inputs(tactile_inputs, expected_actions):
    result = await _extract_actions_from_tactile_inputs(tactile_inputs)
    assert result == expected_actions

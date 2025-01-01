import pytest

from aiden.app.utils import build_sensory_input_prompt_template
from aiden.models.brain import (
    Action,
    AuditoryInput,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    VisionInput,
)


@pytest.mark.parametrize(
    "sensory, expected_output",
    [
        (
            Sensory(
                vision=[VisionInput(content="A bright light.")],
                auditory=[AuditoryInput(type="ambient", content="A loud noise.")],
                tactile=[TactileInput(type="general", content="Smooth surface.")],
                olfactory=[OlfactoryInput(content="Fresh coffee.")],
                gustatory=[GustatoryInput(content="Sweet candy.")],
            ),
            """Your current visual input: A bright light.
Your current auditory input: A loud noise.
Your current tactile input: Smooth surface.
Your current olfactory input: Fresh coffee.
Your current gustatory input: Sweet candy.""",
        ),
        (
            Sensory(
                auditory=[AuditoryInput(type="language", content="How are you today?")],
            ),
            """Your current auditory input: You hear the following spoken - How are you today?""",
        ),
        (
            Sensory(
                auditory=[
                    AuditoryInput(type="ambient", content="A loud noise."),
                    AuditoryInput(type="language", content="How are you today?"),
                ],
            ),
            """Your current auditory input: A loud noise. | You hear the following spoken - How are you today?""",
        ),
        (
            Sensory(
                tactile=[
                    TactileInput(
                        type="action",
                        command=Action(name="jump", description="Jump in the air"),
                    ),
                    TactileInput(
                        type="action",
                        command=Action(name="crouch", description="Crouch down"),
                    ),
                ],
            ),
            """Your current tactile input: You can perform the following actions - jump (Jump in the air), crouch (Crouch down)""",
        ),
        (
            Sensory(
                tactile=[
                    TactileInput(type="action", command=Action(name="jump")),
                    TactileInput(type="action", command=Action(name="crouch")),
                ],
            ),
            """Your current tactile input: You can perform the following actions - jump, crouch""",
        ),
        (
            Sensory(
                tactile=[
                    TactileInput(type="general", content="Smooth surface."),
                    TactileInput(type="action", command=Action(name="jump")),
                    TactileInput(type="action", command=Action(name="crouch")),
                ],
            ),
            """Your current tactile input: Smooth surface. | You can perform the following actions - jump, crouch""",
        ),
        (
            Sensory(
                vision=[VisionInput(content="")],
                auditory=[AuditoryInput(content="")],
                tactile=[TactileInput(content="")],
                olfactory=[OlfactoryInput(content="")],
                gustatory=[GustatoryInput(content="")],
            ),
            """No sensory inputs received""",
        ),
    ],
)
def test_build_sensory_input_prompt_template(sensory, expected_output):
    result = build_sensory_input_prompt_template(sensory)
    assert result == expected_output

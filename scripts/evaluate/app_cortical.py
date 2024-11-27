"""
CLI to directly interact with the process_cortical function in the Brain module.
"""

import asyncio

from aiden.app.brain.cortical import process_cortical_new
from aiden.models.brain import (
    Action,
    AuditoryInput,
    CorticalRequest,
    CorticalResponse,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    TactileType,
    VisionInput,
)


async def main():
    # Prompt user for sensory data
    vision_input = (
        input("Enter vision input (default: 'I see a tree and a car.'): ")
        or "I see a tree and a car."
    )
    auditory_input = (
        input("Enter auditory input (default: 'I hear a bird chirping.'): ")
        or "I hear a bird chirping."
    )
    tactile_input = (
        input(
            "Enter tactile input (default: 'I feel the gentle breeze of the wind.'): "
        )
        or "I feel the gentle breeze of the wind."
    )
    olfactory_input = (
        input(
            "Enter olfactory input (default: 'I smell the sweet scent of flowers blooming.'): "
        )
        or "I smell the sweet scent of flowers blooming."
    )
    gustatory_input = (
        input(
            "Enter gustatory input (default: 'I taste the minty flavour of the gum I'm chewing.'): "
        )
        or "I taste the minty flavour of the gum I'm chewing."
    )

    # Tactile input with actions
    tactile_input_extended = [
        TactileInput(type=TactileType.ACTION, command=Action(name="move forward")),
        TactileInput(type=TactileType.ACTION, command=Action(name="move backward")),
        TactileInput(type=TactileType.ACTION, command=Action(name="turn left")),
        TactileInput(type=TactileType.ACTION, command=Action(name="turn right")),
        TactileInput(content=tactile_input),
    ]

    sensory_data = Sensory(
        vision=[VisionInput(content=vision_input)],
        auditory=[AuditoryInput(content=auditory_input)],
        tactile=tactile_input_extended,
        olfactory=[OlfactoryInput(content=olfactory_input)],
        gustatory=[GustatoryInput(content=gustatory_input)],
    )

    payload = CorticalRequest(
        config="./config/brain/default.json",
        sensory=sensory_data,
        agent_id="0",
    )

    response: CorticalResponse = await process_cortical_new(payload)

    print("Response from cortical:\n---")
    print(f"    Action:\n{response.action}")
    print(f"    Speech:\n{response.speech}")
    print(f"    Thoughts:\n{response.thoughts}")


if __name__ == "__main__":
    asyncio.run(main())

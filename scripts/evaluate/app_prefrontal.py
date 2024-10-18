"""
CLI to interact directly with the process_prefrontal function in the Brain module.
"""

import asyncio

from aiden.app.brain.cognition.prefrontal import process_prefrontal
from aiden.app.utils import load_brain_config
from aiden.models.brain import (
    Action,
    Sensory,
    VisionInput,
    AuditoryInput,
    TactileInput,
    OlfactoryInput,
    GustatoryInput,
)


async def main():
    brain_config = load_brain_config("./config/brain/default.json")

    # Prompt user for sensory data
    vision_input = (
        input(
            "Enter vision input (default: 'I see a tree and a car heading towards me from the front.'): "
        )
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

    sensory_data = Sensory(
        vision=[VisionInput(content=vision_input)],
        auditory=[AuditoryInput(content=auditory_input)],
        tactile=[TactileInput(content=tactile_input)],
        olfactory=[OlfactoryInput(content=olfactory_input)],
        gustatory=[GustatoryInput(content=gustatory_input)],
    )

    actions = [
        Action(name="move forward"),
        Action(name="move backward"),
        Action(name="turn left"),
        Action(name="turn right"),
    ]

    # Call the process_prefrontal function directly
    decision = await process_prefrontal(
        sensory_data.model_dump(), brain_config, actions
    )

    print("Decision made based on sensory data:", decision)


if __name__ == "__main__":
    asyncio.run(main())

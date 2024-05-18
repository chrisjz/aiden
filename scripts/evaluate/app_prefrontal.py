"""
CLI to interact directly with the process_prefrontal function in the Brain module.
"""

import asyncio
from aiden.app.brain import process_prefrontal
from aiden.app.utils import load_brain_config
from aiden.models.brain import Sensory


async def main():
    brain_config = load_brain_config("./config/brain/default.json")

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

    sensory_data = Sensory(
        vision=vision_input,
        auditory=auditory_input,
        tactile=tactile_input,
        olfactory=olfactory_input,
        gustatory=gustatory_input,
    )

    # Call the process_prefrontal function directly
    decision = await process_prefrontal(sensory_data.model_dump(), brain_config)

    print("Decision made based on sensory data:", decision)


if __name__ == "__main__":
    asyncio.run(main())

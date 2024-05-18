"""
CLI to interact directly with the process_broca function in the Brain module.
"""

import asyncio
from aiden.app.brain.cognition import process_broca
from aiden.app.utils import load_brain_config


async def main():
    # Load or create a BrainConfig object
    brain_config = load_brain_config("./config/brain/default.json")

    # Prompt user for sensory input
    sensory_input = (
        input(
            "Enter sensory input (e.g., 'You see a person in front of you. They ask \"How are you today?\"'): "
        )
        or 'You see a person in front of you. They ask "How are you today?"'
    )

    # Call the process_broca function directly
    spoken_response = await process_broca(sensory_input, brain_config)

    print("AI spoken response:", spoken_response)


if __name__ == "__main__":
    asyncio.run(main())

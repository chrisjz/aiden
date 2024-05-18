"""
CLI to interact directly with the process_broca function in the Brain module.
"""

import asyncio
from aiden.app.brain import process_broca
from aiden.app.utils import load_brain_config


async def main():
    # Load or create a BrainConfig object
    brain_config = load_brain_config("./config/brain/default.json")

    # Prompt user for auditory input
    auditory_input = (
        input("Enter auditory input (e.g., 'Someone says: How are you today?'): ")
        or "Someone says: How are you today?"
    )

    # Call the process_broca function directly
    spoken_response = await process_broca(auditory_input, brain_config)

    print("AI spoken response:", spoken_response)


if __name__ == "__main__":
    asyncio.run(main())

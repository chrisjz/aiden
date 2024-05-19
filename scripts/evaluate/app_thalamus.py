"""
CLI to interact directly with the process_thalamus function in the Brain module.
"""

import asyncio
from aiden.app.brain.cognition.thalamus import process_thalamus
from aiden.app.utils import load_brain_config


async def main():
    # Load or create a BrainConfig object
    brain_config = load_brain_config("./config/brain/default.json")

    # Prompt user for integrated sensory data
    integrated_sensory_data = (
        input("Enter integrated sensory data (e.g., 'I see a tree and hear a bird.'): ")
        or "I see a tree and hear a bird."
    )

    # Call the process_thalamus function directly
    rewritten_input = await process_thalamus(integrated_sensory_data, brain_config)

    print("Rewritten sensory input to match narrative structure:", rewritten_input)


if __name__ == "__main__":
    asyncio.run(main())

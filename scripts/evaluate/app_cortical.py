"""
CLI to directly interact with the process_cortical function in the Brain module.
"""

import argparse
import asyncio
import json

from aiden.app.brain.cortical import process_cortical_new
from aiden.models.brain import (
    Action,
    AuditoryInput,
    AuditoryType,
    CorticalRequest,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    TactileType,
    VisionInput,
)


async def main():
    parser = argparse.ArgumentParser(description="Evaluate the cortical processor.")
    parser.add_argument(
        "--actions",
        action="store_true",
        help="Include preset actions for cortical processing",
    )
    parser.add_argument(
        "--default",
        action="store_true",
        help="Process cortical with default sensory input",
    )
    parser.add_argument(
        "--speech",
        action="store_true",
        help="Include preset speech input for cortical processing",
    )
    args = parser.parse_args()

    # Default inputs
    vision_input_default = "I see a tree and a car."
    auditory_input_default = "I hear a bird chirping."
    tactile_input_default = "I feel the gentle breeze of the wind."
    olfactory_input_default = "I smell the sweet scent of flowers blooming."
    gustatory_input_default = "I taste the minty flavour of the gum I'm chewing."

    if args.default:
        vision_input = vision_input_default
        auditory_input = auditory_input_default
        tactile_input = tactile_input_default
        olfactory_input = olfactory_input_default
        gustatory_input = gustatory_input_default
    else:
        # Prompt user for sensory data
        vision_input = (
            input(f"Enter vision input (default: '{vision_input_default}'): ")
            or vision_input_default
        )
        auditory_input = (
            input(f"Enter auditory input (default: '{auditory_input_default}'): ")
            or auditory_input_default
        )
        tactile_input = (
            input(f"Enter tactile input (default: '{tactile_input_default}'): ")
            or tactile_input_default
        )
        olfactory_input = (
            input(f"Enter olfactory input (default: '{olfactory_input_default}'): ")
            or olfactory_input_default
        )
        gustatory_input = (
            input(f"Enter gustatory input (default: '{gustatory_input_default}'): ")
            or gustatory_input_default
        )

    if args.actions:
        # Tactile input with actions
        final_tactile_input = [
            TactileInput(type=TactileType.ACTION, command=Action(name="move forward")),
            TactileInput(type=TactileType.ACTION, command=Action(name="move backward")),
            TactileInput(type=TactileType.ACTION, command=Action(name="turn left")),
            TactileInput(type=TactileType.ACTION, command=Action(name="turn right")),
            TactileInput(content=tactile_input),
        ]
    else:
        final_tactile_input = [TactileInput(content=tactile_input)]

    if args.speech:
        SPEECH_INPUT = "Move out of the way please!"

        final_speech_input = [
            AuditoryInput(type=AuditoryType.LANGUAGE, content=SPEECH_INPUT),
            AuditoryInput(content=auditory_input),
        ]
    else:
        final_speech_input = [AuditoryInput(content=auditory_input)]

    sensory_data = Sensory(
        vision=[VisionInput(content=vision_input)],
        auditory=final_speech_input,
        tactile=final_tactile_input,
        olfactory=[OlfactoryInput(content=olfactory_input)],
        gustatory=[GustatoryInput(content=gustatory_input)],
    )

    payload = CorticalRequest(
        config="./config/brain/default.json",
        sensory=sensory_data,
        agent_id="0",
    )

    response_generator = await process_cortical_new(payload)

    response_chunks = []
    async for chunk in response_generator:
        response_chunks.append(chunk)

    response = json.loads("".join(response_chunks))

    print("Response from cortical:\n---")
    print(f"    Action:\n{response["action"]}")
    print(f"    Speech:\n{response["speech"]}")
    print(f"    Thoughts:\n{response["thoughts"]}")


if __name__ == "__main__":
    asyncio.run(main())

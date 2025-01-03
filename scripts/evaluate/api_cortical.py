"""
CLI to interact with the Brain API's cortical endpoint for evaluation purposes,
without needing to through the Unity simulation.
"""

import os
import requests
import json

from aiden.models.brain import (
    AuditoryInput,
    CorticalRequest,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    VisionInput,
)


def main():
    api_url = f'{os.environ.get("BRAIN_PROTOCOL", "http")}://{os.environ.get("BRAIN_API_HOST", "localhost")}:{os.environ.get("BRAIN_API_PORT", "8000")}/cortical/'

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
        vision=[VisionInput(content=vision_input)],
        auditory=[AuditoryInput(content=auditory_input)],
        tactile=[TactileInput(content=tactile_input)],
        olfactory=[OlfactoryInput(content=olfactory_input)],
        gustatory=[GustatoryInput(content=gustatory_input)],
    )

    payload = CorticalRequest(
        config="./config/brain/default.json",
        sensory=sensory_data,
        agent_id="0",
    ).model_dump(mode="json")

    # Send a POST request to the Cortical endpoint
    print("Send sensory data to Cortical endpoint.")
    with requests.post(api_url, json=payload, stream=True) as response:
        if response.status_code == 200:
            print("\nResponse from Cortical API:\n")
            final_content = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    print(decoded_line)
                    json_line = json.loads(decoded_line)
                    final_content += json_line.get("message", {}).get("content", "")
            print("\nFinal combined content:\n", final_content)
        else:
            print(f"Error: {response.status_code}")


if __name__ == "__main__":
    main()

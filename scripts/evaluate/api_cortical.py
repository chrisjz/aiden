"""
CLI to interact with the Brain API for evaluation purposes,
without needing to through the Unity simulation.
"""

import os
import requests
import json

from aiden.models.brain import CorticalRequest, Sensory


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
        auditory=auditory_input,
        gustatory=gustatory_input,
        olfactory=olfactory_input,
        tactile=tactile_input,
        vision=vision_input,
    )

    payload = CorticalRequest(
        config="./config/brain/default.json", sensory=sensory_data
    ).model_dump()

    # Send a POST request to the Cortical endpoint
    print("Send sensory data to Cortical endpoint.")
    with requests.post(api_url, json=payload, stream=True) as response:
        if response.status_code == 200:
            print("Response from Cortical API:")
            final_content = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    print(decoded_line)
                    json_line = json.loads(decoded_line)
                    final_content += json_line.get("message", {}).get("content", "")
            print("Final combined content:", final_content)
        else:
            print(f"Error: {response.status_code}")


if __name__ == "__main__":
    main()

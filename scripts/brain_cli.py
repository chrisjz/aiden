"""
CLI to interact with the Brain API for testing purposes,
without needing to evaluate it through the Unity simulation.
"""

import os
import requests
import json


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

    sensory_data = {
        "vision": vision_input,
        "auditory": auditory_input,
    }

    # Send a POST request to the Cortical endpoint
    print("Send sensory data to Cortical endpoint.")
    with requests.post(api_url, json=sensory_data, stream=True) as response:
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

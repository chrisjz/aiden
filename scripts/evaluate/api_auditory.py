import os
import base64
import requests

from aiden.models.brain import AuditoryRequest


def load_audio_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode("utf-8")
    return encoded_string


def main():
    api_url = f'{os.environ.get("BRAIN_PROTOCOL", "http")}://{os.environ.get("BRAIN_API_HOST", "localhost")}:{os.environ.get("BRAIN_API_PORT", "8000")}/auditory/'
    default_audio_path = "./Assets/Project/Sfx/birds-chirping-75156.mp3"

    print(f"Audio path for auditory classification: {default_audio_path}")

    # Prompt user for path to audio file for input
    audio_path = (
        input("Enter new audio path to override, or press 'Enter' to use existing: ")
        or default_audio_path
    )

    audio_file = load_audio_as_base64(audio_path)

    payload = AuditoryRequest(
        config="./config/brain/default.json",
        audio=audio_file,
    ).model_dump()

    # Send a POST request to the Auditory endpoint
    print("Send sensory data to Auditory endpoint.")
    with requests.post(api_url, json=payload) as response:
        if response.status_code == 200:
            print("\nResponse from Auditory API:\n")
            print(response.json())
        else:
            print(f"Error: {response.status_code}")


if __name__ == "__main__":
    main()

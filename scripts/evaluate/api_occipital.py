"""
CLI to interact with the Brain API's occipital endpoint for evaluation purposes,
without needing to through the Unity simulation.
"""

import base64
import io
import os
import requests

from PIL import Image

from aiden.models.brain import OccipitalRequest


def load_image_as_base64(path: str) -> str:
    """
    Opens an image, converts it to PNG, and encodes it to a base64 string.

    Args:
        path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    # Open the image file
    with Image.open(path) as img:
        # Convert the image to RGBA (PNG format supports RGBA)
        img = img.convert("RGBA")
        # Prepare the image in memory as PNG
        with io.BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format="PNG")
            # Encode the PNG bytes to Base64
            return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")


def main():
    api_url = f'{os.environ.get("BRAIN_PROTOCOL", "http")}://{os.environ.get("BRAIN_API_HOST", "localhost")}:{os.environ.get("BRAIN_API_PORT", "8000")}/occipital/'
    default_image_path = "./data/samples/visual/capturedImage_202407071611410212.png"

    print(f"Image path for vision recognition: {default_image_path}")

    # Prompt user for path to image file for input
    image_path = (
        input("Enter new image path to override, or press 'Enter' to use existing: ")
        or default_image_path
    )

    image_file = load_image_as_base64(image_path)

    payload = OccipitalRequest(
        config="./config/brain/default.json",
        image=image_file,
    ).model_dump()

    # Send a POST request to the Occipital endpoint
    print("Send sensory data to Occipital endpoint.")
    with requests.post(api_url, json=payload, stream=True) as response:
        if response.status_code == 200:
            print("\nResponse from Occipital API:\n")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    print(decoded_line)
        else:
            print(f"Error: {response.status_code}")


if __name__ == "__main__":
    main()

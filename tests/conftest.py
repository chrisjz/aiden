import os
from testcontainers.core.docker_client import DockerClient
from testcontainers.ollama import OllamaContainer
from testcontainers.redis import RedisContainer
from aiden.models.brain import BrainConfig


import pytest


@pytest.fixture(scope="function")
def redis_client():
    """
    Provides a Redis client connected to a test Redis container.
    """
    with RedisContainer() as redis_container:
        client = redis_container.get_client(decode_responses=True)
        yield client


@pytest.fixture(scope="session")
def cognitive_api():
    """
    Connect to Ollama container for Cognitive API.
    """
    base_image = os.environ.get("TESTCONTAINERS_OLLAMA_IMAGE", "ollama/ollama:0.4.7")
    target_model = os.environ.get("COGNITIVE_MODEL", "llama3.2:1b")
    target_model_formatted = target_model.replace(":", "_")
    target_image = f"testcontainers_ollama/{target_model_formatted}"

    def pull_model(ollama: OllamaContainer, target_model: str) -> None:
        if target_model not in [e["name"] for e in ollama.list_models()]:
            ollama.pull_model(target_model)

    # Check existing images
    docker_client = DockerClient()
    existing_images = docker_client.client.images.list(name=target_image)

    # Load cached image of model if exists
    if existing_images:
        with OllamaContainer(image=target_image) as ollama:
            pull_model(ollama=ollama, target_model=target_model)

            yield ollama.get_endpoint()
    else:
        with OllamaContainer(image=base_image) as ollama:
            pull_model(ollama=ollama, target_model=target_model)

            # Cache the image
            ollama.commit_to_image(target_image)

            yield ollama.get_endpoint()


@pytest.fixture
def brain_config():
    return BrainConfig(
        regions={
            "broca": {
                "instruction": [
                    "Based on the auditory input, decide what to say in response."
                ],
            },
            "cortical": {
                "about": "You are an AI...",
                "description": ["Respond using the sensory data."],
                "instruction": "Please describe any thoughts based on the sensory data.",
                "personality": {
                    "traits": ["curious", "observant"],
                    "preferences": ["prefers concise responses"],
                    "boundaries": [],
                },
            },
            "occipital": {"instruction": ["What do you see?"]},
            "prefrontal": {
                "instruction": [
                    "Decide the next action based on the sensory input.",
                    "- 'move forward' if the path is clear.",
                    "- 'move backward' if there's a hazard.",
                    "- 'turn left' or 'turn_right' based on other inputs.",
                    "- 'none' if no action is needed.",
                ]
            },
            "thalamus": {
                "instruction": [
                    "Rewrite the sensory input to match a narrative structure."
                ]
            },
        },
        settings={"feature_toggles": {"personality": True}},
    )

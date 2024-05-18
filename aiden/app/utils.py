import uuid
from aiden.models.brain import BrainConfig, Sensory


import json
import os


def generate_session_id():
    """Generate a unique session ID based on UUID4."""
    return str(uuid.uuid4())


def load_brain_config(config_file: str) -> BrainConfig:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Cannot find the brain configuration file")
    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return BrainConfig(**data)


def build_sensory_input_prompt_template(sensory: Sensory):
    prompt = f"""
Your current visual input: {sensory.vision or "No visual input detected"}
Your current auditory input: {sensory.auditory or "No sounds detected"}
Your current tactile input: {sensory.tactile or "No tactile input detected"}
Your current olfactory input: {sensory.olfactory or "No smells detected"}
Your current gustatory input: {sensory.gustatory or "No taste detected"}
"""

    return prompt

from aiden.models.brain import BrainConfig, Sensory


import json
import os


def load_brain_config(config_file: str) -> BrainConfig:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Cannot find the brain configuration file")
    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return BrainConfig(**data)


def build_sensory_input_prompt_template(sensory: Sensory):
    prompt = f"""
Your current visual input: {sensory.vision or "None detected"}
Your current auditory input: {sensory.auditory or "None detected"}
Your current tactile input: {sensory.tactile or "None detected"}
Your current olfactory input: {sensory.olfactory or "None detected"}
Your current gustatory input: {sensory.gustatory or "None detected"}
"""

    return prompt

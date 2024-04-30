import datetime
from aiden.models.brain import BrainConfig, Sensory


import json
import os


def load_brain_config(config_file: str) -> BrainConfig:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Cannot find the brain configuration file")
    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return BrainConfig(**data)


def build_user_prompt_template(sensory: Sensory, brain_config: BrainConfig):
    user_prompt_template = f"""
Timestamp: {datetime.datetime.now(datetime.UTC).isoformat()}
Your current visual input: {sensory.vision}
Your current auditory input: {sensory.auditory}
Your current tactile input: {sensory.tactile}
Your current olfactory input: {sensory.olfactory}
Your current gustatory input: {sensory.gustatory}
{brain_config.action}
"""

    return user_prompt_template

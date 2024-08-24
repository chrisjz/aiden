from aiden.models.brain import AuditoryType, BrainConfig, Sensory, TactileType


import json
import os

PROMPT_LANGUAGE_PREFIX = "You hear the following spoken - "
PROMPT_ACTION_PREFIX = "You can perform the following actions - "


def load_brain_config(config_file: str) -> BrainConfig:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Cannot find the brain configuration file")
    with open(config_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return BrainConfig(**data)


def build_sensory_input_prompt_template(sensory: Sensory) -> str:
    """
    Constructs a prompt template describing the current sensory inputs.

    Args:
        sensory (Sensory): An instance of the Sensory class containing lists of sensory input objects.

    Returns:
        str: A formatted string that describes the current visual, auditory, tactile, olfactory, and gustatory inputs.
             If any sensory input list is empty, a default message indicating its absence is used.
    """
    vision_str = (
        " | ".join([input.content for input in sensory.vision])
        or "No visual input detected."
    )

    auditory_ambient_str = " | ".join(
        [
            input.content
            for input in sensory.auditory
            if input.type == AuditoryType.AMBIENT
        ]
    )
    auditory_language_str = " | ".join(
        [
            input.content
            for input in sensory.auditory
            if input.type == AuditoryType.LANGUAGE
        ]
    )

    auditory_str = (
        (auditory_ambient_str or "")
        + (" | " if auditory_ambient_str and auditory_language_str else "")
        + (
            f"{PROMPT_LANGUAGE_PREFIX}{auditory_language_str}"
            if auditory_language_str
            else ""
        )
    )
    auditory_str = auditory_str or "No sounds detected."

    tactile_general_str = " | ".join(
        [
            input.content
            for input in sensory.tactile
            if input.type == TactileType.GENERAL
        ]
    )
    tactile_action_str = ", ".join(
        [
            f"{input.command.name}"
            + (f" ({input.command.description})" if input.command.description else "")
            for input in sensory.tactile
            if input.type == TactileType.ACTION
        ]
    )

    tactile_str = (
        (tactile_general_str or "")
        + (" | " if tactile_general_str and tactile_action_str else "")
        + (f"{PROMPT_ACTION_PREFIX}{tactile_action_str}" if tactile_action_str else "")
    )
    tactile_str = tactile_str or "No tactile input detected."

    olfactory_str = (
        " | ".join([input.content for input in sensory.olfactory])
        or "No smells detected."
    )
    gustatory_str = (
        " | ".join([input.content for input in sensory.gustatory])
        or "No taste detected."
    )

    prompt = f"""
Your current visual input: {vision_str}
Your current auditory input: {auditory_str}
Your current tactile input: {tactile_str}
Your current olfactory input: {olfactory_str}
Your current gustatory input: {gustatory_str}
"""
    return prompt.strip()

from aiden.models.brain import BrainConfig


import pytest


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

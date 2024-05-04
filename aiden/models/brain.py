from typing import Optional
from pydantic import BaseModel, Field

from aiden.models.chat import Message


class FeatureToggle(BaseModel):
    personality: bool


class Personality(BaseModel):
    traits: list[str] = []
    preferences: list[str] = []
    boundaries: list[str] = []


class Sensory(BaseModel):
    vision: str = ""
    auditory: str = ""
    tactile: str = ""
    olfactory: str = ""
    gustatory: str = ""


class BrainConfig(BaseModel):
    action: str
    description: str
    instructions: list[str]
    personality: Personality
    feature_toggles: FeatureToggle


class CorticalRequest(BaseModel):
    config: str = Field(
        default="./config/brain/default.json"
    )  # TODO: pass BrainConfig instead
    sensory: Sensory
    history: Optional[list[Message]] = None

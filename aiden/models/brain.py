from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from aiden.models.chat import Message


class SimpleAction(Enum):
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    NONE = "none"


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


class Cortical(BaseModel):
    about: str
    description: list[str]
    instruction: str
    personality: Personality


class Prefrontal(BaseModel):
    instruction: list[str]


class Thalamus(BaseModel):
    instruction: list[str]


class Regions(BaseModel):
    cortical: Cortical
    prefrontal: Prefrontal
    thalamus: Thalamus


class BrainSettings(BaseModel):
    feature_toggles: FeatureToggle


class BrainConfig(BaseModel):
    regions: Regions
    settings: BrainSettings


class CorticalRequest(BaseModel):
    config: str = Field(default="./config/brain/default.json")
    sensory: Sensory
    history: Optional[list[Message]] = None

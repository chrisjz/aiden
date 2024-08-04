from enum import Enum
from typing import Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class SimpleAction(Enum):
    MOVE_FORWARD = "move forward"
    MOVE_BACKWARD = "move backward"
    TURN_LEFT = "turn left"
    TURN_RIGHT = "turn right"
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


class Broca(BaseModel):
    instruction: list[str]


class Cortical(BaseModel):
    about: str
    description: list[str]
    instruction: str
    personality: Personality


class Prefrontal(BaseModel):
    instruction: list[str]


class Occipital(BaseModel):
    instruction: list[str]


class Thalamus(BaseModel):
    instruction: list[str]


class Regions(BaseModel):
    broca: Broca
    cortical: Cortical
    occipital: Occipital
    prefrontal: Prefrontal
    thalamus: Thalamus


class BrainSettings(BaseModel):
    feature_toggles: FeatureToggle


class BrainConfig(BaseModel):
    regions: Regions
    settings: BrainSettings


class CorticalRequest(BaseModel):
    agent_id: str
    config: str = Field(default="./config/brain/default.json")
    sensory: Sensory
    history: Optional[list[BaseMessage]] = None


class OccipitalRequest(BaseModel):
    config: str = Field(default="./config/brain/default.json")
    image: str

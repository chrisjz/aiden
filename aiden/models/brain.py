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


class Cortical(BaseModel):
    about: str
    description: list[str]
    instruction: str
    personality: Personality


class Thalamus(BaseModel):
    instruction: str


class BrainSettings(BaseModel):
    feature_toggles: FeatureToggle


class Regions(BaseModel):
    cortical: Cortical
    thalamus: Thalamus


class BrainConfig(BaseModel):
    regions: Regions
    settings: BrainSettings


class CorticalRequest(BaseModel):
    config: str = Field(
        default="./config/brain/default.json"
    )  # TODO: pass BrainConfig instead
    sensory: Sensory
    history: Optional[list[Message]] = None

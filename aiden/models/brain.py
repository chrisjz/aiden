from pydantic import BaseModel, Field


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
    sensory: Sensory
    config: str = Field(
        default="./config/brain/default.json"
    )  # TODO: pass BrainConfig instead

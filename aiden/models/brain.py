from pydantic import BaseModel


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

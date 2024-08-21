from enum import Enum

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, root_validator


class BaseAction(Enum):
    MOVE_FORWARD = "move forward"
    MOVE_BACKWARD = "move backward"
    TURN_LEFT = "turn left"
    TURN_RIGHT = "turn right"
    NONE = "none"


class Action(BaseModel):
    name: str
    description: str | None = None


class FeatureToggle(BaseModel):
    personality: bool


class Personality(BaseModel):
    traits: list[str] = []
    preferences: list[str] = []
    boundaries: list[str] = []


class VisionType(Enum):
    GENERAL = "general"


class AuditoryType(Enum):
    LANGUAGE = "language"
    AMBIENT = "ambient"


class TactileType(Enum):
    GENERAL = "general"
    ACTION = "action"


class OlfactoryType(Enum):
    GENERAL = "general"


class GustatoryType(Enum):
    GENERAL = "general"


class SensoryInput(BaseModel):
    type: str
    content: str | None = None
    command: Action | None = None


class VisionInput(SensoryInput):
    type: VisionType = VisionType.GENERAL
    content: str


class AuditoryInput(SensoryInput):
    type: AuditoryType = AuditoryType.AMBIENT
    content: str


class TactileInput(SensoryInput):
    type: TactileType = TactileType.GENERAL
    content: str | None = None
    command: Action | None = None

    @root_validator(pre=True)
    def check_required_fields(cls, values):
        type_ = values.get("type")
        content = values.get("content")
        command = values.get("command")

        if type_ == TactileType.GENERAL:
            if not content:
                raise ValueError("`content` is required when type is `general`")
        elif type_ == TactileType.ACTION:
            if not command:
                raise ValueError("`command` is required when type is `action`")
        return values


class OlfactoryInput(SensoryInput):
    type: OlfactoryType = OlfactoryType.GENERAL
    content: str


class GustatoryInput(SensoryInput):
    type: GustatoryType = GustatoryType.GENERAL
    content: str


class Sensory(BaseModel):
    vision: list[VisionInput] = []
    auditory: list[AuditoryInput] = []
    tactile: list[TactileInput] = []
    olfactory: list[OlfactoryInput] = []
    gustatory: list[GustatoryInput] = []


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
    history: list[BaseMessage] | None = None


class OccipitalRequest(BaseModel):
    config: str = Field(default="./config/brain/default.json")
    image: str

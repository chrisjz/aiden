from typing import Optional, Any
from pydantic import BaseModel, Field

from aiden.models.brain import Sensory


class States(BaseModel):
    requiredStates: dict[str, Any]
    nextStates: dict[str, Any]


class Position(BaseModel):
    x: int
    y: int


class DoorPosition(BaseModel):
    entry: Position
    exit: Position


class Door(BaseModel):
    to: str
    position: DoorPosition


class Interaction(BaseModel):
    command: str
    description: str
    senses: Optional[Sensory] = Field(default_factory=Sensory)
    states: States


class Size(BaseModel):
    width: int
    height: int


class Object(BaseModel):
    name: str
    position: Position
    senses: Sensory = Field(default_factory=Sensory)
    symbol: Optional[str] = None
    initialStates: dict[str, Any]
    interactions: list[Interaction]


class Room(BaseModel):
    name: str
    position: Position
    size: Size
    objects: list[Object] = []
    doors: list[Door] = []
    senses: Sensory = Field(default_factory=Sensory)
    symbol: Optional[str] = None


class Player(BaseModel):
    position: Position
    orientation: str
    fieldOfView: int


class SceneConfig(BaseModel):
    rooms: list[Room]
    player: Player

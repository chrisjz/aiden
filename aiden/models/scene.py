from typing import Optional, Any
from pydantic import BaseModel, Field


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


class Sense(BaseModel):
    smell: str = ""
    sound: str = ""
    tactile: str = ""
    taste: str = ""
    vision: str = ""


class Interaction(BaseModel):
    command: str
    description: str
    senses: Optional[Sense] = Field(default_factory=Sense)
    states: States


class Size(BaseModel):
    width: int
    height: int


class Object(BaseModel):
    name: str
    position: Position
    senses: Sense = Field(default_factory=Sense)
    symbol: Optional[str] = None
    initialStates: dict[str, Any]
    interactions: list[Interaction]


class Room(BaseModel):
    name: str
    position: Position
    size: Size
    objects: list[Object] = []
    doors: list[Door] = []
    senses: Sense = Field(default_factory=Sense)
    symbol: Optional[str] = None


class Player(BaseModel):
    position: Position
    orientation: str
    fieldOfView: int


class SceneConfig(BaseModel):
    rooms: list[Room]
    player: Player

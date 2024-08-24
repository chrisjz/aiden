from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class BaseAction(Enum):
    MOVE_FORWARD = "move forward"
    MOVE_BACKWARD = "move backward"
    TURN_LEFT = "turn left"
    TURN_RIGHT = "turn right"


class EntityType(Enum):
    OBJECT = "object"
    ROOM = "room"


class Action(BaseModel):
    key: str
    function_name: str
    description: Optional[str] = None


class ActionList(BaseModel):
    actions: list[Action]

    def get_action_function(self, key: str) -> Optional[str]:
        # Find the action by key and return the function name if found
        action = next((action for action in self.actions if action.key == key), None)
        return action.function_name if action else None


class States(BaseModel):
    requiredStates: dict[str, Any]
    nextStates: dict[str, Any]


class Sensory(BaseModel):
    vision: str = ""
    auditory: str = ""
    tactile: str = ""
    olfactory: str = ""
    gustatory: str = ""


class Position(BaseModel):
    x: int
    y: int


class Direction(BaseModel):
    name: str
    dx: int
    dy: int


class FieldOfView(BaseModel):
    angle: int
    radius: int


class Compass(BaseModel):
    directions: dict[str, Direction]

    def get_offset(self, orientation: str) -> tuple[int, int]:
        direction = self.directions.get(orientation)
        return (direction.dx, direction.dy) if direction else (0, 0)


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
    fieldOfView: FieldOfView


class SceneConfig(BaseModel):
    rooms: list[Room]
    player: Player

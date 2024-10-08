"""
CLI to interact with the Brain API for testing purposes,
without needing to evaluate it through the Unity simulation.

This script simulates a virtual character named AIden navigating through a detailed grid representing an apartment and a garden.
Each grid square is 1 meter by 1 meter, and different objects in the scene can emit sounds, have distinct smells, tastes, and provide tactile feedback.

The grid visually represents:
- Aiden's position with an arrow indicating direction (N, E, S, W).
- Objects as "O".
- Doors as "D" to depict connections between areas.
- Room areas as "." (walkable area).
- Barriers or external boundaries as "#" (non-walkable area).

Commands:
- w: Move forward
- s: Move backward (turn 180 degrees then move forward)
- a: Turn left
- d: Turn right
- e: Perform action
- q: Quit simulation

Flags:
- --pretty: Show emojis for grid items.
- --scene: Path to the configuration file defining the scene to use.

Example Usage:
python aiden_simulation.py --pretty

This tool allows for a text-based simulation of sensory experiences in a virtual environment, making it useful for debugging and understanding the sensory data processing without a full 3D simulation.
"""

import argparse
import json
import math
import os
from typing import Any

from aiden.models.brain import (
    Action,
    AuditoryInput,
    AuditoryType,
    GustatoryInput,
    GustatoryType,
    OlfactoryInput,
    OlfactoryType,
    Sensory,
    SensoryInput,
    TactileInput,
    TactileType,
    VisionInput,
    VisionType,
)
from aiden.models.scene import (
    Action as SceneAction,
    ActionList,
    BaseAction,
    Compass,
    Direction,
    Door,
    DoorPosition,
    Interaction,
    Object,
    Position,
    Room,
    SceneConfig,
    States,
)
from aiden.models.scene import EntityType

DOOR_OBJECT_NAME = "Door"


class Scene:
    def __init__(self, config: SceneConfig):
        self.config = config
        self.rooms = {room.name: room for room in self.config.rooms}
        self.player = self.config.player
        self.player_position = (self.player.position.x, self.player.position.y)
        self.player_orientation = self.player.orientation
        self.player_fov_angle = self.player.fieldOfView.angle
        self.player_fov_radius = self.player.fieldOfView.radius
        self.object_states = {
            obj.name: obj.initialStates for room in config.rooms for obj in room.objects
        }

        self.base_actions = ActionList(
            actions=[
                SceneAction(
                    key="w",
                    function_name="move_forward",
                    description="Move player forward",
                ),
                SceneAction(
                    key="forward",
                    function_name="move_forward",
                    description="Move player forward",
                ),
                SceneAction(
                    key="move forward",
                    function_name="move_forward",
                    description="Move player forward",
                ),
                SceneAction(
                    key="s",
                    function_name="move_backward",
                    description="Move player backward",
                ),
                SceneAction(
                    key="backward",
                    function_name="move_backward",
                    description="Move player backward",
                ),
                SceneAction(
                    key="move backward",
                    function_name="move_backward",
                    description="Move player backward",
                ),
                SceneAction(
                    key="a", function_name="turn_left", description="Turn player left"
                ),
                SceneAction(
                    key="left",
                    function_name="turn_left",
                    description="Turn player left",
                ),
                SceneAction(
                    key="turn left",
                    function_name="turn_left",
                    description="Turn player left",
                ),
                SceneAction(
                    key="d", function_name="turn_right", description="Turn player right"
                ),
                SceneAction(
                    key="right",
                    function_name="turn_right",
                    description="Turn player right",
                ),
                SceneAction(
                    key="turn right",
                    function_name="turn_right",
                    description="Turn player right",
                ),
                SceneAction(
                    key="e",
                    function_name="print_object_interactions",
                    description="Check available object interactions",
                ),
                SceneAction(
                    key="inspect",
                    function_name="print_object_interactions",
                    description="Check available object interactions",
                ),
            ]
        )
        self.actions = self.base_actions
        self.current_action = None

        self.directions = Compass(
            directions={
                "N": Direction(name="North", dx=0, dy=-1),
                "E": Direction(name="East", dx=1, dy=0),
                "S": Direction(name="South", dx=0, dy=1),
                "W": Direction(name="West", dx=-1, dy=0),
            }
        )

        self.print_additional_commands = {}

        # Define mapping between brain and scene scensory models
        self.sensory_mapping = {
            "vision": (VisionInput, VisionType.GENERAL),
            "auditory": (AuditoryInput, AuditoryType.AMBIENT),
            "tactile": (TactileInput, TactileType.GENERAL),
            "olfactory": (OlfactoryInput, OlfactoryType.GENERAL),
            "gustatory": (GustatoryInput, GustatoryType.GENERAL),
        }

    def get_entity_by_position(
        self, position: tuple[int, int], entity_type: EntityType
    ) -> Room | Object | None:
        """
        Retrieve an entity by its position and type.

        Args:
            position (tuple[int, int]): The (x, y) coordinates of the position to check.
            entity_type (EntityType): The type of entity to look for (ROOM or OBJECT).

        Returns:
             Room | Object | None: The found entity (Room or Object) or None if no entity is found.
        """
        for room in self.rooms.values():
            x, y = position
            if (
                entity_type == EntityType.ROOM
                and (room.position.x <= x < room.position.x + room.size.width)
                and (room.position.y <= y < room.position.y + room.size.height)
            ):
                return room
            elif entity_type == EntityType.OBJECT:
                for obj in room.objects:
                    if (obj.position.x, obj.position.y) == position:
                        return obj
        return None

    def find_door_exit_by_entry(
        self, position: tuple[int, int]
    ) -> tuple[int, int] | None:
        """
        Find the exit position of a door given its entry position.

        Args:
            position (tuple[int, int]): The (x, y) coordinates of the door's entry position.

        Returns:
            tuple[int, int] | None: The (x, y) coordinates of the door's exit position, or None if no matching door is found.
        """
        for room in self.config.rooms:
            for door in room.doors:
                if (door.position.entry.x, door.position.entry.y) == position:
                    return (door.position.exit.x, door.position.exit.y)
        return None

    def find_object_at_position(self) -> Object:
        # Check for doors at the current position
        door_exit = self.find_door_exit_by_entry(self.player_position)
        if door_exit:
            door_initial_state = {
                "isDoor": True,
                "exitPosition": door_exit,
            }
            # Construct a door object
            object_at_position = Object(
                name=DOOR_OBJECT_NAME,
                position=self.player.position,
                initialStates=door_initial_state,
                interactions=[
                    Interaction(
                        command="enter room",
                        description="Pass through the door into another room.",
                        states=States(
                            nextStates=door_initial_state,
                            requiredStates=door_initial_state,
                        ),
                    )
                ],
            )
            # Set a state for the door
            self.object_states[DOOR_OBJECT_NAME] = door_initial_state
        else:
            # Check for objects at the current position
            object_at_position = self.get_entity_by_position(
                self.player_position, EntityType.OBJECT
            )

        return object_at_position

    def get_available_object_interactions(
        self, object: Object, toggle_print_commands: bool = False
    ) -> dict[str, Any]:
        current_states = self.object_states[object.name]
        available_interactions = [
            interaction
            for interaction in object.interactions
            if all(
                current_states.get(key) == value
                for key, value in interaction.states.requiredStates.items()
            )
        ]

        if not available_interactions:
            print(
                f"There are no available interactions with {object.name} based on its current state."
            )
            return {}

        interaction_commands = {}
        for interaction in available_interactions:
            interaction_commands[interaction.command.lower()] = interaction

            if toggle_print_commands:
                self.print_additional_commands[interaction.command.lower()] = (
                    interaction.description
                )

        return interaction_commands

    def execute_interaction(
        self, object_at_position: Object, chosen_interaction: Interaction
    ) -> None:
        """
        Execute the chosen interaction on the object at the given position,
        updating the object's states and printing sensory feedback.

        Args:
            object_at_position (Object): The object on which the interaction is performed.
            chosen_interaction (Interaction): The interaction to be executed.

        Returns:
            None
        """
        next_states = chosen_interaction.states.nextStates
        current_states = self.object_states[object_at_position.name]
        current_states.update(next_states)
        senses = chosen_interaction.senses
        print(f"Executed '{chosen_interaction.command}':")
        print(f"Vision: {senses.vision}")
        print(f"Auditory: {senses.auditory}")
        print(f"Tactile: {senses.tactile}")
        print(f"Olfactory: {senses.olfactory}")
        print(f"Gustatory: {senses.gustatory}")

        # Special handling of traversing doors
        if object_at_position.name == DOOR_OBJECT_NAME:
            door_exit_position = object_at_position.initialStates["exitPosition"]
            self.player_position = door_exit_position
            print(f"You open the door and step through to {door_exit_position}")

    def print_object_interactions(self) -> None:
        object_at_position = self.find_object_at_position()

        if not object_at_position:
            print("There is nothing here to interact with.")
            return

        self.get_available_object_interactions(
            object_at_position, toggle_print_commands=True
        )

    def interact_with_object(self) -> None:
        object_at_position: Object | None = self.find_object_at_position()

        if not object_at_position:
            print("Could not find object to interact with.")
            return

        interaction_commands = self.get_available_object_interactions(
            object_at_position, toggle_print_commands=False
        )

        chosen_interaction = interaction_commands.get(self.current_action, None)

        if not chosen_interaction:
            print(
                f"Could not find interaction `{self.current_action}` for object `{object_at_position.name}`."
            )
            return

        self.execute_interaction(object_at_position, chosen_interaction)

    def find_available_object_interactions(self) -> dict[str, Any] | None:
        object_at_position = self.find_object_at_position()

        if not object_at_position:
            return

        interaction_commands = self.get_available_object_interactions(
            object_at_position, toggle_print_commands=False
        )

        return interaction_commands

    def update_sensory_data(self) -> Sensory:
        """
        Update the sensory data based on the player's current position, room, and visible objects.

        Returns:
            Sensory: A new Sensory instance filled with the combined sensory data.
        """
        current_room = self.get_entity_by_position(
            self.player_position, EntityType.ROOM
        )
        current_object = self.get_entity_by_position(
            self.player_position, EntityType.OBJECT
        )
        visible_entities = self.get_field_of_view()

        # Initialize default senses
        combined_senses = Sensory()

        # Add default actions
        combined_senses.tactile = [
            TactileInput(type=TactileType.ACTION, command=Action(name=action.value))
            for action in BaseAction
        ]

        # Combine room senses if present
        if current_room:
            room_senses = current_room.senses
            for field, (input_class, default_type) in self.sensory_mapping.items():
                sense_value = getattr(room_senses, field)
                if sense_value:
                    getattr(combined_senses, field).append(
                        input_class(type=default_type, content=sense_value)
                    )

        # Handle current object senses
        if current_object:
            self.add_object_senses(
                current_object, self.object_states[current_object.name], combined_senses
            )

        # Combine senses from visible entities, considering their current state
        for entity, pos in visible_entities:
            if (
                isinstance(entity, Object) and entity != current_object
            ):  # Avoid duplicating the current object's senses
                distance_description = self.describe_relative_position(entity.name, pos)
                self.add_object_senses(
                    entity,
                    self.object_states[entity.name],
                    combined_senses,
                    distance_description,
                )
            elif (
                isinstance(entity, Door) and pos[0] != 0
            ):  # Doors at player handled lower down in this function
                distance_description = self.describe_relative_position("Door", pos)
                combined_senses.vision.append(
                    VisionInput(type=VisionType.GENERAL, content=distance_description)
                )

        # Add to vision if player is at a door
        if self.find_door_exit_by_entry(self.player_position):
            combined_senses.vision.append(
                VisionInput(
                    type=VisionType.GENERAL,
                    content="You are at a door which leads to another room.",
                )
            )
        # Add to vision if a boundary is in front of the player
        else:
            dx, dy = self.directions.get_offset(self.player_orientation)
            new_position = (self.player_position[0] + dx, self.player_position[1] + dy)
            if not self.is_position_within_room(new_position):
                combined_senses.vision.append(
                    VisionInput(
                        type=VisionType.GENERAL,
                        content="There is an impassable barrier in front of you.",
                    )
                )

                # Remove the "move forward" action from tactile inputs
                combined_senses.tactile = [
                    tactile_input
                    for tactile_input in combined_senses.tactile
                    if tactile_input.command is None
                    or tactile_input.command.name != BaseAction.MOVE_FORWARD.value
                ]

        # Add to tactile any available object interactions
        if interactions := self.find_available_object_interactions():
            for interaction in interactions:
                combined_senses.tactile.append(
                    TactileInput(
                        type=TactileType.ACTION, command=Action(name=interaction)
                    )
                )

        # Return a new Sensory instance filled with the combined sensory data
        return combined_senses

    def add_object_senses(
        self,
        obj: Object,
        current_states: dict[str, bool],
        combined_senses: Sensory,
        distance_description: str | None = None,
    ) -> None:
        """
        Update the combined senses based on the object's default senses and its interaction-specific senses.

        Args:
            obj (Object): The object whose senses are being considered.
            current_states (dict[str, bool]): The current states of the object.
            combined_senses Sensory: The dictionary to update with the combined senses.
            distance_description str | None: The distance description to append to the vision sense.
        """
        matched_senses = obj.senses  # Start with default object senses

        # Check if any interactions' conditions are met to update senses
        for interaction in obj.interactions:
            if all(
                current_states.get(state) == value
                for state, value in interaction.states.nextStates.items()
            ):
                matched_senses = (
                    interaction.senses
                )  # Update senses to interaction-specific
                break

        # Combining sensory data based on matched senses
        for field, (input_class, default_type) in self.sensory_mapping.items():
            sense_value = getattr(matched_senses, field)
            if sense_value:
                getattr(combined_senses, field).append(
                    input_class(type=default_type, content=sense_value)
                )

        # Append distance description to vision if provided
        if distance_description:
            combined_senses.vision.append(
                VisionInput(type=VisionType.GENERAL, content=distance_description)
            )

    def process_action(self, command: str):
        # Used only for actions related to object interactions
        self.current_action = command

        # Append any available object interactions to base actions
        available_interactions: list[Interaction] = (
            self.find_available_object_interactions()
        )
        if available_interactions:
            available_actions = self.base_actions
            for available_command in available_interactions:
                interaction = available_interactions[available_command]
                object_action = SceneAction(
                    key=interaction.command,
                    function_name="interact_with_object",
                    description=interaction.description,
                )
                available_actions.actions.append(object_action)
            self.actions = available_actions
        else:
            self.actions = self.base_actions

        function_name = self.actions.get_action_function(command)
        if function_name:
            method = getattr(self, function_name, None)
            if method:
                method()
            else:
                print(f"No method found for the command: {command}")
        else:
            print(f"Invalid command: {command}")

    def move_forward(self):
        dx, dy = self.directions.get_offset(self.player_orientation)
        new_position = (self.player_position[0] + dx, self.player_position[1] + dy)
        if self.is_position_within_room(new_position):
            self.player_position = new_position
        else:
            print("Move blocked by environment boundaries.")

    def move_backward(self):
        dx, dy = self.directions.get_offset(self.player_orientation)
        new_position = (self.player_position[0] - dx, self.player_position[1] - dy)
        if self.is_position_within_room(new_position):
            self.player_position = new_position
        else:
            print("Move blocked by environment boundaries.")

    def turn_left(self):
        orientation_order = ["N", "W", "S", "E"]  # Anti-clockwise rotation
        self.player_orientation = orientation_order[
            (orientation_order.index(self.player_orientation) + 1) % 4
        ]

    def turn_right(self):
        orientation_order = ["N", "E", "S", "W"]  # Clockwise rotation
        self.player_orientation = orientation_order[
            (orientation_order.index(self.player_orientation) + 1) % 4
        ]

    def is_position_within_room(self, position: tuple[int, int]) -> bool:
        """
        Check if a given position is within any room in the scene.

        Args:
            position (tuple[int, int]): The (x, y) coordinates of the position to check.

        Returns:
            bool: True if the position is within any room, False otherwise.
        """
        return any(
            room.position.x <= position[0] < room.position.x + room.size.width
            and room.position.y <= position[1] < room.position.y + room.size.height
            for room in self.rooms.values()
        )

    def get_entity_relative_position_by_player_orientation(
        self, nx: int, ny: int
    ) -> tuple[int, int]:
        """
        Calculate the relative position of an entity based on the player's orientation.

        Args:
            nx (int): The x-coordinate of the entity.
            ny (int): The y-coordinate of the entity.

        Returns:
            tuple[int, int]: The relative position (dx, dy) of the entity from the player's current position.
        """
        if self.player_orientation == "N":
            relative_position = (
                self.player_position[1] - ny,
                nx - self.player_position[0],
            )
        elif self.player_orientation == "E":
            relative_position = (
                nx - self.player_position[0],
                ny - self.player_position[1],
            )
        elif self.player_orientation == "S":
            relative_position = (
                ny - self.player_position[1],
                self.player_position[0] - nx,
            )
        elif self.player_orientation == "W":
            relative_position = (
                self.player_position[0] - nx,
                self.player_position[1] - ny,
            )

        return relative_position

    def get_field_of_view(self) -> list[tuple[Door | Object, tuple[int, int]]]:
        """
        Calculate the grids in AIden's field of view based on his orientation and view distance.

        Returns:
            list[tuple[Door | Object, tuple[int, int]]]: A list of tuples where each tuple contains a door or object,
                                                and its relative position to the player.
        """
        visible_entities = []
        checked_positions = set()

        # Define the angle for the field of view
        fov_angle = self.player_fov_angle  # X degrees to each side
        fov_radius = self.player_fov_radius

        # Calculate the range of positions within the cone
        for i in range(1, fov_radius + 1):
            for angle in range(-fov_angle, fov_angle + 1):
                radians = math.radians(angle)
                if self.player_orientation == "N":
                    nx = self.player_position[0] - int(i * math.sin(radians))
                    ny = self.player_position[1] - int(i * math.cos(radians))
                elif self.player_orientation == "E":
                    nx = self.player_position[0] + int(i * math.cos(radians))
                    ny = self.player_position[1] - int(i * math.sin(radians))
                elif self.player_orientation == "S":
                    nx = self.player_position[0] - int(i * math.sin(radians))
                    ny = self.player_position[1] + int(i * math.cos(radians))
                elif self.player_orientation == "W":
                    nx = self.player_position[0] - int(i * math.cos(radians))
                    ny = self.player_position[1] - int(i * math.sin(radians))
                else:
                    continue  # Skip invalid orientation

                if (nx, ny) in checked_positions:
                    continue  # Skip already checked positions

                if not self.is_position_within_room((nx, ny)):
                    continue  # Skip positions outside the room

                if self.get_entity_by_position(
                    self.player_position, EntityType.ROOM
                ) != self.get_entity_by_position((nx, ny), EntityType.ROOM):
                    continue  # Skip if entity is not in the same room as player

                checked_positions.add((nx, ny))
                obj = self.get_entity_by_position((nx, ny), EntityType.OBJECT)
                if obj:
                    relative_position = (
                        self.get_entity_relative_position_by_player_orientation(nx, ny)
                    )
                    visible_entities.append((obj, relative_position))
                    continue

                door_exit_position = self.find_door_exit_by_entry((nx, ny))
                if door_exit_position:
                    relative_position = (
                        self.get_entity_relative_position_by_player_orientation(nx, ny)
                    )
                    room = self.get_entity_by_position((nx, ny), EntityType.ROOM)
                    door = Door(
                        to=room.name,
                        position=DoorPosition(
                            entry=Position(
                                x=nx,
                                y=ny,
                            ),
                            exit=Position(
                                x=door_exit_position[0],
                                y=door_exit_position[1],
                            ),
                        ),
                    )
                    visible_entities.append((door, relative_position))

        return visible_entities

    def describe_relative_position(
        self, name: str, relative_position: tuple[int, int]
    ) -> str:
        """
        Describe the relative position of an object based on its name and relative coordinates.

        Args:
            name (str): The name of the object.
            relative_position (tuple[int, int]): The relative position of the object as (x, y) coordinates.

        Returns:
            str: A description of the object's relative position to the user.
        """
        x, y = relative_position
        distance = math.sqrt(x**2 + y**2)
        angle = math.degrees(math.atan2(y, x))

        # Determine the direction based on the adjusted angle
        if -22.5 <= angle < 22.5:
            direction = "in front"
        elif 22.5 <= angle < 67.5:
            direction = "in front-right"
        elif 67.5 <= angle < 112.5:
            direction = "to the right"
        elif 112.5 <= angle < 157.5:
            direction = "back-right"
        elif angle >= 157.5 or angle < -157.5:
            direction = "behind"
        elif -157.5 <= angle < -112.5:
            direction = "back-left"
        elif -112.5 <= angle < -67.5:
            direction = "to the left"
        elif -67.5 <= angle < -22.5:
            direction = "in front-left"

        return f"The {name} is {distance:.1f} meters {direction}."

    def _convert_sensory_data_to_string(
        self, sensory_list: list[SensoryInput, TactileInput]
    ) -> str:
        """
        Converts a list of sensory input objects to a single formatted string.

        Args:
            sensory_list (list[SensoryInput]): A list of sensory input objects (e.g., VisionInput, AuditoryInput, TactileInput).

        Returns:
            str: A formatted string where each sensory input is represented as '[Type] Content',
                with multiple inputs separated by ' | '. For TactileInput of type 'action', it uses the command instead of content.
        """
        result = []
        for item in sensory_list:
            if (
                isinstance(item, TactileInput)
                and item.type == TactileType.ACTION
                and item.command
            ):
                description_output = (
                    f" - {item.command.description}" if item.command.description else ""
                )
                result.append(
                    f"[{item.type.value.capitalize()}] {item.command.name}{description_output}"
                )
            else:
                result.append(f"[{item.type.value.capitalize()}] {item.content}")

        return " | ".join(result)

    def print_scene(self, pretty: bool):
        max_x = max(
            (room.position.x + room.size.width for room in self.rooms.values()),
            default=0,
        )
        max_y = max(
            (room.position.y + room.size.height for room in self.rooms.values()),
            default=0,
        )
        grid = [[" " for _ in range(max_x)] for _ in range(max_y)]

        for y in range(max_y):
            for x in range(max_x):
                char = " "
                if (x, y) == self.player_position:
                    # Choose arrow based on orientation
                    if (x, y) == self.player_position:
                        arrows = (
                            {"N": "⬆️ ", "E": "➡️ ", "S": "⬇️ ", "W": "⬅️ "}
                            if pretty
                            else {"N": "^", "E": ">", "S": "v", "W": "<"}
                        )
                        char = arrows[self.player_orientation]
                    else:
                        arrows = {"N": "^", "E": ">", "S": "v", "W": "<"}
                        char = arrows[self.player_orientation]
                elif obj := self.get_entity_by_position((x, y), EntityType.OBJECT):
                    char = (
                        obj.symbol if obj.symbol and pretty else "❓" if pretty else "?"
                    )
                elif self.find_door_exit_by_entry((x, y)):
                    char = "🚪" if pretty else "D"
                elif room := self.get_entity_by_position((x, y), EntityType.ROOM):
                    empty_symbol = room.symbol if room.symbol else "⬜"
                    char = empty_symbol if pretty else "."
                else:
                    char = "⬛" if pretty else "#"  # Barriers or boundaries
                grid[y][x] = char

        for row in grid:
            separator = "" if pretty else " "
            print(separator.join(row))

        print(f"Player position: {self.player_position}")
        print(f"Player orientation: {self.player_orientation}")

        current_room = self.get_entity_by_position(
            self.player_position, EntityType.ROOM
        )
        current_object = self.get_entity_by_position(
            self.player_position, EntityType.OBJECT
        )

        if current_object:
            print(f"Now at: {current_object.name}")
        elif current_room:
            print(f"Now in: {current_room.name}")
        else:
            "Player is outside any room"

        sensory_data = (
            self.update_sensory_data()
        )  # Update sensory data after each command

        print(f"Vision: {self._convert_sensory_data_to_string(sensory_data.vision)}")
        print(
            f"Auditory: {self._convert_sensory_data_to_string(sensory_data.auditory)}"
        )
        print(f"Tactile: {self._convert_sensory_data_to_string(sensory_data.tactile)}")
        print(
            f"Olfactory: {self._convert_sensory_data_to_string(sensory_data.olfactory)}"
        )
        print(
            f"Gustatory: {self._convert_sensory_data_to_string(sensory_data.gustatory)}"
        )
        print()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the AIden simulation with a specific scene configuration."
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Enable emoji representations of grid components.",
    )
    parser.add_argument(
        "--scene",
        type=str,
        default="./config/scenes/default.json",
        help="Path to the scene configuration file.",
    )
    return parser.parse_args()


def load_scene(scene_file: str) -> SceneConfig:
    if not os.path.exists(scene_file):
        raise FileNotFoundError("Cannot find the scene configuration file")
    with open(scene_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return SceneConfig(**data)


def main(args) -> None:
    scene_config = load_scene(args.scene)
    env = Scene(scene_config)
    print("Initial scene:")
    env.print_scene(args.pretty)

    while True:
        additional_commands = ""
        if env.print_additional_commands:
            print("Interaction commands available:")
            for cmd in env.print_additional_commands:
                print(f"{cmd}: {env.print_additional_commands[cmd]}")
            print()

            additional_commands = ", ".join(env.print_additional_commands.keys()) + ", "
            env.print_additional_commands = {}

        command_prompt = (
            f"Enter command (w, a, s, d, e, {additional_commands}q to quit): "
        )

        command = input(command_prompt).strip().lower()
        if command == "q":
            break

        env.process_action(command)
        print(f"Action executed: {env.actions.get_action_function(command)}")
        env.print_scene(args.pretty)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)

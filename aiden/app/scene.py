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
import os

from aiden.models.brain import SensoryData
from aiden.models.scene import SceneConfig


class Scene:
    def __init__(self, config: SceneConfig):
        self.config = config
        self.rooms = {room.name: room for room in self.config.rooms}
        self.player = self.config.player
        self.player_position = (self.player.position.x, self.player.position.y)
        self.player_orientation = self.player.orientation
        self.player_view_distance = self.player.fieldOfView
        self.object_states = {
            obj.name: obj.initialStates for room in config.rooms for obj in room.objects
        }

        self.actions = {
            "w": "move_player",
            "s": "move_backward",
            "a": "turn_left",
            "d": "turn_right",
            "e": "interact_with_object",
            "forward": "move_player",
            "backward": "move_backward",
            "left": "turn_left",
            "right": "turn_right",
            "use": "interact_with_object",
        }

        self.directions = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

    def get_entity_by_position(self, position: tuple[int, int], entity_type: str):
        for room in self.rooms.values():
            x, y = position
            if (
                entity_type == "room"
                and (room.position.x <= x < room.position.x + room.size.width)
                and (room.position.y <= y < room.position.y + room.size.height)
            ):
                return room
            elif entity_type == "object":
                for obj in room.objects:
                    if (obj.position.x, obj.position.y) == position:
                        return obj
        return None

    def find_door_exit_by_entry(self, position: tuple[int, int]):
        for room in self.config.rooms:
            for door in room.doors:
                if (door.position.entry.x, door.position.entry.y) == position:
                    return (door.position.exit.x, door.position.exit.y)
        return None

    def interact_with_object(self):
        # Check for doors at the current position
        door_exit = self.find_door_exit_by_entry(self.player_position)
        if door_exit:
            self.player_position = door_exit
            print(f"You open the door and step through to {door_exit}")
            return

        # Check for objects at the current position
        object_at_position = self.get_entity_by_position(self.player_position, "object")
        if object_at_position:
            current_states = self.object_states[object_at_position.name]
            available_interactions = [
                interaction
                for interaction in object_at_position.interactions
                if all(
                    current_states.get(key) == value
                    for key, value in interaction.states.requiredStates.items()
                )
            ]

            if not available_interactions:
                print(
                    f"There are no available interactions with {object_at_position.name} based on its current state."
                )
                return

            print(f"Interacting with {object_at_position.name}. Available commands:")
            interaction_dict = {}
            for index, interaction in enumerate(available_interactions, start=1):
                print(f"{index}. {interaction.command}: {interaction.description}")
                interaction_dict[str(index)] = interaction
                interaction_dict[interaction.command.lower()] = interaction

            print("Type 'exit' to stop interacting or enter the number or command.")

            while True:
                chosen_input = (
                    input("Choose a command to execute or type 'exit': ")
                    .strip()
                    .lower()
                )
                if chosen_input == "exit":
                    print("Exiting interaction mode.")
                    return

                chosen_interaction = interaction_dict.get(chosen_input, None)
                if chosen_interaction:
                    next_states = chosen_interaction.states.nextStates
                    current_states.update(next_states)
                    senses = chosen_interaction.senses
                    print(f"Executed '{chosen_interaction.command}':")
                    print(f"Vision: {senses.vision}")
                    print(f"Sound: {senses.sound}")
                    print(f"Smell: {senses.smell}")
                    print(f"Taste: {senses.taste}")
                    print(f"Tactile: {senses.tactile}")
                    return
                else:
                    print("No such command available or conditions not met.")
        else:
            print("There is nothing here to interact with.")

    def update_sensory_data(self) -> SensoryData:
        current_room = self.get_entity_by_position(self.player_position, "room")
        current_object = self.get_entity_by_position(self.player_position, "object")
        visible_objects = self.get_field_of_view()

        # Initialize default senses
        combined_senses = {
            "vision": "",
            "sound": "",
            "tactile": "",
            "smell": "",
            "taste": "",
        }

        # Combine room senses if present
        if current_room:
            room_senses = current_room.senses
            for key in combined_senses.keys():
                combined_senses[key] += room_senses.__dict__[key]

        # Handle current object senses
        if current_object:
            self.add_object_senses(
                current_object, self.object_states[current_object.name], combined_senses
            )

        # Combine senses from visible objects, considering their current state
        for obj in visible_objects:
            if obj != current_object:  # Avoid duplicating the current object's senses
                self.add_object_senses(
                    obj, self.object_states[obj.name], combined_senses
                )

        # Return a new SensoryData instance filled with the combined sensory data
        return SensoryData(
            vision=combined_senses["vision"].strip(),
            auditory=combined_senses["sound"].strip(),
            tactile=combined_senses["tactile"].strip(),
            smell=combined_senses["smell"].strip(),
            taste=combined_senses["taste"].strip(),
        )

    def add_object_senses(self, obj, current_states, combined_senses):
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
        for sense_key in combined_senses.keys():
            sense_value = getattr(matched_senses, sense_key)
            if sense_value:
                combined_senses[sense_key] += " | " + sense_value

    def process_action(self, command: str):
        method = self.actions.get(command)
        if method:
            getattr(self, method)()
        else:
            print("Invalid command!")

    def move_player(self):
        dx, dy = self.directions[self.player_orientation]
        new_position = (self.player_position[0] + dx, self.player_position[1] + dy)
        if self.is_position_within_room(new_position):
            self.player_position = new_position
        else:
            print("Move blocked by environment boundaries.")

    def move_backward(self):
        dx, dy = self.directions[self.player_orientation]
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

    def is_position_within_room(self, position):
        return any(
            room.position.x <= position[0] < room.position.x + room.size.width
            and room.position.y <= position[1] < room.position.y + room.size.height
            for room in self.rooms.values()
        )

    def get_field_of_view(self):
        """Calculate the grids in Aiden's field of view based on his orientation and view distance."""
        dx, dy = self.directions[self.player_orientation]
        visible_objects = []
        for i in range(1, self.player_view_distance + 1):
            nx, ny = self.player_position[0] + i * dx, self.player_position[1] + i * dy
            if not self.is_position_within_room((nx, ny)):
                break  # Stop scanning if an obstruction or boundary is reached
            obj = self.get_entity_by_position((nx, ny), "object")
            if obj:
                visible_objects.append(obj)
        return visible_objects

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
                            {"N": "⬆️", "E": "➡️", "S": "⬇️", "W": "⬅️"}
                            if pretty
                            else {"N": "^", "E": ">", "S": "v", "W": "<"}
                        )
                        char = arrows[self.player_orientation]
                    else:
                        arrows = {"N": "^", "E": ">", "S": "v", "W": "<"}
                        char = arrows[self.player_orientation]
                elif self.get_entity_by_position((x, y), "object"):
                    char = "O"
                elif self.find_door_exit_by_entry((x, y)):
                    char = "D"
                elif self.get_entity_by_position((x, y), "room"):
                    char = "."
                else:
                    char = "#"  # Barriers or boundaries
                grid[y][x] = char

        for row in grid:
            print(" ".join(row))

        print(f"Player position: {self.player_position}")
        print(f"Player orientation: {self.player_orientation}")

        current_room = self.get_entity_by_position(self.player_position, "room")
        current_object = self.get_entity_by_position(self.player_position, "object")

        if current_object:
            print(f"Now at: {current_object.name}")
        elif current_room:
            print(f"Now in: {current_room.name}")
        else:
            "Player is outside any room"

        sensory_data = (
            self.update_sensory_data()
        )  # Update sensory data after each command

        print(f"Vision: {sensory_data.vision}")
        print(f"Sound: {sensory_data.auditory}")
        print(f"Smell: {sensory_data.smell}")
        print(f"Taste: {sensory_data.taste}")
        print(f"Tactile: {sensory_data.tactile}")
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
        command = input("Enter command (w, a, s, d, e, q to quit): ").strip().lower()
        if command == "q":
            break

        env.process_action(command)
        print(f"Action executed: {env.actions.get(command, '')}")
        env.print_scene(args.pretty)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)

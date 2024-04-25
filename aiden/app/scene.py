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
- --show-position: If present, displays the grid and Aiden's position after each command.
- --verbose: If present, prints detailed actions of Aiden's experiences and senses after each move.

Example Usage:
python aiden_simulation.py --verbose --show-position

This tool allows for a text-based simulation of sensory experiences in a virtual environment, making it useful for debugging and understanding the sensory data processing without a full 3D simulation.
"""

import argparse
import json
import os

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
            "w": "forward",
            "s": "backward",
            "a": "left",
            "d": "right",
            "e": "use",
        }

    def find_room_by_position(self, position: tuple[int, int]):
        for room_name, room in self.rooms.items():
            x, y = position
            room_pos = room.position
            room_size = room.size
            if (
                room_pos.x <= x < room_pos.x + room_size.width
                and room_pos.y <= y < room_pos.y + room_size.height
            ):
                return room
        return None

    def find_object_by_position(self, position: tuple[int, int]):
        for room_name, room in self.rooms.items():
            for obj in room.objects:
                obj_x = obj.position.x
                obj_y = obj.position.y
                if (obj_x, obj_y) == position:
                    return obj
        return None

    def find_door_exit_by_entry(self, position: tuple[int, int]):
        for room in self.config.rooms:
            for door in room.doors:
                entry = door.position.entry
                exit = door.position.exit
                if (entry.x, entry.y) == position:
                    return (exit.x, exit.y)
        return None

    def interact_with_object(self):
        # Check for doors at the current position
        door_exit = self.find_door_exit_by_entry(self.player_position)
        if door_exit:
            self.player_position = door_exit
            print(f"You open the door and step through to {door_exit}")
            return

        # Check for objects at the current position
        object_at_position = self.find_object_by_position(self.player_position)
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

    def move_player(self, command: str) -> None:
        if command in ("forward", "w"):
            self.advance()
        elif command in ("backward", "s"):
            self.turn_around()
            self.advance()
        elif command in ("left", "a"):
            self.turn_left()
        elif command in ("right", "d"):
            self.turn_right()
        elif command in ("use", "e"):
            self.interact_with_object()
        else:
            print("Unknown command!")

    def turn_around(self):
        self.player_orientation = {"N": "S", "S": "N", "E": "W", "W": "E"}[
            self.player_orientation
        ]

    def turn_left(self):
        self.player_orientation = {"N": "W", "W": "S", "S": "E", "E": "N"}[
            self.player_orientation
        ]

    def turn_right(self):
        self.player_orientation = {"N": "E", "E": "S", "S": "W", "W": "N"}[
            self.player_orientation
        ]

    def advance(self):
        direction_offset = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        dx, dy = direction_offset[self.player_orientation]
        new_x = self.player_position[0] + dx
        new_y = self.player_position[1] + dy
        new_position = (new_x, new_y)

        if self.is_position_within_room(new_position):
            self.player_position = new_position
        else:
            print("Move blocked by environment boundaries.")

    def is_position_within_room(self, position: tuple[int, int]):
        for room in self.config.rooms:
            room_position = room.position
            room_size = room.size
            if (
                room_position.x <= position[0] < room_position.x + room_size.width
            ) and (room_position.y <= position[1] < room_position.y + room_size.height):
                return True
        return False

    def get_field_of_view(self):
        """Calculate the grids in Aiden's field of view based on his orientation and view distance."""
        directions = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        dx, dy = directions[self.player_orientation]
        visible_objects = []
        for i in range(1, self.player_view_distance + 1):
            nx, ny = self.player_position[0] + i * dx, self.player_position[1] + i * dy
            if not self.is_position_within_room(
                (nx, ny)
            ):  # Check for obstructions and room boundaries
                break  # Stop scanning if an obstruction or boundary is reached
            obj = self.find_object_by_position((nx, ny))
            if obj:
                visible_objects.append(obj)
        return visible_objects

    def print_scene(self, pretty: bool):
        print(
            f"Player's Position: {self.player_position}, Orientation: {self.player_orientation}"
        )
        current_room = self.find_room_by_position(self.player_position)
        current_object = self.find_object_by_position(self.player_position)
        visible_objects = self.get_field_of_view()

        # Combine the vision descriptions
        room_vision = current_room.senses.vision if current_room else "nothing"
        objects_vision = [
            obj.senses.vision for obj in visible_objects if obj.senses.vision
        ]

        # Include current object's vision if present
        if current_object and "vision" in current_object.senses:
            current_object_vision = current_object.senses.vision
            objects_vision.insert(
                0, current_object_vision
            )  # Prepend to make it more prominent

        # Construct the full vision string
        full_vision = (
            f"{room_vision}. Visible objects: {', '.join(objects_vision)}"
            if objects_vision
            else room_vision
        )

        # Prepare to display the grid with Aiden's position and orientation
        max_x = (
            max(room.position.x + room.size.width for room in self.rooms.values()) + 1
        )
        max_y = (
            max(room.position.y + room.size.height for room in self.rooms.values()) + 1
        )

        # Display grid with Aiden's position and orientation
        for y in range(max_y):
            for x in range(max_x):
                if (x, y) == self.player_position:
                    orientation_char = {
                        "N": "⬆️" if pretty else "^",
                        "E": "➡️" if pretty else ">",
                        "S": "⬇️" if pretty else "v",
                        "W": "⬅️" if pretty else "<",
                    }[self.player_orientation]
                    print(f"{orientation_char} ", end="")
                else:
                    room = self.find_room_by_position((x, y))
                    if room:
                        printed = False
                        # Check for objects and print their symbols
                        for obj in room.objects:
                            if obj.position.x == x and obj.position.y == y:
                                print(
                                    obj.symbol
                                    if obj.symbol and pretty
                                    else "❓"
                                    if pretty
                                    else "? ",
                                    end="",
                                )
                                printed = True
                                break
                        if not printed:  # No object at this position
                            # Check for doors and print door symbol
                            if any(
                                door.position.entry.x == x
                                and door.position.entry.y == y
                                for door in room.doors
                            ):
                                print("🚪" if pretty else "D ", end="")
                            else:
                                # Print the room's specified empty space symbol or a default symbol
                                empty_symbol = room.symbol if room.symbol else "⬜"
                                print(empty_symbol if pretty else ". ", end="")
                    else:
                        # Print a hash for barriers or outside the room boundaries
                        print("⬛" if pretty else "# ", end="")
            print()  # New line after each row

        # Sensory feedback based on Aiden's position
        if current_object:
            senses = current_object.senses
            print(f"Now at: {current_object.name}")
        else:
            senses = current_room.senses if current_room else {}
            print(
                f"Now in: {current_room.name}"
                if current_room
                else "Player is outside any room"
            )

        print(f"Vision: {full_vision}")
        print(f"Sound: {senses.sound}")
        print(f"Smell: {senses.smell}")
        print(f"Taste: {senses.taste}")
        print(f"Tactile: {senses.tactile}")
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
    parser.add_argument(
        "--show-position",
        action="store_true",
        help="Display the grid and player's position after each command.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed actions of player's experience.",
    )
    args = parser.parse_args()
    return args


def load_scene(scene_file: str) -> SceneConfig:
    if not os.path.exists(scene_file):
        raise FileNotFoundError("Cannot find the scene configuration file")
    with open(scene_file, "r", encoding="utf8") as f:
        data = json.load(f)
    return SceneConfig(**data)


def main(scene_file: str, pretty: bool, show_position: bool, verbose: bool) -> None:
    scene_config = load_scene(scene_file)
    env = Scene(scene_config)
    print("Initial scene:")
    if show_position:
        env.print_scene(pretty)

    while True:
        command = input("Enter command (w, a, s, d, e, q to quit): ").strip().lower()
        if command == "q":
            break
        else:
            env.move_player(command)
            if verbose:
                print(f"Action executed: {env.actions.get(command, '')}")
                print(f"Player orientation: {env.player_orientation}")
            if show_position:
                env.print_scene(pretty)


if __name__ == "__main__":
    args = parse_arguments()
    main(args.scene, args.pretty, args.show_position, args.verbose)

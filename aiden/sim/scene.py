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
- q: Quit simulation

Flags:
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


class Scene:
    def __init__(self, scene_file: str):
        if not os.path.exists(scene_file):
            raise FileNotFoundError("Cannot find the scene configuration file")

        with open(scene_file, "r") as f:
            self.config = json.load(f)

        self.rooms = {room["name"]: room for room in self.config["rooms"]}
        self.directions = {"w": "forward", "s": "backward", "a": "left", "d": "right"}
        self.aiden_position = (1, 1)  # Initialize Aiden's position
        self.aiden_orientation = "N"  # Initialize orientation

    def find_room_by_position(self, position: tuple[int, int]):
        for room_name, room in self.rooms.items():
            x, y = position
            room_pos = room["position"]
            room_size = room["size"]
            if (
                room_pos["x"] <= x < room_pos["x"] + room_size["width"]
                and room_pos["y"] <= y < room_pos["y"] + room_size["height"]
            ):
                return room
        return None

    def find_object_by_position(self, position: tuple[int, int]):
        for room_name, room in self.rooms.items():
            for obj in room.get("objects", []):
                obj_x = obj["position"]["x"]
                obj_y = obj["position"]["y"]
                if (obj_x, obj_y) == position:
                    return obj
        return None

    def move_aiden(self, command: str) -> None:
        if command == "w":
            self.advance()
        elif command == "s":
            self.turn_around()
            self.advance()
        elif command == "a":
            self.turn_left()
        elif command == "d":
            self.turn_right()

    def turn_around(self):
        self.aiden_orientation = {"N": "S", "S": "N", "E": "W", "W": "E"}[
            self.aiden_orientation
        ]

    def turn_left(self):
        self.aiden_orientation = {"N": "W", "W": "S", "S": "E", "E": "N"}[
            self.aiden_orientation
        ]

    def turn_right(self):
        self.aiden_orientation = {"N": "E", "E": "S", "S": "W", "W": "N"}[
            self.aiden_orientation
        ]

    def advance(self):
        direction_offset = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        dx, dy = direction_offset[self.aiden_orientation]
        new_x = self.aiden_position[0] + dx
        new_y = self.aiden_position[1] + dy
        new_position = (new_x, new_y)

        if self.is_position_within_room(new_position):
            self.aiden_position = new_position
        else:
            print("Move blocked by environment boundaries.")

    def is_position_within_room(self, position: tuple[int, int]):
        for room in self.config["rooms"]:
            room_position = room["position"]
            room_size = room["size"]
            if (
                room_position["x"]
                <= position[0]
                < room_position["x"] + room_size["width"]
            ) and (
                room_position["y"]
                <= position[1]
                < room_position["y"] + room_size["height"]
            ):
                return True
        return False

    def print_scene(self):
        print(
            f"Aiden's Position: {self.aiden_position}, Orientation: {self.aiden_orientation}"
        )
        current_room = self.find_room_by_position(self.aiden_position)
        current_object = self.find_object_by_position(self.aiden_position)
        if current_object:
            senses = current_object.get("senses", {})
            print(f"Now at: {current_object['name']}")
        else:
            room = self.find_room_by_position(self.aiden_position)
            senses = room.get("senses", {}) if room else {}
            print(f"Now in: {room['name']}" if room else "Aiden is outside any room")

        # Prepare to display the grid
        max_x = max(
            room["position"]["x"] + room["size"]["width"]
            for room in self.rooms.values()
        )
        max_y = max(
            room["position"]["y"] + room["size"]["height"]
            for room in self.rooms.values()
        )

        # Display grid with Aiden's position and orientation
        for y in range(max_y):
            for x in range(max_x):
                if (x, y) == self.aiden_position:
                    # Display Aiden with an arrow indicating his orientation
                    orientation_char = {"N": "^", "E": ">", "S": "v", "W": "<"}[
                        self.aiden_orientation
                    ]
                    print(f"{orientation_char} ", end="")
                else:
                    # Determine if the position is within any room
                    room = self.find_room_by_position((x, y))
                    if room:
                        # Check if the position has an object
                        if any(
                            obj["position"]["x"] == x and obj["position"]["y"] == y
                            for obj in room.get("objects", [])
                        ):
                            print("O ", end="")
                        elif any(
                            obj["position"]["x"] == x and obj["position"]["y"] == y
                            for obj in room.get("doors", [])
                        ):
                            print("D ", end="")
                        else:
                            print(". ", end="")
                    else:
                        # Display hash for barriers or outside the room boundaries
                        print("# ", end="")
            print()  # New line after each row

        # Sensory feedback based on Aiden's position
        if current_object:
            senses = current_object.get("senses", {})
            print(f"Now at: {current_object['name']}")
        else:
            senses = current_room.get("senses", {}) if current_room else {}
            print(
                f"Now in: {current_room['name']}"
                if current_room
                else "Aiden is outside any room"
            )

        print(f"Vision: {senses.get('vision', 'nothing')}")
        print(f"Sound: {senses.get('sound', 'nothing')}")
        print(f"Smell: {senses.get('smell', 'nothing')}")
        print(f"Taste: {senses.get('taste', 'nothing')}")
        print(f"Tactile: {senses.get('tactile', 'nothing')}")
        print()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the AIden simulation with a specific scene configuration."
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
        help="Display the grid and AIden's position after each command.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed actions of AIden's experience.",
    )
    args = parser.parse_args()
    return args


def main(scene_file: str, show_position: bool, verbose: bool) -> None:
    env = Scene(scene_file)
    print("Initial scene:")
    if show_position:
        env.print_scene()

    while True:
        command = input("Enter command (w, a, s, d, q to quit): ").strip().lower()
        if command == "q":
            break
        elif command in ["w", "a", "s", "d"]:
            env.move_aiden(command)
            if verbose:
                print(f"Action executed: {env.directions[command]}")
                print(f"AIden orientation: {env.aiden_orientation}")
                current_room = env.find_room_by_position(env.aiden_position)
                if current_room:
                    senses = current_room.get("senses", {})
                    print(
                        f"AIden senses: Vision: {senses.get('vision', 'nothing')}, Sound: {senses.get('sound', 'nothing')}, Smell: {senses.get('smell', 'nothing')}"
                    )
            if show_position:
                env.print_scene()
        else:
            print("Unknown command!")


if __name__ == "__main__":
    args = parse_arguments()
    main(args.scene, args.show_position, args.verbose)

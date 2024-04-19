"""
CLI to interact with the Brain API for testing purposes,
without needing to evaluate it through the Unity simulation.

This script simulates a virtual character named AIden navigating through a grid representing an apartment and a garden.
Each grid square is 1 meter by 1 meter, and different objects in the scene can emit sounds, have distinct smells,
tastes, and provide tactile feedback.

Commands:
- w: Move forward
- s: Move backward (turn 180 degrees then move forward)
- a: Turn left
- d: Turn right
- q: Quit simulation

Flags:
- --scene: Path to configuration file defining scene to use.
- --show-position: If present, displays the grid and AIden's position after each command.
- --verbose: If present, prints detailed actions of AIden's movements.

Example Usage:
python aiden_simulation.py --verbose --show-position
"""

import argparse
import json
import os
import sys

class Scene:
    def __init__(self, scene_file: str):
        print(scene_file)
        if not os.path.exists(scene_file):
            raise FileNotFoundError("Cannot find the scene configuration file")
        with open(scene_file, 'r') as f:
            config = json.load(f)
        self.grid = {eval(k): v for k, v in config['grid'].items()}
        self.directions = {'w': 'forward', 's': 'backward', 'a': 'left', 'd': 'right'}
        self.aiden_position = (0, 0)
        self.aiden_orientation = 'N'  # 'N', 'E', 'S', 'W'
        self.size = (3, 3)  # Grid size

    def move_aiden(self, command: str) -> None:
        x, y = self.aiden_position
        if command == 'w':
            self.advance(x, y)
        elif command == 's':
            self.turn_around()
            self.advance(x, y)
        elif command == 'a':
            self.turn_left()
        elif command == 'd':
            self.turn_right()

    def turn_around(self):
        self.aiden_orientation = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[self.aiden_orientation]

    def turn_left(self):
        self.aiden_orientation = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}[self.aiden_orientation]

    def turn_right(self):
        self.aiden_orientation = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}[self.aiden_orientation]

    def advance(self, x, y):
        if self.aiden_orientation == 'N' and y > 0:
            self.aiden_position = (x, y - 1)
        elif self.aiden_orientation == 'E' and x < self.size[0] - 1:
            self.aiden_position = (x + 1, y)
        elif self.aiden_orientation == 'S' and y < self.size[1] - 1:
            self.aiden_position = (x, y + 1)
        elif self.aiden_orientation == 'W' and x > 0:
            self.aiden_position = (x - 1, y)

    def print_scene(self):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                obj = self.grid.get((j, i), {}).get('name', 'Empty')
                pos = f"AIden({self.aiden_orientation})>" if (j, i) == self.aiden_position else "         "
                print(f"[{pos}{obj[:6]}]", end='')
            print()  # New line after each row

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the AIden simulation with a specific scene configuration.")
    parser.add_argument('--scene', type=str, default='./config/scenes/default.json', help='Path to the scene configuration file.')
    parser.add_argument('--show-position', action='store_true', help='Display the grid and AIden\'s position after each command.')
    parser.add_argument('--verbose', action='store_true', help='Print detailed actions of AIden\'s experience.')
    args = parser.parse_args()
    return args

def main(scene_file: str = True, show_position: bool = True, verbose: bool = True) -> None:
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
                current_cell = env.grid.get(env.aiden_position, {})
                print(f"AIden senses: Vision: {current_cell.get('name', 'nothing')}, Sound: {current_cell.get('sound', 'nothing')}, Smell: {current_cell.get('smell', 'nothing')}")
            if show_position:
                env.print_scene()
        else:
            print("Unknown command!")

if __name__ == "__main__":
    args = parse_arguments()
    main(args.scene, args.show_position, args.verbose)

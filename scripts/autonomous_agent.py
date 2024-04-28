"""
This script operates as the main driver for the AIden autonomous agent simulation via the CLI,
interfacing with a virtual environment to process and respond to sensory data in real-time.
It supports interaction through a specified API, continuously updating based on inputs
from the virtual scene and responses from the brain API.

The simulation can be configured through command-line arguments to specify the scene
configuration, enable detailed logging to both terminal and files, and adjust log levels
for different outputs. It leverages asyncio for asynchronous operations, ensuring the
simulation runs smoothly and responsively.

Features:
- Dynamic scene rendering and sensory data processing.
- Interaction with brain API to fetch and execute AI-generated actions.
- Configurable logging setup to track and record simulation activities in detail.

Usage:
    python main.py --scene [path] --log --terminal-level [level] --file-level [level]
    --scene: Specify the path to the scene configuration file.
    --log: Enable logging to file.
    --terminal-level: Set the logging level for terminal output (default: DEBUG).
    --file-level: Set the logging level for file output (default: INFO).

The logging outputs are stored in the 'Logs/autonomous_agent_cli' directory, with each session
timestamped to facilitate easy tracking and review of past activities.
"""

import argparse
import asyncio
import datetime
import json
import logging
import os

import httpx
from aiden.app.scene import Scene, load_scene
from aiden.models.brain import CorticalRequest


def setup_logging(log_to_file: bool, terminal_level: str, file_level: str):
    log_directory = "./Logs/autonomous_agent_cli"
    os.makedirs(log_directory, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_directory, f"{timestamp}.log")

    # Create logger
    logger = logging.getLogger("aiden")
    logger.setLevel(
        logging.DEBUG
    )  # Set to DEBUG to allow all levels through to handlers

    # Create handlers with specified log levels
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(getattr(logging, terminal_level.upper(), "INFO"))
    stream_formatter = logging.Formatter("%(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    if log_to_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, file_level.upper(), "INFO"))
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


async def autonomous_agent_simulation(
    brain_config_file: str, scene: Scene, logger: logging.Logger
):
    api_url = f'{os.environ.get("BRAIN_PROTOCOL", "http")}://{os.environ.get("BRAIN_API_HOST", "localhost")}:{os.environ.get("BRAIN_API_PORT", "8000")}/cortical/'

    async with httpx.AsyncClient() as client:
        chat_history = []
        while True:  # Loop indefinitely to keep processing sensory data and actions
            logger.debug("Refreshing scene display...")
            print("\033c", end="")
            scene.print_scene(False)
            sensory_data = scene.update_sensory_data()
            logger.info(f"Sensory data: {sensory_data}")

            payload = CorticalRequest(
                config=brain_config_file, sensory=sensory_data
            ).model_dump()
            response = await client.post(
                api_url, json=payload
            )  # Send sensory data to brain API
            content = ""
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line:
                        json_line = json.loads(line)
                        content += json_line.get("message", {}).get("content", "")
                action = process_response(content, logger)
                if action:
                    scene.process_action(
                        action
                    )  # Process the action derived from response
            else:
                logger.error(f"Error: {response.status_code}")

            logger.debug("Chat history:")
            for instance in chat_history[-5:]:
                logger.debug(instance)
            chat_history.append(content)

            await asyncio.sleep(1)  # Sleep to simulate time passing between actions


def process_response(content: str, logger: logging.Logger) -> str | None:
    """Process the response from AI and extract thoughts, speech, and actions."""
    found_thoughts = False
    found_speech = False
    found_action = False

    if "<thoughts>" in content:
        start = content.find("<thoughts>") + 10
        end = content.find("</thoughts>")
        thoughts = content[start:end].strip()
        found_thoughts = True
        logger.info(f"Thoughts: {thoughts}")

    if "<speech>" in content:
        start = content.find("<speech>") + 8
        end = content.find("</speech>")
        speech = content[start:end].strip()
        found_speech = True
        logger.info(f"Speech: {speech}")

    if "<action>" in content:
        start = content.find("<action>") + 8
        end = content.find("</action>")
        action = content[start:end].strip()
        found_action = True
        logger.info(f"Action to perform: {action}")

    # If none of these explicitly found, assume they are thoughts
    if not found_thoughts and not found_speech and not found_action:
        logger.info(f"Thoughts: {content}")

    if found_action:
        return action

    return None  # No action to process


async def main():
    parser = argparse.ArgumentParser(description="Run the AIden simulation.")
    parser.add_argument(
        "--config",
        type=str,
        default="./config/brain/default.json",
        help="Path to the brain configuration file.",
    )
    parser.add_argument(
        "--scene",
        type=str,
        default="./config/scenes/default.json",
        help="Path to the scene configuration file.",
    )
    parser.add_argument("--log", action="store_true", help="Enable logging to a file.")
    parser.add_argument(
        "--terminal-level",
        type=str,
        default="DEBUG",
        help="Set log level for terminal output.",
    )
    parser.add_argument(
        "--file-level", type=str, default="INFO", help="Set log level for file output."
    )
    args = parser.parse_args()

    logger = setup_logging(args.log, args.terminal_level, args.file_level)
    scene_config = load_scene(args.scene)
    scene = Scene(scene_config)
    await autonomous_agent_simulation(args.config, scene, logger)


if __name__ == "__main__":
    asyncio.run(main())

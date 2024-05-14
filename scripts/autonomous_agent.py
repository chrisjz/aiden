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
from aiden.app.utils import build_sensory_input_prompt_template
from aiden.models.brain import CorticalRequest
from aiden.models.chat import Message


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
    brain_config_file: str,
    scene: Scene,
    logger: logging.Logger,
    enable_speech: bool = False,
    pretty: bool = False,
):
    api_url = f'{os.environ.get("BRAIN_PROTOCOL", "http")}://{os.environ.get("BRAIN_API_HOST", "localhost")}:{os.environ.get("BRAIN_API_PORT", "8000")}/cortical/'

    async with httpx.AsyncClient() as client:
        chat_history = []
        first_loop = True
        while True:  # Loop indefinitely to keep processing sensory data and actions
            # User speech input
            speech_input_formatted = None
            if enable_speech and not first_loop:
                speech_input = input("Your input: ")
                if speech_input:
                    speech_input_formatted = (
                        f'In your earpiece you hear someone nearby say "{speech_input}"'
                    )

            first_loop = False

            logger.debug("Refreshing scene display...")
            print("\033c", end="")

            scene.print_scene(pretty=pretty)
            sensory_data = scene.update_sensory_data()

            # Append user speech
            if speech_input_formatted:
                sensory_data.auditory = ". ".join(
                    filter(None, [sensory_data.auditory, speech_input_formatted])
                )
                logger.info(f"Auditory (amended): {sensory_data.auditory}\n")
                await asyncio.sleep(1)

            history = [
                hist for hist in chat_history
            ]  # TODO: Configure history length for short-term memory

            payload = CorticalRequest(
                config=brain_config_file,
                sensory=sensory_data,
                history=history,
            ).model_dump()
            response = await client.post(
                api_url, json=payload, timeout=60.0
            )  # Send sensory data to brain API
            content = ""
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line:
                        json_line = json.loads(line)
                        content += json_line.get("message", {}).get("content", "")
                logger.debug(f"Response: {content}")
                thoughts, _, action = process_response(content, logger)
                if action:
                    scene.process_action(action)
            else:
                logger.error(f"Error: {response.status_code}")

            user_prompt_template = build_sensory_input_prompt_template(sensory_data)

            # Flush short-term memory when AI start repeating the same response.
            # TODO: Revisit this rule once AI performance improves.
            # TODO: Also append speech to content once we introduce it.
            if chat_history and thoughts == chat_history[-1].content:
                chat_history = []
            else:
                chat_history.append(Message(role="user", content=user_prompt_template))
                chat_history.append(Message(role="assistant", content=thoughts))

            logger.debug("Chat history:")
            for instance in chat_history[-10:]:
                logger.debug(instance)

            await asyncio.sleep(1)  # Sleep to simulate time passing between actions


def process_response(content: str, logger: logging.Logger) -> tuple[str, str, str]:
    """Process the response from AI and extract thoughts, speech, and actions."""
    thoughts = False
    speech = False
    action = False

    if "<thoughts>" in content:
        start = content.find("<thoughts>") + 10
        end = content.find("</thoughts>")
        thoughts = content[start:end].strip()
        logger.info(f"Thoughts:\n{thoughts}\n")

    if "<speech>" in content:
        start = content.find("<speech>") + 8
        end = content.find("</speech>")
        speech = content[start:end].strip()
        logger.info(f"\nSpeech:\n{speech}\n")

    if "<action>" in content:
        start = content.find("<action>") + 8
        end = content.find("</action>")
        action = content[start:end].strip()
        logger.info(f"\nAction to perform:\n{action}\n")

    # If none of these explicitly found, assume they are thoughts
    if not thoughts and not speech and not action:
        logger.warning("No valid response obtained from Brain API.")

    return thoughts, speech, action


async def main():
    parser = argparse.ArgumentParser(description="Run the AIden simulation.")
    parser.add_argument(
        "--config",
        dest="config_path",
        type=str,
        default="./config/brain/default.json",
        help="Path to the brain configuration file.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Enable emoji representations of grid components.",
    )
    parser.add_argument(
        "--scene",
        dest="scene_path",
        type=str,
        default="./config/scenes/default.json",
        help="Path to the scene configuration file.",
    )
    parser.add_argument(
        "--speech",
        dest="enable_speech",
        action="store_true",
        help="Enable speech input.",
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
    scene_config = load_scene(args.scene_path)
    scene = Scene(scene_config)
    await autonomous_agent_simulation(
        args.config_path, scene, logger, args.enable_speech, args.pretty
    )


if __name__ == "__main__":
    asyncio.run(main())

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden import logger
from aiden.app.brain.memory.hippocampus import MemoryManager
from aiden.app.brain.cognition.broca import process_broca
from aiden.app.brain.cognition.prefrontal import process_prefrontal
from aiden.app.brain.cognition.subconscious import process_subconscious
from aiden.app.brain.cognition.thalamus import process_thalamus
from aiden.app.clients.redis_client import redis_client
from aiden.app.utils import (
    build_sensory_input_prompt_template,
    load_brain_config,
)
from aiden.models.brain import SimpleAction


async def process_cortical(request) -> str:
    """
    Processes a cortical request to determine the AI's actions and thoughts based on sensory input.

    Args:
        request (CorticalRequest): The request containing sensory data and configuration.

    Returns:
        Generator: A generator yielding the AI's responses as a stream.
    """
    brain_config = load_brain_config(request.config)
    cortical_config = brain_config.regions.cortical
    personality = cortical_config.personality

    # Check if agent_id is provided in request or default to the catch-all zero ID
    agent_id = getattr(request, "agent_id", "0")

    # Prepare the system prompt
    system_input = cortical_config.about + "\n"
    if brain_config.settings.feature_toggles.personality:
        system_input += f"Personality Profile:\n- Traits: {', '.join(personality.traits)}\n- Preferences: {', '.join(personality.preferences)}\n- Boundaries: {', '.join(personality.boundaries)}\n\n"
    system_input += "\n".join(cortical_config.description)

    # Prepare the user prompt based on available sensory data
    raw_sensory_input = build_sensory_input_prompt_template(request.sensory)
    logger.info(f"Raw sensory: {raw_sensory_input}")

    # Sensory integration through thalamus function
    sensory_input = await process_thalamus(raw_sensory_input, brain_config)

    # Decision-making through prefrontal function
    action_output = await process_prefrontal(sensory_input, brain_config)

    # Verbal output through broca function
    speech_output = await process_broca(sensory_input, brain_config)

    # Format final thoughts prompt
    final_thoughts_input = (
        f"\n{cortical_config.instruction}\nYour sensory data: {sensory_input}"
    )
    if action_output != SimpleAction.NONE.value:
        action_output_formatted = action_output.replace("_", " ")
        final_thoughts_input += (
            f"\nYou decide to perform the action: {action_output_formatted}."
        )

    # Retrieve short-term memory
    memory_manager = MemoryManager(redis_client=redis_client)
    history = memory_manager.read_memory(agent_id)

    logger.info(f"History from redis: {history}")

    # # Perform memory consolidation
    memory_manager.consolidate_memory(agent_id)

    # Prepare the chat message for the Cognitive API
    messages = [SystemMessage(content=system_input)]
    if history:
        messages.extend(history)

    messages.append(HumanMessage(content=final_thoughts_input))

    # Thoughts output through subconcious function
    thoughts_output = await process_subconscious(messages)

    # Combine action, thoughts, and speech into one message
    combined_message_content = ""
    if action_output != SimpleAction.NONE.value:
        combined_message_content += f"<action>{action_output}</action>\n"
    combined_message_content += f"<thoughts>{thoughts_output}</thoughts>\n"
    if speech_output:
        combined_message_content += f"<speech>{speech_output}</speech>\n"

    # Append formatted combined message to messages
    combined_message_content_formatted = f"My thoughts:\n{thoughts_output}"
    combined_message_content_formatted += (
        f"\nMy speech:\n{speech_output}" if speech_output else ""
    )
    combined_message_content_formatted += (
        f"\nMy actions performed: {action_output}"
        if action_output != SimpleAction.NONE
        else ""
    )
    messages.append(AIMessage(content=combined_message_content_formatted))

    # TODO: Stream all of these separately
    async def stream_response():
        # Stream the combined message
        yield json.dumps({"message": {"content": combined_message_content}}) + "\n"

        # Store the updated history in Redis
        memory_manager.update_memory(agent_id, messages)

    return stream_response()

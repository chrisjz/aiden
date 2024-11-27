from typing import AsyncGenerator, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState

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
from aiden.models.brain import (
    Action,
    AuditoryType,
    BrainConfig,
    CorticalRequest,
    CorticalResponse,
    TactileInput,
    TactileType,
)


class CorticalState(MessagesState):
    action_choices: list[Action]
    action_chosen: str | None
    brain_config: BrainConfig
    language_input: str
    sensory_input: str


async def _extract_actions_from_tactile_inputs(
    tactile_inputs: list[TactileInput],
) -> list[Action]:
    """
    Filters and extracts actions from a list of tactile inputs, returning a list of Action objects.

    Args:
        tactile_inputs (list[TactileInput]): A list of tactile inputs where some might be of type ACTION.

    Returns:
        list[Action]: A list of Action objects filtered from the tactile inputs of type ACTION.
    """
    return [
        input.command
        for input in tactile_inputs
        if input.type == TactileType.ACTION and input.command is not None
    ]


async def process_cortical_new(request: CorticalRequest) -> AsyncGenerator:
    """
    Simulates the cortical region (cerebral cortex) by processing sensory inputs to determine
    the AI's actions and thoughts.

    Args:
        request (CorticalRequest): The request containing sensory data and configuration.

    Returns:
        Generator: A generator yielding the AI's responses as a stream.
    """
    brain_config = load_brain_config(request.config)
    cortical_config = brain_config.regions.cortical
    personality = cortical_config.personality

    # Prepare the system prompt
    system_input = cortical_config.about + "\n"
    if brain_config.settings.feature_toggles.personality:
        system_input += f"Personality Profile:\n- Traits: {', '.join(personality.traits)}\n- Preferences: {', '.join(personality.preferences)}\n- Boundaries: {', '.join(personality.boundaries)}\n\n"
    system_input += "\n".join(cortical_config.description)

    # Prepare the user prompt based on available sensory data
    raw_sensory_input = build_sensory_input_prompt_template(request.sensory)
    logger.info(f"Raw sensory: {raw_sensory_input}")
    print(f"Raw sensory: {raw_sensory_input}")

    # Prepare graph
    graph_builder = StateGraph(CorticalState)

    async def call_thalamus(state: CorticalState) -> dict[str, list]:
        response = await process_thalamus(
            sensory_input=state["sensory_input"], brain_config=state["brain_config"]
        )
        return {"messages": [response]}

    async def call_prefrontal(state: CorticalState) -> dict[str, list]:
        sensory_input = state["messages"][-1].content
        response = await process_prefrontal(
            sensory_input=sensory_input,
            brain_config=state["brain_config"],
            actions=state["action_choices"],
        )
        state["action_chosen"] = response
        return state

    async def has_actions(state: CorticalState) -> Literal["end", "continue"]:
        actions = state["action_choices"]

        if actions:
            return "continue"

        return "end"

    # Add nodes
    graph_builder.add_node("thalamus", call_thalamus)
    graph_builder.add_node("prefrontal", call_prefrontal)

    # Add edges
    graph_builder.add_edge(START, "thalamus")
    graph_builder.add_conditional_edges(
        "thalamus",
        has_actions,
        {
            "continue": "prefrontal",
            "end": END,
        },
    )

    # Compile graph
    graph = graph_builder.compile()

    # Prepare lists of actions available from tactile sensory input
    actions = await _extract_actions_from_tactile_inputs(request.sensory.tactile)
    logger.info(f"Action commands available: {actions}")

    # Set initial cortical state
    state = CorticalState(
        brain_config=brain_config,
        sensory_input=raw_sensory_input,
        action_choices=actions,
        action_chosen=None,
    )

    # Execute graph
    response = await graph.ainvoke(state)

    # Set cortical outputs
    action_output = response["action_chosen"]
    speech_output = None
    thoughts_output = response["messages"][-1].content

    # Prepare response
    response = CorticalResponse(
        action=action_output,
        speech=speech_output,
        thoughts=thoughts_output,
    )
    logger.info(f"Cortical response: {response}")

    return response


async def process_cortical(request: CorticalRequest) -> AsyncGenerator:
    """
    Simulates the cortical region (cerebral cortex) by processing sensory inputs to determine
    the AI's actions and thoughts.

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

    # Prepare lists of actions available from tactile sensory input
    actions = await _extract_actions_from_tactile_inputs(request.sensory.tactile)
    logger.info(f"Action commands available: {actions}")

    # Decision-making through prefrontal function
    action_output = await process_prefrontal(sensory_input, brain_config, actions)

    # Check if there is language input in sensory_input
    language_input = None
    for auditory_input in request.sensory.auditory:
        if auditory_input.type == AuditoryType.LANGUAGE and auditory_input.content:
            language_input = auditory_input.content
            logger.info(f"Language input: {language_input}")
            break  # Assuming we only need the first relevant language input

    # Verbal output through broca function, only if language input is present
    speech_output = None
    if language_input:
        speech_output = await process_broca(
            sensory_input=sensory_input,
            brain_config=brain_config,
            language_input=language_input,
        )

    # Format final thoughts prompt
    final_thoughts_input = (
        f"\n{cortical_config.instruction}\nYour sensory data: {sensory_input}"
    )
    if action_output:
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
    if action_output:
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
        f"\nMy actions performed: {action_output}" if action_output else ""
    )
    messages.append(AIMessage(content=combined_message_content_formatted))

    # Prepare response
    response = CorticalResponse(
        action=action_output,
        speech=speech_output,
        thoughts=thoughts_output,
    )

    logger.info(f"Cortical response: {response}")

    # TODO: Stream all of these separately
    async def stream_response():
        # Stream the combined message
        yield response.model_dump_json()

        # Store the updated history in Redis
        memory_manager.update_memory(agent_id, messages)

    return stream_response()

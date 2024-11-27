import operator
from typing import Annotated, AsyncGenerator, Literal

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
    AuditoryInput,
    AuditoryType,
    BrainConfig,
    CorticalRequest,
    CorticalResponse,
    Sensory,
    TactileInput,
    TactileType,
)


class CorticalState(MessagesState):
    action: str | None
    agent_id: str
    aggregate: Annotated[list, operator.add]
    brain_config: BrainConfig
    sensory: Sensory
    speech: str | None


def _add_cortical_output_to_memory(state: CorticalState):
    """
    Updates agent memory with consolidated cortical response.

    Args:
        state CorticalState: The cortical state.
    """
    agent_id = state["agent_id"]
    messages = state["messages"]

    action_output = state["action"]
    speech_output = state["speech"]
    thoughts_output = messages[-1].content

    # Append formatted combined message to messages
    combined_message_content_formatted = f"My thoughts:\n{thoughts_output}"
    combined_message_content_formatted += (
        f"\nMy speech:\n{speech_output}" if speech_output else ""
    )
    combined_message_content_formatted += (
        f"\nMy actions performed: {action_output}" if action_output else ""
    )

    # Store the updated history in Redis
    messages.append(AIMessage(content=combined_message_content_formatted))
    memory_manager = MemoryManager(redis_client=redis_client)
    memory_manager.update_memory(agent_id, messages)


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


async def _has_actions_in_tactile_inputs(
    tactile_inputs: list[TactileInput],
) -> bool:
    """
    Checks if there are any actions in a list of tactile inputs.

    Args:
        tactile_inputs (list[TactileInput]): A list of tactile inputs where some might be of type ACTION.

    Returns:
        bool: True if there are any tactile inputs of type ACTION with a valid command, otherwise False.
    """
    return any(
        input.type == TactileType.ACTION and input.command is not None
        for input in tactile_inputs
    )


def _has_speech_in_auditory_inputs(auditory_inputs: list[AuditoryInput]) -> bool:
    """
    Checks if there is any speech (LANGUAGE type) content in the list of auditory inputs.

    Args:
        auditory_inputs (list[AuditoryInput]): A list of auditory inputs to check.

    Returns:
        bool: True if any auditory input of type LANGUAGE contains non-empty content, otherwise False.
    """
    return any(
        auditory_input.type == AuditoryType.LANGUAGE and bool(auditory_input.content)
        for auditory_input in auditory_inputs
    )


async def process_cortical(request: CorticalRequest) -> AsyncGenerator:
    """
    Simulates the cortical region (cerebral cortex) by processing sensory inputs to determine
    the AI's actions and thoughts.

    Args:
        request (CorticalRequest): The request containing sensory data and configuration.

    Returns:
        Generator: A generator yielding the AI's responses as a stream.
    """
    # Prepare graph
    graph_builder = StateGraph(CorticalState)

    async def call_thalamus(state: CorticalState) -> dict[str, list]:
        # Prepare the user prompt based on available sensory data
        raw_sensory_input = build_sensory_input_prompt_template(state["sensory"])
        logger.info(f"Raw sensory: {raw_sensory_input}")

        response = await process_thalamus(
            sensory_input=raw_sensory_input, brain_config=state["brain_config"]
        )
        return {"messages": [response]}

    async def call_prefrontal(state: CorticalState) -> dict[str, list]:
        sensory = state["sensory"]
        sensory_input = state["messages"][-1].content

        # Prepare lists of actions available from tactile sensory input
        actions = await _extract_actions_from_tactile_inputs(sensory.tactile)
        logger.info(f"Action commands available: {actions}")

        response = await process_prefrontal(
            sensory_input=sensory_input,
            brain_config=state["brain_config"],
            actions=actions,
        )

        return {"aggregate": [{"action": response}]}

    async def call_broca(state: CorticalState) -> dict[str, list]:
        sensory_input = state["messages"][-1].content

        # Get language input in sensory_input
        language_input = None
        for auditory_input in request.sensory.auditory:
            if auditory_input.type == AuditoryType.LANGUAGE and auditory_input.content:
                language_input = auditory_input.content
                logger.info(f"Language input: {language_input}")
                break  # Assuming we only need the first relevant language input

        response = await process_broca(
            sensory_input=sensory_input,
            brain_config=state["brain_config"],
            language_input=language_input,
        )

        return {"aggregate": [{"speech": response}]}

    async def call_subconscious(state: CorticalState) -> dict[str, list]:
        sensory_input = state["messages"][-1].content
        agent_id = state["agent_id"]
        brain_config = state["brain_config"]
        cortical_config = brain_config.regions.cortical
        personality = cortical_config.personality

        # Aggregate action and speech outputs if set
        action_output = None
        for aggr in state["aggregate"]:
            if "action" in aggr:
                action_output = aggr["action"]
                state["action"] = action_output
            if "speech" in aggr:
                state["speech"] = aggr["speech"]

        # Prepare the system prompt
        system_input = cortical_config.about + "\n"
        if brain_config.settings.feature_toggles.personality:
            system_input += f"Personality Profile:\n- Traits: {', '.join(personality.traits)}\n- Preferences: {', '.join(personality.preferences)}\n- Boundaries: {', '.join(personality.boundaries)}\n\n"
        system_input += "\n".join(cortical_config.description)

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

        # Perform memory consolidation
        memory_manager.consolidate_memory(agent_id)

        # Prepare the chat message for the Cognitive API
        messages = [SystemMessage(content=system_input)]
        if history:
            messages.extend(history)

        messages.append(HumanMessage(content=final_thoughts_input))

        # Thoughts output through subconcious function
        thoughts_output = await process_subconscious(messages)

        state["messages"] = [thoughts_output]

        return state

    async def has_actions(
        state: CorticalState,
    ) -> Literal["run_prefrontal", "run_subconscious"]:
        sensory = state["sensory"]

        if await _has_actions_in_tactile_inputs(sensory.tactile):
            return "run_prefrontal"

        return "run_subconscious"

    async def has_speech(
        state: CorticalState,
    ) -> Literal["run_broca", "run_subconscious"]:
        sensory = state["sensory"]

        if _has_speech_in_auditory_inputs(sensory.auditory):
            return "run_broca"

        return "run_subconscious"

    # Add nodes
    graph_builder.add_node("thalamus", call_thalamus)
    graph_builder.add_node("prefrontal", call_prefrontal)
    graph_builder.add_node("broca", call_broca)
    graph_builder.add_node("subconscious", call_subconscious)

    # Add edges
    graph_builder.add_edge(START, "thalamus")
    graph_builder.add_edge("prefrontal", "subconscious")
    graph_builder.add_edge("broca", "subconscious")
    graph_builder.add_conditional_edges(
        "thalamus",
        has_actions,
        {
            "run_prefrontal": "prefrontal",
            "run_subconscious": "subconscious",
        },
    )
    graph_builder.add_conditional_edges(
        "thalamus",
        has_speech,
        {
            "run_broca": "broca",
            "run_subconscious": "subconscious",
        },
    )
    graph_builder.add_edge("subconscious", END)

    # Compile graph
    graph = graph_builder.compile()

    # Get agent ID
    agent_id = getattr(request, "agent_id", "0")

    # Set initial cortical state
    state = CorticalState(
        # Check if agent_id is provided in request or default to the catch-all zero ID
        agent_id=agent_id,
        brain_config=load_brain_config(request.config),
        sensory=request.sensory,
        action=None,
        speech=None,
    )

    # Execute graph
    response = await graph.ainvoke(state)

    # Combine action, thoughts, and speech into one message to save in agent's memory
    _add_cortical_output_to_memory(response)

    # Set cortical outputs
    action_output = response["action"]
    speech_output = response["speech"]
    thoughts_output = response["messages"][-1].content

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

    return stream_response()

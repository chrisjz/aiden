import json
import pytest

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from aiden.app.brain import cortical
from aiden.app.brain.cognition import broca, prefrontal, subconscious, thalamus
from aiden.app.brain.cortical import process_cortical
from aiden.app.brain.memory.hippocampus import MemoryManager
from aiden.models.brain import (
    Action,
    AuditoryInput,
    AuditoryType,
    CorticalRequest,
    GustatoryInput,
    OlfactoryInput,
    Sensory,
    TactileInput,
    TactileType,
    VisionInput,
)


@pytest.mark.asyncio
async def test_cortical_success(monkeypatch, redis_client, cognitive_api):
    # Given
    agent_id = "test"
    brain_config = "./config/brain/default.json"

    sensory_data = Sensory(
        vision=[VisionInput(content="I see a tree and a car.")],
        auditory=[
            AuditoryInput(type=AuditoryType.LANGUAGE, content="How are you today?"),
            AuditoryInput(content="I hear a bird chirping."),
        ],
        tactile=[
            TactileInput(type=TactileType.ACTION, command=Action(name="move forward")),
            TactileInput(type=TactileType.ACTION, command=Action(name="move backward")),
            TactileInput(type=TactileType.ACTION, command=Action(name="turn left")),
            TactileInput(type=TactileType.ACTION, command=Action(name="turn right")),
            TactileInput(content="I feel the gentle breeze of the wind."),
        ],
        olfactory=[
            OlfactoryInput(content="I smell the sweet scent of flowers blooming.")
        ],
        gustatory=[
            GustatoryInput(content="I taste the minty flavour of the gum I'm chewing.")
        ],
    )

    request = CorticalRequest(
        agent_id=agent_id, config=brain_config, sensory=sensory_data
    )

    memory_manager = MemoryManager(redis_client=redis_client)

    monkeypatch.setattr(cortical, "redis_client", redis_client)
    monkeypatch.setattr(broca, "COGNITIVE_API_URL_BASE", cognitive_api)
    monkeypatch.setattr(prefrontal, "COGNITIVE_API_URL_BASE", cognitive_api)
    monkeypatch.setattr(subconscious, "COGNITIVE_API_URL_BASE", cognitive_api)
    monkeypatch.setattr(thalamus, "COGNITIVE_API_URL_BASE", cognitive_api)

    # When
    response_generator = await process_cortical(request)

    response_chunks = []
    async for chunk in response_generator:
        response_chunks.append(chunk)

    response = json.loads("".join(response_chunks))

    memory = memory_manager.read_memory(agent_id=agent_id)

    # Then
    assert response["thoughts"] is not None
    assert "action" in response
    assert "speech" in response

    assert len(memory) == 3
    assert isinstance(memory[0], SystemMessage)
    assert memory[0].content is not None
    assert isinstance(memory[1], HumanMessage)
    assert memory[1].content is not None
    assert isinstance(memory[2], AIMessage)
    assert memory[2].content is not None

    # When
    response_generator = await process_cortical(request)

    response_chunks = []
    async for chunk in response_generator:
        response_chunks.append(chunk)

    response = json.loads("".join(response_chunks))

    memory = memory_manager.read_memory(agent_id=agent_id)

    # Then
    assert response["thoughts"] is not None
    assert "action" in response
    assert "speech" in response

    assert len(memory) == 5
    assert isinstance(memory[0], SystemMessage)
    assert memory[0].content is not None
    assert isinstance(memory[1], HumanMessage)
    assert memory[1].content is not None
    assert isinstance(memory[2], AIMessage)
    assert memory[2].content is not None
    assert isinstance(memory[3], HumanMessage)
    assert memory[3].content is not None
    assert isinstance(memory[4], AIMessage)
    assert memory[4].content is not None

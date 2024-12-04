import json
import pytest
from aiden.app.brain import cortical
from aiden.app.brain.cognition import broca, prefrontal, subconscious, thalamus
from aiden.app.brain.cortical import process_cortical
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

    # Then
    assert response["thoughts"] is not None
    assert response["action"] is not None
    assert response["speech"] is not None

import json

import pytest
from fastapi.encoders import jsonable_encoder
from langchain_core.load import dumps
from langchain_core.messages import AIMessage, HumanMessage

from aiden.app.brain.memory.hippocampus import MemoryManager


def test_update_memory(redis_client):
    # Given
    memory_manager = MemoryManager(redis_client=redis_client)
    messages = [
        HumanMessage(content="User message 1"),
        AIMessage(content="Assistant message 1"),
    ]

    # When
    memory_manager.update_memory("0", messages)

    # Then
    assert redis_client.get("agent:0:memory") == dumps(messages)


def test_read_memory_has_memory(redis_client):
    # Given
    memory_manager = MemoryManager(redis_client=redis_client)
    messages = [
        HumanMessage(content="User message 1"),
        AIMessage(content="Assistant message 1"),
    ]
    memory_manager.update_memory("0", messages)

    # When
    memory = memory_manager.read_memory("0")

    # Then
    assert memory == messages


def test_read_memory_empty(redis_client):
    # Given
    memory_manager = MemoryManager(redis_client=redis_client)

    # When
    memory = memory_manager.read_memory("0")

    # Then
    assert memory == []


def test_wipe_memory(redis_client):
    # Given
    memory_manager = MemoryManager(redis_client=redis_client)
    messages = [
        HumanMessage(content="User message 1"),
        AIMessage(content="Assistant message 1"),
    ]
    redis_client.set("agent:0:memory", json.dumps(messages, default=jsonable_encoder))
    assert redis_client.get("agent:0:memory") == json.dumps(
        messages, default=jsonable_encoder
    )

    # When
    memory_manager.wipe_memory("0")

    # Then
    assert redis_client.get("agent:0:memory") is None


@pytest.mark.skip("Not implemented")
def test_consolidate_memory(monkeypatch, redis_client):
    # Given
    monkeypatch.setenv("MEMORY_CONSOLIDATION_HISTORY_MIN_CONSOLIDATE", "4")
    monkeypatch.setenv("MEMORY_CONSOLIDATION_HISTORY_KEEP_LATEST", "2")
    memory_manager = MemoryManager(redis_client=redis_client)
    messages = [
        HumanMessage(content="User message 1"),
        AIMessage(content="Assistant message 1"),
        HumanMessage(content="User message 2"),
        AIMessage(content="Assistant message 2"),
        HumanMessage(content="User message 3"),
        AIMessage(content="Assistant message 3"),
        HumanMessage(content="User message 4"),
        AIMessage(content="Assistant message 4"),
        HumanMessage(content="User message 5"),
        AIMessage(content="Assistant message 5"),
    ]
    redis_client.set("agent:0:memory", json.dumps(messages, default=jsonable_encoder))

    # When / then
    # TODO: Update test after final implementation
    with pytest.raises(Exception):
        memory_manager.consolidate_memory("0")

    updated_messages = [
        HumanMessage(content="User message 4"),
        AIMessage(content="Assistant message 4"),
        HumanMessage(content="User message 5"),
        AIMessage(content="Assistant message 5"),
    ]
    memory = memory_manager.read_memory("0")
    assert memory == updated_messages


def test_dont_consolidate_memory(monkeypatch, redis_client):
    # Given
    monkeypatch.setenv("MEMORY_CONSOLIDATION_HISTORY_MIN_CONSOLIDATE", "3")
    memory_manager = MemoryManager(redis_client=redis_client)
    messages = [
        HumanMessage(content="User message 1"),
        AIMessage(content="Assistant message 1"),
    ]
    memory_manager.update_memory("0", messages)

    # When
    memory_manager.consolidate_memory("0")

    # Then
    memory = memory_manager.read_memory("0")
    assert memory == messages
    # TODO: Check consolidated memory not in long-term memory

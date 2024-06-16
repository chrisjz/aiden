import os

from langchain_core.load import dumps, loads
from langchain_core.messages import BaseMessage
from redis import Redis

from aiden import logger

CHROMA_COLLECTION_MEMORY = "memory"


class MemoryManager:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _get_memory_key(self, agent_id: str) -> str:
        """Fixed memory key"""
        key = f"agent:{agent_id}:memory"
        return key

    def update_memory(self, agent_id: str, messages: list[BaseMessage]):
        """
        Save chat history representing short-term memory to Redis.

        Args:
            agent_id (str): Unique identifier for the AI agent.
            messages (List[BaseMessage]): List of Message models to save.
        """
        key = self._get_memory_key(agent_id)
        messages_serialized = dumps(messages)
        self.redis_client.set(key, messages_serialized)
        self.redis_client.expire(key, 86400)  # Expires in 1 day

    def read_memory(self, agent_id: str) -> list[BaseMessage]:
        """
        Retrieve chat history representing short-term memory from Redis.

        Args:
            agent_id (str): Unique identifier for the AI agent.

        Returns:
            List[BaseMessage]: A list of Message models.
        """
        key = self._get_memory_key(agent_id)
        history_json = self.redis_client.get(key)
        if history_json:
            return loads(history_json)
        else:
            return []

    def wipe_memory(self, agent_id: str) -> None:
        """
        Delete the agent's entire short-term memory in Redis

        Args:
            agent_id (str): Unique identifier for the AI agent.
        """
        key = self._get_memory_key(agent_id)
        self.redis_client.delete(key)

    def consolidate_memory(self, agent_id):
        min_history_to_consolidate = int(
            os.environ.get("MEMORY_CONSOLIDATION_HISTORY_MIN_CONSOLIDATE", "20")
        )
        history = self.read_memory(agent_id)

        if len(history) < min_history_to_consolidate * 2:
            return

        logger.info("Perform memory consolidation.")
        keep_newest_memories_num = int(
            os.environ.get("MEMORY_CONSOLIDATION_HISTORY_KEEP_LATEST", "10")
        )

        # TODO: Consolidate oldest memories to long-term memory

        # Update short-term memory by removing the oldest entries
        updated_history = history[-keep_newest_memories_num * 2 :]
        self.update_memory(agent_id, updated_history)

        raise NotImplementedError("Memory consolidation not fully implemented.")

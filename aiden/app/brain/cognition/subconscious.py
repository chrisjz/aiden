import os

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, BaseMessage

from aiden import logger
from aiden.app.brain.cognition import COGNITIVE_API_URL_BASE


async def process_subconscious(messages: list[BaseMessage]) -> str | None:
    """
    Process the thoughts from the subconscious areas of the AI model and return them as a string.

    Args:
        chat_message (list[BaseMessage]): The message to be processed.

    Returns:
        str: The processed thoughts as a string. If processing fails, returns None.
    """
    llm = ChatOllama(
        base_url=COGNITIVE_API_URL_BASE,
        model=os.environ.get("COGNITIVE_MODEL", "mistral"),
        timeout=30.0,
        frequency_penalty=1.2,
        penalize_newline=False,
        presence_penalty=1.7,
        repeat_last_n=48,
        repeat_penalty=1.3,
        temperature=0.9,
        top_k=16,
        top_p=0.9,
    )

    logger.info(f"Subconcious chat message: {messages}")

    response: AIMessage = llm.invoke(messages)
    try:
        content = response.content.strip()
        logger.info(f"Thoughts: {content}")
        return content
    except Exception as exc:
        logger.error(f"Failed thoughts processing with error: {exc}")
        return None
